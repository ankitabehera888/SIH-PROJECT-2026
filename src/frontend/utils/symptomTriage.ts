import {
  FIRST_AID, RED_FLAGS, SECONDARY_QUESTIONS, URGENCY_TIERS, ageBand, firstAidById, tierById,
  type BodyType, type FirstAidGuide, type RedFlag, type UrgencyTier,
} from '../../mock-data/symptomCheckerTriage';
import { symptomById, type Symptom } from '../../mock-data/symptomCheckerSymptoms';
import { regionById } from '../../mock-data/symptomCheckerBody';
import { scT, scAgeBandLabel, scFormatAge } from '../i18n/symptomChecker';
import type { Language } from '../i18n/translations';

/* ---------------------------------------------------------------------------
   Multi-symptom triage engine.
   Design rule taken from the scanned checker: red flags always win, symptom
   patterns only decide the *baseline* level. Everything is computed from the
   whole selection at once, so adding a second or third symptom can only raise
   (never lower) the urgency, and can re-rank the likely conditions.
   Age (in months) further raises risk for under-3-months, infants, young
   children and older adults, and swaps first-aid guides for age variants.
   --------------------------------------------------------------------------- */

export interface SelectedSymptom {
  id: string;
  durationDays: number;
  severity: number;      // 1..10
  flags: string[];       // red-flag ids the user confirmed for this symptom
}

export interface AssessmentInput {
  model: BodyType;
  ageMonths: number;     // patient age in months (0 = under 1 month)
  symptoms: SelectedSymptom[];
  secondary: string[];   // ids from SECONDARY_QUESTIONS
  language?: Language;   // localize engine-built reasons/summary only
}

export interface ConditionMatch {
  name: string;
  icd10: string;
  specialist: string;
  score: number;         // 0..100 “how much of this picture it explains”
  factors: string[];     // which of your symptoms point to it
}

export interface Assessment {
  tier: UrgencyTier;
  reasons: string[];
  redFlags: RedFlag[];
  firstAid: FirstAidGuide[];
  homeCare: string[];
  watchFor: RedFlag[];
  conditions: ConditionMatch[];
  specialist: string | null;
  symptomCount: number;
  regionCount: number;
  maxDuration: number;
  maxSeverity: number;
  ageMonths: number;
  ageLabel: string;
  ageBandLabel: string;
  summary: string;
}

const BASE_LEVEL: Record<string, number> = { self: 10, office: 20, h24: 65 };

/* First-aid guide → age band with min/max filter + optional step rewrite. */
const firstAidForAge = (id: string, months: number): FirstAidGuide | null => {
  const guide = firstAidById(id) ?? FIRST_AID.find((g) => g.id === id);
  if (!guide) return null;
  if (guide.minAgeMonths !== undefined && months < guide.minAgeMonths) return null;
  if (guide.maxAgeMonths !== undefined && months >= guide.maxAgeMonths) return null;
  const band = ageBand(months);
  const variant = guide.ageVariants?.[band];
  if (!variant) return guide;
  return {
    ...guide,
    title: variant.title ?? guide.title,
    steps: variant.steps ?? guide.steps,
  };
};

export const urgencyBand = (level: number): 'emergency' | 'urgent' | 'soon' | 'routine' => {
  if (level >= 95) return 'emergency';
  if (level >= 90) return 'urgent';
  if (level >= 65) return 'soon';
  return 'routine';
};

export function analyzeSymptoms(input: AssessmentInput): Assessment {
  const lang: Language = input.language ?? 'en';
  const L = (source: string, params?: Record<string, string | number>) => scT(lang, source, params);
  const selected = input.symptoms
    .map((s) => ({ ...s, symptom: symptomById(s.id) }))
    .filter((s): s is SelectedSymptom & { symptom: Symptom } => Boolean(s.symptom));

  const reasons: string[] = [];
  let level = 10;
  const raise = (next: number, why: string) => {
    if (next > level) level = next;
    const text = L(why);
    if (text && !reasons.includes(text)) reasons.push(text);
  };

  /* ---- 1. baseline from each symptom pattern ------------------------- */
  let baselineSet = false;
  selected.forEach(({ symptom }) => {
    const l = BASE_LEVEL[symptom.baseTier] ?? 10;
    if (l > level) { level = l; baselineSet = true; }
  });
  if (baselineSet) reasons.push(L('The symptom pattern on its own needs a clinical review, not just home care.'));

  /* ---- 2. confirmed red flags (the “any one of these” rules) --------- */
  const checkedFlagIds = new Set<string>();
  selected.forEach((s) => s.flags.forEach((f) => checkedFlagIds.add(f)));
  SECONDARY_QUESTIONS.forEach((q) => {
    if (input.secondary.includes(q.id)) checkedFlagIds.add(q.redFlag);
  });

  const redFlags = [...checkedFlagIds]
    .map((id) => RED_FLAGS.find((f) => f.id === id))
    .filter((f): f is RedFlag => Boolean(f))
    .sort((a, b) => tierById(b.tier).level - tierById(a.tier).level);

  redFlags.forEach((flag) => {
    const t = tierById(flag.tier);
    if (t.level > level) level = t.level;
  });
  if (redFlags.length) {
    const top = tierById(redFlags[0].tier);
    reasons.unshift(L('{n} warning sign{s} confirmed — the most serious needs: {short}.', {
      n: redFlags.length, s: redFlags.length > 1 ? 's' : '', short: L(top.short),
    }));
  }
  /* ---- 3. modifiers from duration, severity and spread -------------- */
  const maxDuration = selected.reduce((m, s) => Math.max(m, s.durationDays), 0);
  const maxSeverity = selected.reduce((m, s) => Math.max(m, s.severity), 1);
  const regions = new Set(selected.map((s) => s.symptom.region));
  const symptomCount = selected.length;
  const regionCount = regions.size;
  const months = input.ageMonths;
  const band = ageBand(months);

  if (maxDuration >= 14) raise(20, 'Symptoms lasting more than two weeks need a routine review and possibly tests.');
  else if (maxDuration >= 4) raise(20, 'Symptoms lasting more than three days should be reviewed by a clinician.');

  if (maxSeverity >= 9) raise(90, 'Pain or distress rated 9–10 out of 10 needs care today.');
  else if (maxSeverity >= 7) raise(65, 'Symptoms rated 7–8 out of 10 should be seen within 24 hours.');
  else if (maxSeverity >= 4) raise(20, 'Moderate severity should be reviewed during office hours.');

  if (symptomCount >= 4) raise(20, 'Four or more symptoms at once need a clinician to look at the whole picture.');
  if (regionCount >= 3) raise(65, 'Symptoms in three or more body areas together suggest a systemic illness.');
  if (regionCount >= 2 && maxDuration >= 3) raise(65, 'Symptoms in more than one body area lasting several days need a same-day review.');

  /* Age-based raises — age always wins over a low baseline. */
  if (months < 3 && symptomCount > 0) {
    raise(90, 'Any illness in a baby under 3 months is treated as urgent.');
  } else if (months < 12 && symptomCount > 0 && (maxSeverity >= 4 || regions.has('chest') || regions.has('abdomen') || regions.has('general'))) {
    raise(65, 'Babies under 1 year dehydrate quickly — arrange a review within 24 hours.');
  }

  if (band === 'child' && symptomCount > 0) {
    const childSensitive = selected.some(({ symptom }) =>
      symptom.region === 'chest' || symptom.region === 'general' || symptom.id.startsWith('fever') || symptom.id === 'diarrhea' || symptom.id === 'vomiting',
    );
    if (childSensitive && level < 65) raise(65, 'Symptoms that would be routine in an adult need a same-day check in a young child.');
  }

  if (band === 'senior' && symptomCount > 0) {
    const seniorSensitive = selected.some(({ symptom }) =>
      symptom.region === 'general' || symptom.region === 'head' || symptom.region === 'chest' || symptom.id === 'dizziness' || symptom.id === 'tiredness',
    );
    if (seniorSensitive && level < 65) raise(65, 'In an older adult, these symptoms can change quickly — get reviewed within 24 hours.');
  }

  /* Keep the old explicit infant secondary for users who ticked it before age was required. */
  if (input.secondary.includes('infant') && months >= 3 && months < 36) {
    raise(90, 'Any illness in a baby under 3 months is treated as urgent.');
  }

  /* ---- 4. rank the likely conditions across the whole selection ----- */
  const conditionMap = new Map<string, { c: ConditionMatch; sum: number; hits: number }>();
  selected.forEach(({ symptom }) => {
    const cap = symptom.conditions.reduce((m, c) => Math.max(m, c.weight), 1);
    symptom.conditions.forEach((cond) => {
      const entry = conditionMap.get(cond.name) ?? {
        c: { name: cond.name, icd10: cond.icd10, specialist: cond.specialist, score: 0, factors: [] },
        sum: 0, hits: 0,
      };
      entry.sum += cond.weight / cap;
      entry.hits += 1;
      entry.c.factors.push(symptom.label);
      conditionMap.set(cond.name, entry);
    });
  });

  /* Score = how much of the whole picture this condition explains:
     coverage (how many of my symptoms point to it) weighted by how strongly
     each of those symptoms points to it, capped so nothing reads as certain. */
  const conditions: ConditionMatch[] = [...conditionMap.values()]
    .map((entry) => {
      const coverage = entry.hits / Math.max(symptomCount, 1);
      const strength = entry.sum / entry.hits;
      const score = Math.min(96, Math.round(100 * Math.pow(coverage, 0.6) * strength));
      return { ...entry.c, score };
    })
    .filter((c) => c.score >= 12)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);
  /* ---- 5. first aid: red-flag actions first, then symptom guides ---- */
  const firstAidIds: string[] = [];
  redFlags.forEach((f) => f.firstAid.forEach((id) => firstAidIds.push(id)));
  selected.forEach(({ symptom }) => symptom.firstAid.forEach((id) => firstAidIds.push(id)));
  if (months < 3) firstAidIds.push('fa.newborn');
  const firstAid = [...new Set(firstAidIds)]
    .map((id) => firstAidForAge(id, months))
    .filter((g): g is FirstAidGuide => Boolean(g))
    .slice(0, 6);

  /* ---- 6. home care, watch-for list, specialist -------------------- */
  const homeCare = [...new Set(selected.flatMap(({ symptom }) => symptom.homeCare))].slice(0, 8);

  const watchFor = [...new Set(selected.flatMap(({ symptom }) => symptom.flags))]
    .filter((id) => !checkedFlagIds.has(id))
    .map((id) => RED_FLAGS.find((f) => f.id === id))
    .filter((f): f is RedFlag => Boolean(f))
    .filter((f) => tierById(f.tier).level > level)
    .sort((a, b) => tierById(b.tier).level - tierById(a.tier).level)
    .slice(0, 5);

  const specialist = conditions.length ? conditions[0].specialist : null;

  /* ---- 7. narrative summary ---------------------------------------- */
  const tier = URGENCY_TIERS.find((t) => t.level === level) ?? URGENCY_TIERS[URGENCY_TIERS.length - 1];
  const isChild = months < 144;
  const who = input.model === 'female'
    ? (isChild ? 'a girl' : band === 'teen' ? 'a teen girl' : 'a woman')
    : (isChild ? 'a boy' : band === 'teen' ? 'a teen boy' : 'a man');
  const regionNames = [...regions].map((r) => L(regionById(r)?.caption ?? r)).join(', ');
  const top = conditions.slice(0, 2).map((c) => L(c.name)).join(lang === 'en' ? ' or ' : ' किंवा ');
  const durationText = maxDuration === 0
    ? L('starting today')
    : L('lasting up to {n} day{s}', { n: maxDuration, s: maxDuration > 1 ? 's' : '' });
  const summary = [
    L('You reported {count} symptom{s} for {who} aged {age} ({band}), in the {regions} area{sa}, {duration}, worst severity {sev}/10.', {
      count: symptomCount, s: symptomCount === 1 ? '' : 's', who: L(who),
      age: scFormatAge(lang, months), band: scAgeBandLabel(lang, band),
      regions: regionNames, sa: regionCount > 1 ? 's' : '', duration: durationText, sev: maxSeverity,
    }),
    redFlags.length
      ? L('{n} warning sign{s} {was} confirmed — this is what sets the urgency below.', {
        n: redFlags.length, s: redFlags.length === 1 ? '' : 's',
        was: lang === 'en' ? (redFlags.length === 1 ? 'was' : 'were') : '',
      })
      : L('No emergency warning signs were confirmed in the questions you answered.'),
    top ? L('The combination fits {top} best, but only a clinician can confirm it.', { top }) : '',
    L('Triage result: {tier} — {timeframe}.', { tier: L(tier.short), timeframe: L(tier.timeframe) }),
  ].filter(Boolean).join(' ');

  return {
    tier, reasons, redFlags, firstAid, homeCare, watchFor, conditions,
    specialist, symptomCount, regionCount, maxDuration, maxSeverity,
    ageMonths: months, ageLabel: scFormatAge(lang, months), ageBandLabel: scAgeBandLabel(lang, band),
    summary,
  };
}
