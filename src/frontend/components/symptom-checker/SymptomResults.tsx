import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle, BadgeCheck, CalendarDays, ChevronDown, ClipboardCopy, Flame, HeartPulse, MapPin,
  PhoneCall, RotateCcw, ShieldAlert, Sparkles, Stethoscope, Info,
} from 'lucide-react';
import { DISCLAIMER, SECONDARY_QUESTIONS, tierById, type BodyType } from '../../../mock-data/symptomCheckerTriage';
import { symptomById } from '../../../mock-data/symptomCheckerSymptoms';
import type { Assessment, SelectedSymptom } from '../../utils/symptomTriage';
import { useToast } from '../ui/Toast';
import { useLanguage } from '../../context/providers';
import { scT, scModelLabel } from '../../i18n/symptomChecker';

interface SymptomResultsProps {
  assessment: Assessment;
  selected: SelectedSymptom[];
  secondary: string[];
  notes?: string;
  model: BodyType;
  ageLabel?: string;
  onRestart: () => void;
  onEdit: () => void;
  onNavigate: (route: string) => void;
  aiConnected?: boolean;
  recommendedTests?: string[];
  aiLoading?: boolean;
}

export function SymptomResults({ assessment, selected, secondary, notes = '', model, ageLabel, onRestart, onEdit, onNavigate, aiConnected = false, recommendedTests = [], aiLoading = false }: SymptomResultsProps) {
  const { showToast } = useToast();
  const { language, t } = useLanguage();
  const L = (source: string, params?: Record<string, string | number>) => scT(language, source, params);
  const [tab, setTab] = useState<'advice' | 'watch' | 'help'>('advice');
  const [openGuide, setOpenGuide] = useState<string | null>(assessment.firstAid[0]?.id ?? null);
  const { tier } = assessment;
  const whoAge = ageLabel ?? assessment.ageLabel;
  const modelText = scModelLabel(language, model);

  const copySummary = async () => {
    const lines = [
      t('sc.res.copyHeader'),
      t('sc.res.person', { model: modelText, age: whoAge, band: assessment.ageBandLabel }),
      t('sc.res.symptomsHeader', {
        list: selected.map((s) =>
          t('sc.res.symptomItem', {
            label: L(symptomById(s.id)?.label ?? ''),
            d: s.durationDays,
            sev: s.severity,
          }),
        ).join('; '),
      }),
      notes.trim() ? t('sc.res.notesLine', { text: notes.trim() }) : null,
      t('sc.res.triage', { tier: L(tier.label) }),
      t('sc.res.likely', {
        list: assessment.conditions.map((c) => `${L(c.name)} ${c.score}%`).join(', ') || t('sc.res.noInfo'),
      }),
      t('sc.res.firstAidLine', {
        list: assessment.firstAid.map((f) => L(f.title)).join('; ') || t('sc.res.noneRequired'),
      }),
      L(DISCLAIMER),
    ].filter(Boolean) as string[];
    try {
      await navigator.clipboard.writeText(lines.join('\n'));
      showToast(t('sc.res.copied'));
    } catch {
      showToast(t('sc.res.copyFail'));
    }
  };

  return (
    <div className="space-y-5">
      {/* ---- Urgency banner ---- */}
      <motion.div
        initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
        className={`rounded-2xl border p-5 ${tier.bg} ${tier.border}`}
      >
        <div className="flex flex-col sm:flex-row sm:items-start gap-4">
          <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${tier.bar} text-white`}>
            {tier.level >= 90 ? <ShieldAlert size={24} /> : tier.level >= 65 ? <AlertTriangle size={24} /> : <BadgeCheck size={24} />}
          </div>
          <div className="flex-1">
            <p className={`text-[11px] font-bold uppercase tracking-[0.14em] ${tier.text}`}>
              {t('sc.res.urgencyMeta', { timeframe: L(tier.timeframe), model: modelText, age: whoAge })}
            </p>
            <h2 className={`mt-1 font-display text-xl font-bold ${tier.text}`}>{L(tier.label)}</h2>
            <p className="mt-1.5 text-sm text-ink-700 dark:text-slate-200">{L(tier.action)}</p>

            {/* urgency ladder */}
            <div className="mt-3 flex gap-1">
              {[10, 65, 90, 95, 100].map((lvl) => (
                <span key={lvl} className={`h-1.5 flex-1 rounded-full ${tier.level >= lvl ? tier.bar : 'bg-black/10'}`} />
              ))}
            </div>

            {assessment.reasons.length > 0 && (
              <ul className="mt-3 space-y-1">
                {assessment.reasons.map((r) => (
                  <li key={r} className="flex gap-2 text-xs text-ink-600 dark:text-slate-300">
                    <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${tier.bar}`} />{r}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {tier.level >= 90 && (
            <a href="tel:108" className="sahaay-btn-primary flex items-center gap-2 px-4 py-2 text-sm">
              <PhoneCall size={16} /> {t('sc.res.callNow')}
            </a>
          )}
          <button onClick={() => onNavigate('/patient/appointments')} className="sahaay-btn-primary flex items-center gap-2 px-4 py-2 text-sm">
            <Stethoscope size={16} /> {t('sc.res.book')}
          </button>
          <button onClick={() => onNavigate('/patient/facilities')}
            className="flex items-center gap-2 rounded-xl border border-sahaay-deep/15 bg-white/80 px-4 py-2 text-sm font-semibold text-ink-700 hover:bg-white">
            <MapPin size={16} /> {t('sc.res.findFacility')}
          </button>
          <button onClick={copySummary}
            className="flex items-center gap-2 rounded-xl border border-sahaay-deep/15 bg-white/80 px-4 py-2 text-sm font-semibold text-ink-700 hover:bg-white">
            <ClipboardCopy size={16} /> {t('sc.res.copySummary')}
          </button>
        </div>
      </motion.div>
      {/* ---- AI narrative + what was reported ---- */}
      <div className="grid gap-5 lg:grid-cols-3">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
          className="lg:col-span-2 glass-card-elevated p-5">
          <h3 className="flex items-center gap-2 text-sm font-bold text-ink-900 dark:text-slate-100">
            <Sparkles size={16} className="text-vital-nerve" /> {t('sc.res.aiAssessment')}
            <span className={`ml-auto inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-[9px] font-bold uppercase tracking-wider ${aiLoading ? 'bg-amber-50 text-amber-600' : aiConnected ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${aiLoading ? 'animate-pulse bg-amber-400' : aiConnected ? 'bg-emerald-500' : 'bg-slate-400'}`} />
              {aiLoading ? 'Analyzing' : aiConnected ? 'OpenAI analyzed' : 'Local triage'}
            </span>
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-ink-600 dark:text-slate-300">{assessment.summary}</p>
          {recommendedTests.length > 0 && (
            <div className="mt-4 rounded-xl border border-sky-200 bg-sky-50/70 p-3">
              <p className="text-[11px] font-bold uppercase tracking-wider text-sky-700">Suggested tests for clinician review</p>
              <ul className="mt-2 space-y-1.5">
                {recommendedTests.map(test => <li key={test} className="flex gap-2 text-xs text-sky-900"><span>•</span>{test}</li>)}
              </ul>
            </div>
          )}
          {assessment.redFlags.length > 0 && (
            <div className="mt-3 rounded-xl border border-rose-200 bg-rose-50/70 p-3">
              <p className="text-[11px] font-bold uppercase tracking-wider text-rose-700">{t('sc.res.confirmedFlags')}</p>
              <ul className="mt-1.5 space-y-1">
                {assessment.redFlags.map((f) => (
                  <li key={f.id} className="flex gap-2 text-xs text-rose-800">
                    <AlertTriangle size={12} className="mt-0.5 shrink-0" />{L(f.text)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-5">
          <h3 className="text-sm font-bold text-ink-900 dark:text-slate-100">{t('sc.res.whatReported')}</h3>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-sahaay-deep/10 px-2.5 py-1 text-[11px] font-bold text-sahaay-deep">
              <CalendarDays size={11} /> {modelText} · {whoAge} · {assessment.ageBandLabel}
            </span>
            {secondary.filter((id) => id !== 'infant').map((id) => {
              const q = SECONDARY_QUESTIONS.find((x) => x.id === id);
              return q ? (
                <span key={id} className="rounded-full bg-vital-sun/12 px-2.5 py-1 text-[11px] font-semibold text-vital-sun-ink">
                  {L(q.label)}
                </span>
              ) : null;
            })}
          </div>
          <ul className="mt-3 space-y-2">
            {selected.map((s) => {
              const symptom = symptomById(s.id);
              if (!symptom) return null;
              return (
                <li key={s.id} className="rounded-xl border border-sahaay-deep/10 bg-white/60 dark:bg-slate-800/50 p-2.5">
                  <p className="text-xs font-semibold text-ink-800 dark:text-slate-200">{L(symptom.label)}</p>
                  <p className="text-[11px] text-ink-400">
                    {s.durationDays === 0
                      ? t('sc.res.startedToday')
                      : t('sc.res.days', { n: s.durationDays, s: s.durationDays > 1 ? 's' : '' })}
                    {' · '}
                    {t('sc.res.severity', { n: s.severity })}
                    {s.flags.length > 0 && ` · ${t('sc.res.flagCount', { n: s.flags.length, s: s.flags.length > 1 ? 's' : '' })}`}
                  </p>
                </li>
              );
            })}
          </ul>
          {notes.trim() && (
            <div className="mt-3 rounded-xl border border-sahaay-deep/10 bg-white/60 dark:bg-slate-800/50 p-2.5">
              <p className="text-[11px] font-bold uppercase tracking-wider text-ink-400">{t('sc.res.notes')}</p>
              <p className="mt-1 whitespace-pre-wrap text-xs text-ink-700 dark:text-slate-300">{notes.trim()}</p>
            </div>
          )}
          <div className="mt-3 flex items-center gap-2">
            <button onClick={onEdit} className="text-xs font-semibold text-sahaay-deep hover:underline">{t('sc.res.edit')}</button>
            <button onClick={onRestart} className="ml-auto flex items-center gap-1 text-xs font-semibold text-ink-500 hover:text-ink-700">
              <RotateCcw size={12} /> {t('sc.startOver')}
            </button>
          </div>
        </motion.div>
      </div>

      {/* ---- First aid ---- */}
      {assessment.firstAid.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="rounded-2xl border border-rose-200/70 bg-white/70 dark:bg-slate-800/50 p-5">
          <h3 className="flex items-center gap-2 text-sm font-bold text-ink-900 dark:text-slate-100">
            <HeartPulse size={16} className="text-vital-pulse" /> {t('sc.res.firstAid')}
          </h3>
          <p className="mt-1 text-xs text-ink-500">
            {t('sc.res.firstAidDesc', { age: whoAge, band: assessment.ageBandLabel })}
          </p>
          <div className="mt-3 space-y-2">
            {assessment.firstAid.map((guide) => {
              const open = openGuide === guide.id;
              return (
                <div key={guide.id} className="overflow-hidden rounded-xl border border-sahaay-deep/10">
                  <button
                    onClick={() => setOpenGuide(open ? null : guide.id)}
                    className="flex w-full items-center justify-between gap-3 bg-white/70 dark:bg-slate-800/60 px-3.5 py-2.5 text-left"
                  >
                    <span className="flex items-center gap-2 text-xs font-bold text-ink-800 dark:text-slate-200">
                      <Flame size={13} className="text-vital-pulse" />{L(guide.title)}
                    </span>
                    <ChevronDown size={14} className={`shrink-0 text-ink-400 transition-transform ${open ? 'rotate-180' : ''}`} />
                  </button>
                  {open && (
                    <ol className="space-y-2 border-t border-sahaay-deep/8 bg-white/40 dark:bg-slate-900/40 px-4 py-3">
                      {guide.steps.map((step, i) => (
                        <li key={step} className="flex gap-2.5 text-xs text-ink-600 dark:text-slate-300">
                          <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-sahaay-deep/10 text-[10px] font-bold text-sahaay-deep">{i + 1}</span>
                          {L(step)}
                        </li>
                      ))}
                    </ol>
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>
      )}
      {/* ---- Likely conditions ---- */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card-elevated p-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="flex items-center gap-2 text-sm font-bold text-ink-900 dark:text-slate-100">
            <Stethoscope size={16} className="text-sahaay-deep" /> {t('sc.res.possible')}
          </h3>
          {assessment.specialist && (
            <span className="rounded-full bg-sahaay-deep/8 px-3 py-1 text-[11px] font-semibold text-sahaay-deep">
              {t('sc.res.suggested', { name: assessment.specialist })}
            </span>
          )}
        </div>

        {assessment.conditions.length === 0 ? (
          <p className="mt-3 text-sm text-ink-500">{t('sc.res.noConditions')}</p>
        ) : (
          <div className="mt-4 space-y-3">
            {assessment.conditions.map((c, i) => (
              <div key={c.name}>
                <div className="flex items-baseline justify-between gap-3">
                  <p className="text-sm font-semibold text-ink-800 dark:text-slate-200">
                    {i === 0 && <span className="mr-1.5 rounded bg-sahaay-deep/10 px-1.5 py-0.5 text-[10px] font-bold uppercase text-sahaay-deep">{t('sc.res.bestFit')}</span>}
                    {L(c.name)}
                    <span className="ml-2 font-mono text-[10px] text-ink-400">{t('sc.res.icd', { code: c.icd10 })}</span>
                  </p>
                  <span className="shrink-0 text-xs font-bold text-ink-600 dark:text-slate-300">{c.score}%</span>
                </div>
                <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-black/5 dark:bg-white/10">
                  <motion.div initial={{ width: 0 }} animate={{ width: `${c.score}%` }} transition={{ duration: 0.6, delay: 0.05 * i }}
                    className="h-full rounded-full bg-sahaay-deep" />
                </div>
                <p className="mt-1 text-[11px] text-ink-400">
                  {t('sc.res.matched', {
                    factors: c.factors.map((f) => L(f)).join(', '),
                    specialist: c.specialist,
                  })}
                </p>
              </div>
            ))}
          </div>
        )}
        <p className="mt-4 flex gap-2 rounded-xl bg-sahaay-surface px-3 py-2 text-[11px] text-ink-500">
          <Info size={13} className="mt-0.5 shrink-0" />
          {t('sc.res.percentNote')}
        </p>
      </motion.div>

      {/* ---- Care advice tabs ---- */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="glass-card-elevated p-5">
        <div className="flex flex-wrap gap-1.5">
          {([
            ['advice', t('sc.res.tabHome', { n: assessment.homeCare.length })],
            ['watch', t('sc.res.tabWatch', { n: assessment.watchFor.length })],
            ['help', t('sc.res.tabHelp')],
          ] as const).map(([id, label]) => (
            <button key={id} onClick={() => setTab(id)}
              className={`rounded-xl px-3.5 py-2 text-xs font-semibold transition-colors ${
                tab === id ? 'bg-sahaay-deep text-white' : 'bg-white/60 text-ink-600 hover:bg-white border border-sahaay-deep/10'
              }`}>{label}</button>
          ))}
        </div>

        {tab === 'advice' && (
          <ul className="mt-4 space-y-2">
            {assessment.homeCare.map((line) => (
              <li key={line} className="flex gap-2.5 text-sm text-ink-600 dark:text-slate-300">
                <BadgeCheck size={15} className="mt-0.5 shrink-0 text-sahaay-500" />{L(line)}
              </li>
            ))}
            {assessment.homeCare.length === 0 && <li className="text-sm text-ink-500">{t('sc.res.noHomeCare')}</li>}
          </ul>
        )}

        {tab === 'watch' && (
          <div className="mt-4 space-y-2">
            <p className="text-xs text-ink-500">{t('sc.res.watchIntro')}</p>
            {assessment.watchFor.map((f) => (
              <div key={f.id} className="flex items-start gap-2.5 rounded-xl border border-sahaay-deep/10 bg-white/60 dark:bg-slate-800/50 p-3">
                <AlertTriangle size={14} className="mt-0.5 shrink-0 text-amber-500" />
                <div>
                  <p className="text-xs font-semibold text-ink-800 dark:text-slate-200">{L(f.text)}</p>
                  <p className="text-[11px] text-ink-400">{t('sc.res.then', { tier: L(tierById(f.tier).label) })}</p>
                </div>
              </div>
            ))}
            {assessment.watchFor.length === 0 && <p className="text-sm text-ink-500">{t('sc.res.noWatch')}</p>}
          </div>
        )}

        {tab === 'help' && (
          <div className="mt-4 space-y-2 text-sm text-ink-600 dark:text-slate-300">
            <p className="font-semibold text-ink-800 dark:text-slate-200">{L(tier.label)}</p>
            <p>{L(tier.action)}</p>
            <ul className="mt-2 space-y-1.5 text-xs">
              <li>• {t('sc.res.helpAmbulance')} <strong>108</strong> · {t('sc.res.helpNational')} <strong>112</strong></li>
              <li>• {t('sc.res.helpMental')} <strong>Tele-MANAS 14416</strong></li>
              <li>• {t('sc.res.helpHelpline')} <strong>104</strong> · {t('sc.res.helpAsha')}</li>
              <li>• {t('sc.res.helpRerun')}</li>
            </ul>
          </div>
        )}
      </motion.div>

      <p className="flex gap-2 rounded-xl bg-amber-50/70 border border-amber-200/70 px-3.5 py-2.5 text-[11px] text-amber-800">
        <Info size={13} className="mt-0.5 shrink-0" />{L(DISCLAIMER)}
      </p>
    </div>
  );
}

