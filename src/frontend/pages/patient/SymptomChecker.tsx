import { useMemo, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle, ArrowLeft, ArrowRight, Baby, CalendarDays, Check, Info, RotateCcw, Search, Sparkles, Trash2, User, Users,
} from 'lucide-react';
import { BodyMap } from '../../components/symptom-checker/BodyMap';
import { SymptomResults } from '../../components/symptom-checker/SymptomResults';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';
import { scT, scAgeBandLabel, scModelLabel } from '../../i18n/symptomChecker';
import { BODY_MODELS, BODY_REGIONS, regionById } from '../../../mock-data/symptomCheckerBody';
import { RED_FLAGS, SECONDARY_QUESTIONS, tierById, type BodyType, type RedFlag, type ViewSide } from '../../../mock-data/symptomCheckerTriage';
import {
  commonSymptoms, searchSymptoms, symptomById, symptomsForRegion, type Symptom,
} from '../../../mock-data/symptomCheckerSymptoms';
import { analyzeSymptoms, type Assessment, type SelectedSymptom } from '../../utils/symptomTriage';

interface SymptomCheckerProps {
  onNavigate?: (route: string) => void;
}

const DURATION_OPTIONS = [
  { days: 0, label: 'Today' },
  { days: 2, label: '1–3 days' },
  { days: 5, label: '4–7 days' },
  { days: 10, label: '1–2 weeks' },
  { days: 15, label: 'More than 2 weeks' },
];

const STEPS = ['Who', 'Where', 'Details', 'Result'];

const severityColor = (n: number) =>
  n >= 9 ? 'text-rose-600' : n >= 7 ? 'text-orange-600' : n >= 4 ? 'text-amber-600' : 'text-sahaay-deep';

const modelIcon: Record<BodyType, typeof User> = { male: User, female: Users };

interface AIAnalysis {
  ai_connected: boolean;
  summary: string;
  urgency_score: number;
  urgency_tier: string;
  reasons: string[];
  conditions: Assessment['conditions'];
  specialist: string | null;
  home_care: string[];
  recommended_tests: string[];
}

const ageBandOf = (months: number): 'neonate' | 'infant' | 'child' | 'teen' | 'adult' | 'senior' =>
  months < 1 ? 'neonate' : months < 12 ? 'infant' : months < 144 ? 'child' : months < 216 ? 'teen' : months < 780 ? 'adult' : 'senior';

/* Age presets keep the currently selected sex card; age alone drives child/adult rules. */
const AGE_PRESETS: { years: number; months: number }[] = [
  { years: 0, months: 1 },
  { years: 2, months: 0 },
  { years: 7, months: 0 },
  { years: 16, months: 0 },
  { years: 32, months: 0 },
  { years: 70, months: 0 },
];

/* Consumer-app card themes — one vivid gradient per model (Swiggy/Instamart energy). */
const MODEL_THEME: Record<BodyType, {
  card: string;
  activeRing: string;
  glow: string;
  text: string;
  muted: string;
  badge: string;
}> = {
  male: {
    card: 'linear-gradient(145deg, #E0F2FE 0%, #BAE6FD 45%, #7DD3FC 100%)',
    activeRing: 'rgba(14, 165, 201, 0.55)',
    glow: '0 10px 28px rgba(14, 165, 201, 0.35)',
    text: '#076A82',
    muted: '#0C4A6E',
    badge: 'linear-gradient(135deg, #0EA5C9, #0284C7)',
  },
  female: {
    card: 'linear-gradient(145deg, #FFE4E6 0%, #FECDD3 45%, #FDA4AF 100%)',
    activeRing: 'rgba(244, 63, 94, 0.5)',
    glow: '0 10px 28px rgba(244, 63, 94, 0.32)',
    text: '#9F1239',
    muted: '#881337',
    badge: 'linear-gradient(135deg, #FB7185, #E11D48)',
  },
};

/* Illustrated, full-colour characters — halo, skin, outfit, floating sparkles. */
function ModelFigure({ model, active }: { model: BodyType; active: boolean }) {
  const uid = `mf-${model}`;
  const [haloA, haloB] =
    model === 'male' ? ['#38BDF8', '#0EA5C9']
    : ['#FB7185', '#E11D48'];
  const skin = model === 'female' ? '#F5C6A5' : '#E8B48A';
  const hair = model === 'male' ? '#1F2937' : '#4A1D3F';
  const top = model === 'male' ? '#0369A1' : '#BE123C';
  const topDark = model === 'male' ? '#075985' : '#9F1239';
  const bottom = model === 'male' ? '#1E3A5F' : '#4C0519';
  const accent = model === 'male' ? '#7DD3FC' : '#FECDD3';

  return (
    <span className={`relative flex h-28 w-24 shrink-0 items-center justify-center ${active ? 'animate-float' : ''}`}>
      <svg viewBox="0 0 96 140" className="h-full w-full" aria-hidden="true">
        <defs>
          <linearGradient id={`${uid}-halo`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={haloA} />
            <stop offset="100%" stopColor={haloB} />
          </linearGradient>
          <linearGradient id={`${uid}-top`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={top} />
            <stop offset="100%" stopColor={topDark} />
          </linearGradient>
          <filter id={`${uid}-soft`} x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="3" />
          </filter>
        </defs>

        {/* colour halo + soft ground shadow */}
        <ellipse cx="48" cy="72" rx="40" ry="44" fill={`url(#${uid}-halo)`} opacity={active ? 0.35 : 0.22} />
        <ellipse cx="48" cy="128" rx="26" ry="7" fill="#052e16" opacity="0.12" filter={`url(#${uid}-soft)`} />

        {/* orbiting sparkle dots */}
        <circle cx="18" cy="36" r="3.5" fill={haloA} opacity={active ? 0.95 : 0.55} className={active ? 'animate-pulse-soft' : ''} />
        <circle cx="78" cy="48" r="2.5" fill={haloB} opacity={active ? 0.95 : 0.5} />
        <circle cx="72" cy="24" r="2" fill={accent} opacity={active ? 1 : 0.6} className={active ? 'animate-float-delay' : ''} />

        {model === 'male' && (
          <g>
            <path d="M48 34c-13 0-22 7-23 17l-3 22h6l2-14v20l-4 36c-.4 5 3 9 8 9s7.6-4 7.4-9L42 84l3.6 30c-.2 5 3 9 8 9s8.4-4 8-9l-4-36V59l2 14h6l-3-22c-1-10-10-17-23-17z" fill={`url(#${uid}-top)`} />
            <path d="M42 84h12l-1 36c0 3-2.4 5-5 5s-5-2-5-5z" fill={bottom} />
            <ellipse cx="48" cy="22" rx="13" ry="14" fill={skin} />
            <path d="M35 20c1-11 9-16 18-15 8 1 13 7 13 15-4-5-10-7-18-6-5 1-9 3-13 6z" fill={hair} />
            <circle cx="43" cy="23" r="1.6" fill="#1F2937" />
            <circle cx="53" cy="23" r="1.6" fill="#1F2937" />
            <path d="M45 29c1.5 2 4.5 2 6 0" stroke="#B45309" strokeWidth="1.4" fill="none" strokeLinecap="round" />
            <rect x="44" y="34" width="8" height="7" rx="3" fill={skin} />
            <path d="M30 60h8v5h-8zM58 60h8v5h-8z" fill={accent} opacity="0.55" rx="2" />
          </g>
        )}

        {model === 'female' && (
          <g>
            <path d="M48 36c-14 0-24 7-26 18l-4 20c-1 5 1.5 9 5.5 9H28l1 12c0 5-2 10-4.5 19-2.5 10-2 24 0 30 1 4 4.5 6.5 9 6.5s8-2.5 9-6.5c1.5-6 2-20 0-30-2.5-9-4.5-14-4.5-19l1-12h6l1 12c0 5-2 10-4.5 19-2.5 10-2 24 0 30 1 4 4.5 6.5 9 6.5s8-2.5 9-6.5c2-6 2.5-20 0-30-2.5-9-4.5-14-4.5-19l1-12h5c4 0 6.5-4 5.5-9l-4-20c-2-11-12-18-26-18z" fill={`url(#${uid}-top)`} />
            <path d="M31 55c-3 8-4 16-4 24l3 4c1-10 3-18 6-24zM65 55c3 8 4 16 4 24l-3 4c-1-10-3-18-6-24z" fill={skin} />
            <ellipse cx="48" cy="22" rx="12" ry="13" fill={skin} />
            <path d="M34 24c0-14 8-20 16-20 9 0 15 7 15 20 0 4-1 8-2 11-1-8-4-13-8-15-6 3-14 4-21 4z" fill={hair} />
            <path d="M34 20c-2 8-1 16 1 22 3-6 4-14 3-22zM62 20c2 8 1 16-1 22-3-6-4-14-3-22z" fill={hair} />
            <circle cx="43.5" cy="23" r="1.5" fill="#1F2937" />
            <circle cx="52.5" cy="23" r="1.5" fill="#1F2937" />
            <path d="M45.5 29c1.4 1.8 3.6 1.8 5 0" stroke="#BE123C" strokeWidth="1.4" fill="none" strokeLinecap="round" />
            <rect x="44.5" y="34" width="7" height="6" rx="3" fill={skin} />
            <circle cx="48" cy="58" r="3" fill={accent} opacity="0.9" />
          </g>
        )}
      </svg>
    </span>
  );
}

export function SymptomChecker({ onNavigate = () => {} }: SymptomCheckerProps) {
  const { showToast } = useToast();
  const { language, t } = useLanguage();
  const L = useCallback(
    (source: string, params?: Record<string, string | number>) => scT(language, source, params),
    [language],
  );
  const [step, setStep] = useState(0);
  const [model, setModel] = useState<BodyType>('male');
  const [ageYears, setAgeYears] = useState(32);
  const [ageMonthPart, setAgeMonthPart] = useState(0);
  const [side, setSide] = useState<ViewSide>('front');
  const [activeRegions, setActiveRegions] = useState<string[]>([]);
  const [picked, setPicked] = useState<SelectedSymptom[]>([]);
  const [secondary, setSecondary] = useState<string[]>([]);
  const [notes, setNotes] = useState('');
  const [query, setQuery] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const ageMonths = Math.max(0, ageYears * 12 + (ageYears <= 1 ? ageMonthPart : 0));
  const ageLabel = ageYears === 0
    ? L(ageMonthPart === 1 ? '{n} month' : '{n} months', { n: ageMonthPart })
    : ageYears === 1 && ageMonthPart
      ? L(ageMonthPart === 1 ? '{y} year {m} month' : '{y} year {m} months', { y: 1, m: ageMonthPart })
      : L(ageYears === 1 ? '{n} year' : '{n} years', { n: ageYears });
  const bandLabel = scAgeBandLabel(language, ageBandOf(ageMonths));
  const modelLabelOf = (m: BodyType) => scModelLabel(language, m);

  const selectedSymptoms = picked.map((p) => symptomById(p.id)).filter((s): s is Symptom => Boolean(s));
  const assessment = useMemo(
    () => analyzeSymptoms({ model, ageMonths, symptoms: picked, secondary, language }),
    [model, ageMonths, picked, secondary, language],
  );
  const displayAssessment = useMemo<Assessment>(() => {
    if (!aiAnalysis) return assessment;
    return {
      ...assessment,
      tier: tierById(aiAnalysis.urgency_tier),
      summary: aiAnalysis.summary,
      reasons: [...assessment.reasons, ...aiAnalysis.reasons].slice(0, 8),
      conditions: aiAnalysis.conditions.length ? aiAnalysis.conditions : assessment.conditions,
      specialist: aiAnalysis.specialist || assessment.specialist,
      homeCare: aiAnalysis.home_care.length ? aiAnalysis.home_care : assessment.homeCare,
    };
  }, [aiAnalysis, assessment]);

  /* ---- selection helpers ---- */
  const toggleRegion = (id: string) =>
    setActiveRegions((prev) => (prev.includes(id) ? prev.filter((r) => r !== id) : [...prev, id]));

  const toggleSymptom = (symptom: Symptom) =>
    setPicked((prev) => prev.some((p) => p.id === symptom.id)
      ? prev.filter((p) => p.id !== symptom.id)
      : [...prev, { id: symptom.id, durationDays: 0, severity: 5, flags: [] }]);

  const toggleFlag = (symptomId: string, flagId: string) =>
    setPicked((prev) => prev.map((p) => p.id === symptomId
      ? { ...p, flags: p.flags.includes(flagId) ? p.flags.filter((f) => f !== flagId) : [...p.flags, flagId] }
      : p));

  const patch = (id: string, next: Partial<SelectedSymptom>) =>
    setPicked((prev) => prev.map((p) => (p.id === id ? { ...p, ...next } : p)));

  const reset = () => {
    setStep(0); setActiveRegions([]); setPicked([]); setSecondary([]); setQuery(''); setShowAll(false); setNotes('');
    setAgeYears(32); setAgeMonthPart(0);
    setAiAnalysis(null);
  };

  const pickModel = (id: BodyType) => {
    setModel(id);
    setPicked([]); setActiveRegions([]); setSecondary([]); setNotes('');
  };

  const goToResults = async () => {
    setStep(3);
    setAiAnalysis(null);
    setAiLoading(true);
    if (assessment.tier.level >= 90) showToast(`${L(assessment.tier.short)}: ${L(assessment.tier.timeframe)}`);
    try {
      const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
      const response = await fetch(`${apiBase}/symptoms/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model,
          age_months: ageMonths,
          regions: activeRegions.map(region => regionById(region)?.caption || region),
          symptoms: picked.map(item => ({
            ...item,
            label: symptomById(item.id)?.label || item.id,
            region: symptomById(item.id)?.region || 'unknown',
            duration_days: item.durationDays,
          })),
          secondary,
          notes,
          language,
        }),
      });
      if (response.ok) setAiAnalysis(await response.json() as AIAnalysis);
      else showToast('AI analysis unavailable. Local safety triage shown.');
    } catch {
      showToast('AI analysis unavailable. Local safety triage shown.');
    } finally {
      setAiLoading(false);
    }
  };

  /* ---- the catalogue shown in step 2 ---- */
  const list: Symptom[] = useMemo(() => {
    const unique = (arr: Symptom[]) => {
      const seen = new Set<string>();
      return arr.filter((s) => (seen.has(s.id) ? false : (seen.add(s.id), true)));
    };
    if (query.trim()) return searchSymptoms(query, model, ageMonths, 40, (s) => L(s.label));
    if (activeRegions.length) return unique(activeRegions.flatMap((r) => symptomsForRegion(r, model, ageMonths)));
    if (showAll) return unique(BODY_REGIONS.flatMap((r) => symptomsForRegion(r.id, model, ageMonths)));
    return commonSymptoms(model, ageMonths);
  }, [query, model, ageMonths, activeRegions, showAll, L]);

  const universalFlags = useMemo(
    () => RED_FLAGS.filter((f) => f.firstAid.length > 0 && f.tier === 'call911' && !f.regions),
    [],
  );

  const ageOk = ageYears >= 0 && ageMonthPart >= 0 && ageMonthPart <= 11 && (ageYears > 0 || ageMonthPart >= 0);
  const canContinue = (step !== 0 || ageOk) && (step !== 2 || picked.length > 0 || notes.trim().length > 0);
  const NavButtons = (
    <div className="flex items-center justify-end gap-3">
      {step < 2 ? (
        <button
          onClick={() => setStep((s) => s + 1)}
          disabled={step === 0 && !ageOk}
          className="sahaay-btn-primary flex items-center gap-2 px-5 py-2 text-sm disabled:opacity-50"
        >
          {step === 0 ? t('sc.nav.chooseAreas') : t('sc.nav.addDetails')} <ArrowRight size={15} />
        </button>
      ) : (
        <button onClick={goToResults} disabled={!canContinue} className="sahaay-btn-primary flex items-center gap-2 px-5 py-2 text-sm disabled:opacity-50">
          <Sparkles size={15} /> {t('sc.nav.seeResult')}
        </button>
      )}
    </div>
  );

  return (
    <div className="space-y-5">
      {/* ---------- shell header ---------- */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card-elevated p-5 lg:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-2xl">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-vital-nerve/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.14em] text-vital-nerve-ink">
              <Sparkles size={11} /> {t('sc.badge')}
            </span>
            <h1 className="mt-2 font-display text-2xl font-bold text-ink-900 dark:text-slate-100">{t('sc.title')}</h1>
            <p className="mt-1 text-sm text-ink-500">
              {t('sc.headerDesc')}
            </p>
          </div>
          {picked.length > 0 && (
            <button onClick={reset} className="flex items-center gap-2 rounded-xl border border-sahaay-deep/15 bg-white/70 px-3.5 py-2 text-xs font-semibold text-ink-600 hover:bg-white">
              <RotateCcw size={13} /> {t('sc.startOver')}
            </button>
          )}
        </div>

        {/* stepper */}
        <div className="mt-5 flex flex-wrap items-center gap-2">
          {STEPS.map((label, i) => {
            const done = i < step;
            const active = i === step;
            const stepKey = (['sc.step.who', 'sc.step.where', 'sc.step.details', 'sc.step.result'] as const)[i];
            return (
              <button
                key={label}
                onClick={() => { if (i < step || (i === 2 && picked.length > 0) || i === 3) setStep(i); }}
                className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-[11px] font-semibold transition-colors ${
                  active ? 'border-sahaay-deep bg-sahaay-deep text-white'
                    : done ? 'border-sahaay-deep/25 bg-sahaay-surface text-sahaay-deep'
                      : 'border-sahaay-deep/10 bg-white/60 text-ink-400'
                }`}
              >
                <span className={`flex h-4 w-4 items-center justify-center rounded-full text-[10px] ${active || done ? 'bg-white/25' : 'bg-black/5'}`}>
                  {done ? <Check size={10} /> : i + 1}
                </span>
                {t(stepKey)}
                {i === 1 && picked.length > 0 && <span className="rounded-full bg-white/25 px-1.5">{picked.length}</span>}
              </button>
            );
          })}
        </div>
      </motion.div>
      <div className="flex items-center">
        <button
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={step === 0}
          className="flex items-center gap-1.5 rounded-xl border border-sahaay-deep/15 bg-[rgba(255,255,255,0.7)] px-3.5 py-1.5 text-sm font-semibold text-ink-600 transition-colors hover:border-sahaay-deep hover:bg-sahaay-deep hover:text-white disabled:pointer-events-none disabled:opacity-40 dark:border-white/15 dark:bg-white/10 dark:text-slate-300 dark:hover:border-sahaay-500 dark:hover:bg-sahaay-700 dark:hover:text-white"
        >
          <ArrowLeft size={15} /> {t('sc.nav.back')}
        </button>
      </div>
      <AnimatePresence mode="wait">
        {/* ---------- STEP 1 · who ---------- */}
        {step === 0 && (
          <motion.div key="who" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} className="space-y-5">
            <div className="glass-card-elevated p-5 lg:p-6">
              <h2 className="text-sm font-bold text-ink-900 dark:text-slate-100">{t('sc.who.title')}</h2>
              <p className="mt-1 text-xs text-ink-500">
                {t('sc.who.desc')}
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {BODY_MODELS.map((m) => {
                  const Icon = modelIcon[m.id];
                  const active = model === m.id;
                  const theme = MODEL_THEME[m.id];
                  return (
                    <motion.button
                      key={m.id}
                      onClick={() => pickModel(m.id)}
                      aria-pressed={active}
                      whileHover={{ y: -4, scale: 1.02 }}
                      whileTap={{ scale: 0.97 }}
                      transition={{ type: 'spring', stiffness: 380, damping: 24 }}
                      className={`relative flex flex-col items-center gap-1 overflow-hidden rounded-3xl border-2 px-3 pb-4 pt-3 text-center outline-none transition-shadow focus-visible:ring-2 focus-visible:ring-sahaay-400 ${
                        active ? 'shadow-lg' : 'border-transparent hover:border-white/70 hover:shadow-md'
                      }`}
                      style={{
                        background: theme.card,
                        borderColor: active ? theme.activeRing : undefined,
                        boxShadow: active ? theme.glow : undefined,
                      }}
                    >
                      {/* soft decorative blobs */}
                      <span
                        aria-hidden
                        className="pointer-events-none absolute -right-6 -top-8 h-20 w-20 rounded-full opacity-40 blur-xl"
                        style={{ background: theme.badge }}
                      />
                      <span
                        aria-hidden
                        className="pointer-events-none absolute -bottom-8 -left-6 h-16 w-16 rounded-full opacity-30 blur-lg"
                        style={{ background: theme.badge }}
                      />

                      <span className={`absolute right-2 top-2 z-10 flex h-6 w-6 items-center justify-center rounded-full text-white transition-all ${active ? 'scale-100 opacity-100' : 'scale-0 opacity-0'}`} style={{ background: theme.badge }}>
                        <Check size={13} strokeWidth={3} />
                      </span>

                      <ModelFigure model={m.id} active={active} />

                      <span className="relative z-[1] mt-1 flex items-center gap-1.5 text-sm font-extrabold tracking-tight" style={{ color: theme.text }}>
                        <Icon size={15} strokeWidth={2.5} /> {modelLabelOf(m.id)}
                      </span>
                      <span className="relative z-[1] text-[11px] font-medium" style={{ color: theme.muted, opacity: 0.85 }}>
                        {L(m.hint)}
                      </span>
                      <span
                        className={`relative z-[1] mt-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white transition-opacity ${active ? 'opacity-100' : 'opacity-0'}`}
                        style={{ background: theme.badge }}
                      >
                        {t('sc.model.selected')}
                      </span>
                    </motion.button>
                  );
                })}
              </div>

              {/* ---- age input ---- */}
              <div className="mt-4 rounded-2xl border border-sahaay-deep/12 bg-white/70 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="flex items-center gap-1.5 text-sm font-bold text-ink-900 dark:text-slate-100">
                      <CalendarDays size={14} className="text-sahaay-deep" /> {t('sc.age.title')}
                    </p>
                    <p className="mt-0.5 text-[11px] text-ink-500">
                      {t('sc.age.desc')}
                    </p>
                  </div>
                  <span className="rounded-full bg-sahaay-deep/10 px-2.5 py-1 text-[11px] font-bold text-sahaay-deep">
                    {bandLabel}
                  </span>
                </div>

                <div className="mt-3 flex flex-wrap items-end gap-3">
                  <label className="block">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-ink-400">{t('sc.age.years')}</span>
                    <input
                      type="number"
                      min={0}
                      max={120}
                      value={ageYears}
                      onChange={(e) => {
                        const v = Number(e.target.value);
                        setAgeYears(Number.isFinite(v) ? Math.min(120, Math.max(0, Math.floor(v))) : 0);
                      }}
                      className="sahaay-input mt-1 w-16 min-h-[32px] px-2 py-1 text-sm"
                      aria-label={t('sc.age.ariaYears')}
                    />
                  </label>
                  <label className="block">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-ink-400">
                      {ageYears === 0 ? t('sc.age.months') : t('sc.age.extraMonths')}
                    </span>
                    <input
                      type="number"
                      min={0}
                      max={11}
                      value={ageMonthPart}
                      disabled={ageYears > 1}
                      onChange={(e) => {
                        if (ageYears > 1) return;
                        const v = Number(e.target.value);
                        setAgeMonthPart(Number.isFinite(v) ? Math.min(11, Math.max(0, Math.floor(v))) : 0);
                      }}
                      className="sahaay-input mt-1 w-16 min-h-[32px] px-2 py-1 text-sm disabled:opacity-40"
                      aria-label={t('sc.age.ariaMonths')}
                    />
                  </label>
                  <div className="flex flex-wrap items-center gap-1.5 pb-0.5">
                    <span className="text-[11px] text-ink-400">{t('sc.age.quick')}</span>
                    {AGE_PRESETS.map((p) => (
                      <button
                        key={`${p.years}-${p.months}`}
                        type="button"
                        onClick={() => {
                          setAgeYears(p.years);
                          setAgeMonthPart(p.months);
                          setPicked([]); setActiveRegions([]); setSecondary([]);
                        }}
                        className={`rounded-full border px-2.5 py-1 text-[11px] font-semibold transition-colors ${
                          ageYears === p.years && (p.years > 0 || ageMonthPart === p.months)
                            ? 'border-sahaay-deep bg-sahaay-deep text-white'
                            : 'border-sahaay-deep/15 bg-white/70 text-ink-600 hover:bg-white'
                        }`}
                      >
                        {p.years === 0 ? t('sc.age.presetMo', { n: p.months }) : t('sc.age.presetY', { n: p.years })}
                      </button>
                    ))}
                  </div>
                </div>
                <p className="mt-2 flex items-center gap-1.5 text-[11px] text-ink-500">
                  <Baby size={12} className="shrink-0 text-vital-nerve" />
                  {t('sc.age.entered')} <strong className="text-ink-700 dark:text-slate-200">{ageLabel}</strong>
                  {ageMonths < 3 && ` ${t('sc.age.under3')}`}
                  {ageMonths >= 780 && ` ${t('sc.age.over65')}`}
                </p>
              </div>

              <div className="mt-4 rounded-xl border border-sahaay-deep/10 bg-sahaay-surface p-3 text-[11px] text-ink-600">
                <span className="flex items-center gap-1.5 font-semibold"><Info size={12} /> {t('sc.emergency.label')}</span>
                <p className="mt-1">
                  {t('sc.emergency.p1')} <strong>108</strong> {t('sc.emergency.p2')} <strong>112</strong>{' '}
                  {t('sc.emergency.p3')}
                </p>
              </div>
            </div>
            <div className="glass-card p-4">{NavButtons}</div>
          </motion.div>
        )}
        {/* ---------- STEP 2 · where & what ---------- */}
        {step === 1 && (
          <motion.div key="where" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} className="space-y-5">
            <div className="grid gap-5 lg:grid-cols-[minmax(400px,560px)_1fr]">
              {/* body map */}
              <div className="glass-card-elevated p-4 lg:p-5">
                <div className="flex items-center justify-between gap-2">
                  <h2 className="text-sm font-bold text-ink-900 dark:text-slate-100">{t('sc.where.title')}</h2>
                  <span className="text-[11px] font-semibold text-ink-400">
                    {activeRegions.length
                      ? t(activeRegions.length > 1 ? 'sc.where.areas' : 'sc.where.area', { n: activeRegions.length })
                      : t('sc.where.tapBody')}
                  </span>
                </div>
                <p className="mt-1 text-xs text-ink-500">
                  {t('sc.where.meta', { model: modelLabelOf(model), age: ageLabel })}
                </p>
                <div className="mt-3">
                  <BodyMap
                    model={model}
                    side={side}
                    selectedRegions={activeRegions}
                    onSelectRegion={toggleRegion}
                    onToggleSide={() => setSide((s) => (s === 'front' ? 'back' : 'front'))}
                    onSelectSide={setSide}
                  />
                </div>
                <div className="mt-3 flex flex-wrap gap-2 border-t border-sahaay-deep/8 pt-3">
                  <button
                    onClick={() => { setActiveRegions([]); setShowAll(false); }}
                    className="rounded-lg border border-sahaay-deep/12 px-2.5 py-1.5 text-[11px] font-semibold text-ink-500 hover:bg-white"
                  >
                    {t('sc.where.clearAreas')}
                  </button>
                  <button
                    onClick={() => setShowAll((v) => !v)}
                    className="rounded-lg border border-sahaay-deep/12 px-2.5 py-1.5 text-[11px] font-semibold text-ink-500 hover:bg-white"
                  >
                    {showAll ? t('sc.where.showCommon') : t('sc.where.showEvery')}
                  </button>
                </div>
              </div>

              {/* symptom list */}
              <div className="glass-card-elevated p-4 lg:p-5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h2 className="text-sm font-bold text-ink-900 dark:text-slate-100">{t('sc.pick.title')}</h2>
                  <span className="rounded-full bg-sahaay-deep/8 px-2.5 py-1 text-[11px] font-semibold text-sahaay-deep">
                    {t('sc.pick.count', { n: picked.length })}
                  </span>
                </div>
                <p className="mt-1 text-xs text-ink-500">{t('sc.pick.desc')}</p>

                <div className="relative mt-3">
                  <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-300" />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={t('sc.pick.search')}
                    className="sahaay-input pl-9"
                  />
                </div>

                {activeRegions.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {activeRegions.map((r) => (
                      <span key={r} className="flex items-center gap-1 rounded-full bg-sahaay-surface px-2.5 py-1 text-[11px] font-medium text-ink-600">
                        {L(regionById(r)?.caption ?? r)}
                        <button onClick={() => toggleRegion(r)} aria-label={`Remove ${regionById(r)?.caption}`}>
                          <Trash2 size={11} className="text-ink-400 hover:text-rose-500" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
                {/* symptom list */}
                <div className="mt-4 max-h-[430px] space-y-2 overflow-y-auto pr-1">
                  {list.map((s) => {
                    const isPicked = picked.some((p) => p.id === s.id);
                    const flagCount = s.flags.length;
                    return (
                      <button
                        key={s.id}
                        onClick={() => toggleSymptom(s)}
                        aria-pressed={isPicked}
                        className={`flex w-full items-start gap-3 rounded-xl border p-3 text-left transition-all ${
                          isPicked ? 'border-sahaay-deep/40 bg-sahaay-surface' : 'border-sahaay-deep/10 bg-white/60 hover:bg-white'
                        }`}
                      >
                        <span className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                          isPicked ? 'border-sahaay-deep bg-sahaay-deep text-white' : 'border-ink-300'
                        }`}>
                          {isPicked && <Check size={11} />}
                        </span>
                        <span className="flex-1">
                          <span className="flex flex-wrap items-center gap-2">
                            <span className="text-xs font-semibold text-ink-800 dark:text-slate-200">{L(s.label)}</span>
                            {s.common && <span className="rounded bg-vital-oxy/12 px-1.5 py-0.5 text-[9px] font-bold uppercase text-vital-oxy-ink">{t('sc.pick.common')}</span>}
                          </span>
                          <span className="mt-0.5 block text-[11px] text-ink-400">
                            {L(regionById(s.region)?.caption ?? s.region)} ·{' '}
                            {s.audience === 'peds' ? t('sc.audience.peds') : s.audience === 'adult' ? t('sc.audience.adult') : t('sc.audience.all')}
                          </span>
                        </span>
                        {flagCount > 0 && (
                          <span className="flex shrink-0 items-center gap-1 rounded-full bg-rose-50 px-2 py-0.5 text-[10px] font-semibold text-rose-600"
                            title={t('sc.pick.flagTitle', { n: flagCount })}>
                            <AlertTriangle size={10} /> {flagCount}
                          </span>
                        )}
                      </button>
                    );
                  })}
                  {list.length === 0 && (
                    <div className="rounded-xl border border-dashed border-sahaay-deep/15 p-6 text-center">
                      <p className="text-sm font-semibold text-ink-600">{t('sc.pick.noMatch', { q: query })}</p>
                      <p className="mt-1 text-xs text-ink-400">{t('sc.pick.noMatchHint')}</p>
                    </div>
                  )}
                </div>

                <p className="mt-2 text-[11px] text-ink-400">
                  {t('sc.pick.showing', { n: list.length, s: list.length === 1 ? '' : 's' })}
                  {activeRegions.length
                    ? t('sc.pick.forRegions', { regions: activeRegions.map((r) => L(regionById(r)?.caption ?? r)).join(', ') })
                    : ''}
                  {query.trim() ? t('sc.pick.matching', { q: query }) : ''}
                </p>
              </div>
            </div>

            {/* selection tray */}
            {picked.length > 0 && (
              <div className="glass-card p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="text-sm font-bold text-ink-900 dark:text-slate-100">
                    {t('sc.tray.title', { n: picked.length })}
                  </h3>
                  <button onClick={() => setPicked([])} className="text-[11px] font-semibold text-ink-400 hover:text-rose-500">
                    {t('sc.tray.clearAll')}
                  </button>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {selectedSymptoms.map((s) => (
                    <span key={s.id} className="flex items-center gap-2 rounded-full border border-sahaay-deep/15 bg-white/70 px-3 py-1.5 text-xs font-semibold text-ink-700">
                      {L(s.label)}
                      <button onClick={() => toggleSymptom(s)} aria-label={`Remove ${s.label}`}>
                        <Trash2 size={12} className="text-ink-400 hover:text-rose-500" />
                      </button>
                    </span>
                  ))}
                </div>
                <p className="mt-3 flex items-start gap-1.5 text-[11px] text-ink-400">
                  <Info size={12} className="mt-0.5 shrink-0" />
                  {t('sc.tray.info')}
                </p>
              </div>
            )}
            <div className="glass-card p-4">{NavButtons}</div>
          </motion.div>
        )}
        {/* ---------- STEP 3 · details ---------- */}
        {step === 2 && (
          <motion.div key="details" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} className="space-y-5">
            <div className="glass-card p-3.5 text-[11px] text-ink-500">
              {t('sc.details.instr')}
            </div>

            {picked.map((p) => {
              const symptom = symptomById(p.id);
              if (!symptom) return null;
              const own = symptom.flags
                .map((id) => RED_FLAGS.find((f) => f.id === id))
                .filter((f): f is RedFlag => Boolean(f));
              const extras = universalFlags.filter((u) => !own.some((o) => o.id === u.id));
              const all = [...own, ...extras];
              return (
                <div key={p.id} className="glass-card-elevated p-4 lg:p-5">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <h3 className="text-sm font-bold text-ink-900 dark:text-slate-100">{L(symptom.label)}</h3>
                      <p className="text-[11px] text-ink-400">{L(regionById(symptom.region)?.caption ?? symptom.region)}</p>
                    </div>
                    <button onClick={() => toggleSymptom(symptom)} className="flex items-center gap-1.5 text-[11px] font-semibold text-ink-400 hover:text-rose-500">
                      <Trash2 size={12} /> {t('sc.details.remove')}
                    </button>
                  </div>

                  <div className="mt-4 grid gap-4 sm:grid-cols-2">
                    {/* duration */}
                    <div>
                      <p className="text-[11px] font-bold uppercase tracking-wider text-ink-400">{t('sc.details.howLong')}</p>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {DURATION_OPTIONS.map((opt) => (
                          <button
                            key={opt.days}
                            onClick={() => patch(p.id, { durationDays: opt.days })}
                            className={`rounded-lg border px-2.5 py-1.5 text-[11px] font-semibold transition-colors ${
                              p.durationDays === opt.days
                                ? 'border-sahaay-deep bg-sahaay-deep text-white'
                                : 'border-sahaay-deep/12 bg-white/60 text-ink-600 hover:bg-white'
                            }`}
                          >{t(opt.label === 'Today' ? 'sc.dur.today' : opt.label === '1–3 days' ? 'sc.dur.d3' : opt.label === '4–7 days' ? 'sc.dur.d7' : opt.label === '1–2 weeks' ? 'sc.dur.w2' : 'sc.dur.over2')}</button>
                        ))}
                      </div>
                    </div>

                    {/* severity */}
                    <div>
                      <div className="flex items-center justify-between">
                        <p className="text-[11px] font-bold uppercase tracking-wider text-ink-400">{t('sc.details.howBad')}</p>
                        <span className={`text-xs font-bold ${severityColor(p.severity)}`}>{p.severity}/10</span>
                      </div>
                      <input
                        type="range" min={1} max={10} step={1} value={p.severity}
                        onChange={(e) => patch(p.id, { severity: Number(e.target.value) })}
                        aria-label={t('sc.details.severityAria', { name: symptom.label })}
                        className="mt-3 w-full accent-sahaay-deep"
                      />
                      <div className="flex justify-between text-[10px] text-ink-400">
                        <span>{t('sc.details.mild')}</span><span>{t('sc.details.uncomfortable')}</span><span>{t('sc.details.worst')}</span>
                      </div>
                    </div>
                  </div>
                  {/* warning-sign checklist for this symptom */}
                  {all.length > 0 && (
                    <div className="mt-4 border-t border-sahaay-deep/8 pt-3">
                      <p className="text-[11px] font-bold uppercase tracking-wider text-ink-400">
                        {t('sc.details.flags')}
                      </p>
                      <div className="mt-2 grid gap-2 sm:grid-cols-2">
                        {all.map((f) => {
                          const on = p.flags.includes(f.id);
                          const tier = tierById(f.tier);
                          return (
                            <button
                              key={f.id}
                              onClick={() => toggleFlag(p.id, f.id)}
                              aria-pressed={on}
                              className={`flex items-start gap-2.5 rounded-xl border p-2.5 text-left transition-all ${
                                on ? 'border-rose-300 bg-rose-50/70' : 'border-sahaay-deep/10 bg-white/60 hover:bg-white'
                              }`}
                            >
                              <span className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                                on ? 'border-rose-500 bg-rose-500 text-white' : 'border-ink-300'
                              }`}>
                                {on && <Check size={11} />}
                              </span>
                              <span>
                                <span className="block text-[11px] font-medium text-ink-700 dark:text-slate-200">{L(f.text)}</span>
                                <span className={`mt-0.5 inline-block rounded px-1.5 py-0.5 text-[9px] font-bold uppercase ${tier.bg} ${tier.text}`}>
                                  {L(tier.short)}
                                </span>
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {/* personal situation — asked once for the whole assessment */}
            <div className="glass-card-elevated p-4 lg:p-5">
              <h3 className="text-sm font-bold text-ink-900 dark:text-slate-100">{t('sc.secondary.title')}</h3>
              <p className="mt-1 text-xs text-ink-500">{t('sc.secondary.desc')}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {SECONDARY_QUESTIONS
                  .filter((q) => {
                    if (q.id === 'pregnant') return model === 'female' && ageYears >= 12;
                    if (q.id === 'infant') return ageMonths < 3;
                    if (q.id === 'fever' || q.id === 'diabetes') return true;
                    return true;
                  })
                  .map((q) => {
                    const on = secondary.includes(q.id);
                    return (
                      <button
                        key={q.id}
                        onClick={() => setSecondary((prev) => (prev.includes(q.id) ? prev.filter((x) => x !== q.id) : [...prev, q.id]))}
                        aria-pressed={on}
                        className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-semibold transition-colors ${
                          on ? 'border-sahaay-deep bg-sahaay-surface text-sahaay-deep' : 'border-sahaay-deep/12 bg-white/60 text-ink-600 hover:bg-white'
                        }`}
                      >
                        <span className={`flex h-4 w-4 items-center justify-center rounded border ${on ? 'border-sahaay-deep bg-sahaay-deep text-white' : 'border-ink-300'}`}>
                          {on && <Check size={11} />}
                        </span>
                        {L(q.label)}
                      </button>
                    );
                  })}
              </div>
            </div>

            {/* free-text — symptoms not in the list */}
            <div className="glass-card-elevated p-4 lg:p-5">
              <h3 className="text-sm font-bold text-ink-900 dark:text-slate-100">{t('sc.notes.title')}</h3>
              <p className="mt-1 text-xs text-ink-500">{t('sc.notes.desc')}</p>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                maxLength={500}
                placeholder={t('sc.notes.placeholder')}
                aria-label={t('sc.notes.title')}
                className="mt-3 w-full rounded-xl border border-sahaay-deep/12 bg-white/70 px-3 py-2.5 text-sm text-ink-800 placeholder:text-ink-400 focus:border-sahaay-deep focus:outline-none focus:ring-2 focus:ring-sahaay-deep/20 dark:border-white/10 dark:bg-slate-800/60 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:border-sahaay-500"
              />
              <p className="mt-1.5 text-right text-[10px] text-ink-400">{notes.length}/500</p>
            </div>

            <div className="glass-card p-4">{NavButtons}</div>
          </motion.div>
        )}

        {/* ---------- STEP 4 · result ---------- */}
        {step === 3 && (
          <motion.div key="result" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
            <SymptomResults
               assessment={displayAssessment}
              selected={picked}
              secondary={secondary}
              notes={notes}
              model={model}
              ageLabel={ageLabel}
              onRestart={reset}
              onEdit={() => setStep(1)}
               onNavigate={onNavigate}
               aiConnected={aiAnalysis?.ai_connected ?? false}
               recommendedTests={aiAnalysis?.recommended_tests ?? []}
               aiLoading={aiLoading}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
