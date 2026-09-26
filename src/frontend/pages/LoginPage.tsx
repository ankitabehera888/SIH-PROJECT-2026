import { useId, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Heart, Eye, EyeOff, ArrowRight, ArrowLeft, Shield, Clock, Users, Building2, ChevronRight } from 'lucide-react';
import { HealthcareCarousel } from '../components/ui/HealthcareCarousel';
import { LanguageSelector } from '../components/ui/LanguageSelector';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { AuroraField } from '../components/fx/AuroraField';
import { SplitText } from '../components/fx/SplitText';
import { TiltCard } from '../components/fx/TiltCard';
import { useTimeGreeting } from '../hooks/useTimeGreeting';
import { useLanguage } from '../context/providers';

interface LoginPageProps {
  onNavigate: (route: string) => void;
}

/* All four destinations — patient, doctor, health worker and facility. */
const QUICK_ROLES = [
  { key: 'login.patient', icon: Users, route: '/patient/dashboard', tint: '#17B366' },
  { key: 'login.doctor', icon: Shield, route: '/doctor/dashboard', tint: '#0EA5C9' },
  { key: 'login.worker', icon: Clock, route: '/worker/dashboard', tint: '#F59E0B' },
  { key: 'login.facility', icon: Building2, route: '/facility/dashboard', tint: '#7C5CFF' },
];

/** Accepts an email or an Indian mobile number — the field takes either. */
function looksLikeIdentifier(value: string) {
  const v = value.trim();
  return /^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(v) || /^(\+91[\s-]?)?[6-9]\d{9}$/.test(v.replace(/[\s-]/g, ''));
}

export function LoginPage({ onNavigate }: LoginPageProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [touched, setTouched] = useState(false);
  /* No credential fields until a role is picked. Null = show the three large
     role shortcuts; a role = show the form bound to that role's destination. */
  const [selectedRole, setSelectedRole] = useState<(typeof QUICK_ROLES)[number] | null>(null);
  const { t } = useLanguage();
  const { greeting, Icon: TimeIcon, tint } = useTimeGreeting();
  const reduce = useReducedMotion();

  // Stable, unique ids so every label is genuinely associated with its input.
  // The previous markup used bare <label> elements, which look right but do not
  // move focus on click and are not announced as the field's name.
  const uid = useId();
  const emailId = `${uid}-identifier`;
  const passwordId = `${uid}-password`;
  const emailErrorId = `${uid}-identifier-error`;
  const rememberId = `${uid}-remember`;

  /* Advisory only. It fires on a value that cannot possibly be a mobile number
     or an email, and it never blocks submission — the demo has no backend, and
     gating the button would break the one path a reviewer actually clicks. */
  const identifierWarning = touched && email.trim().length > 0 && !looksLikeIdentifier(email);

  return (
    <div className="flex min-h-screen">
      {/* ── Form side ──────────────────────────────────────────────────── */}
      <div className="sahaay-page-bg relative flex flex-1 items-center justify-center overflow-hidden p-6 lg:p-12">
        {/* Back to landing page */}
        <button
          onClick={() => onNavigate('/')}
          aria-label="Back to landing page"
          className="glass-card absolute left-4 top-4 z-20 flex items-center gap-1.5 rounded-xl px-3 py-2 text-sm font-semibold text-ink-500 transition-colors hover:text-sahaay-deep lg:left-6 lg:top-6"
        >
          <ArrowLeft size={15} />
          Back
        </button>
        {/* The three faded Unsplash photos that used to sit here failed to load
            whenever the network could not reach images.unsplash.com, leaving
            blank rectangles. This field is CSS only, so it renders offline. */}
        <AuroraField intensity={0.7} />
        <div aria-hidden="true" className="grid-paper pointer-events-none absolute inset-0 opacity-60" />
        <span aria-hidden="true" className="holo-line absolute inset-x-0 top-0 h-[2px]" />

        <motion.div
          initial={reduce ? { opacity: 0 } : { opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="relative z-10 w-full max-w-md"
        >
          {/* Logo + language */}
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sahaay-deep to-sahaay-600">
                {!reduce && (
                  <span
                    aria-hidden="true"
                    className="animate-halo absolute inset-0 rounded-xl"
                    style={{ boxShadow: '0 0 0 1px rgba(23,179,102,0.55)' }}
                  />
                )}
                <Heart size={20} className="relative text-white" fill="currentColor" />
              </span>
              <span className="font-display text-2xl font-bold tracking-tight text-sahaay-deep">SAHAAY</span>
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <LanguageSelector />
            </div>
          </div>

          {/* Live greeting — the same clock-driven band used on the dashboards */}
          <span
            className="mb-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-mono text-[10px] font-bold uppercase tracking-[0.16em]"
            style={{ color: tint, background: `${tint}14`, boxShadow: `inset 0 0 0 1px ${tint}33` }}
          >
            <TimeIcon size={12} />
            {greeting}
          </span>

          {/* Split by words, never by characters: two of the three locales are
              Devanagari, where a per-glyph split breaks conjuncts and matras. */}
          <SplitText
            as="h1"
            by="words"
            immediate
            text={t('login.welcome')}
            className="font-display text-[26px] font-bold leading-[1.2] tracking-tight text-ink-900 lg:text-[32px]"
            stagger={0.06}
          />
          <p className="mb-8 mt-2 text-ink-500">{t('login.subtitle')}</p>

          {!selectedRole ? (
            /* ── Role shortcuts: large, bold, centred. Credentials stay hidden
                 until one of these is picked. */
            <div className="flex flex-col gap-4">
              {QUICK_ROLES.map((role, i) => {
                const Icon = role.icon;
                return (
                  <motion.div
                    key={role.route}
                    initial={reduce ? { opacity: 0 } : { opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 + i * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                  >
                    <TiltCard
                      as="button"
                      strength={8}
                      lift={14}
                      onClick={() => setSelectedRole(role)}
                      ariaLabel={`${t('login.submit')} ${t(role.key)}`}
                      className="glass-card group flex min-h-[104px] w-full items-center justify-center gap-4 p-5 text-center"
                    >
                      <span
                        aria-hidden="true"
                        className="flex h-14 w-14 items-center justify-center rounded-2xl transition-transform duration-300 group-hover:scale-110"
                        style={{ color: role.tint, background: `${role.tint}1A`, boxShadow: `inset 0 0 0 1px ${role.tint}2E` }}
                      >
                        <Icon size={28} />
                      </span>
                      <span className="font-display text-2xl font-bold tracking-tight text-ink-900">
                        {t(role.key)}
                      </span>
                      <ArrowRight
                        size={22}
                        aria-hidden="true"
                        className="text-ink-400 transition-all duration-300 group-hover:translate-x-1 group-hover:text-sahaay-deep"
                      />
                    </TiltCard>
                  </motion.div>
                );
              })}
            </div>
          ) : (
          <>
            {/* Selected role banner — one tap goes back to the shortcuts. */}
            <button
              type="button"
              onClick={() => setSelectedRole(null)}
              className="mb-5 flex items-center gap-2 text-sm font-semibold text-ink-500 transition-colors hover:text-sahaay-deep"
            >
              <ArrowLeft size={15} />
              {t(selectedRole.key)} — change role
            </button>

          {/* ── Form ─────────────────────────────────────────────────── */}
          <form onSubmit={(e) => e.preventDefault()} className="space-y-5">
            <div>
              <label htmlFor={emailId} className="mb-1.5 block text-sm font-semibold text-ink-700">
                {t('login.email')}
              </label>
              <input
                id={emailId}
                type="text"
                inputMode="email"
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={() => setTouched(true)}
                placeholder={t('login.emailPlaceholder')}
                aria-invalid={identifierWarning || undefined}
                aria-describedby={identifierWarning ? emailErrorId : undefined}
                className="sahaay-input"
                style={identifierWarning ? { borderColor: 'rgba(255,77,109,0.55)' } : undefined}
              />
              {/* The message sits under the field it belongs to, not in a
                  summary at the top of the form. */}
              {identifierWarning && (
                <motion.p
                  id={emailErrorId}
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-1.5 text-xs font-medium text-vital-pulse-ink"
                >
                  That doesn't look like a mobile number or an email address yet.
                </motion.p>
              )}
            </div>

            <div>
              <label htmlFor={passwordId} className="mb-1.5 block text-sm font-semibold text-ink-700">
                {t('login.password')}
              </label>
              <div className="relative">
                <input
                  id={passwordId}
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t('login.passwordPlaceholder')}
                  className="sahaay-input pr-14"
                />
                {/* 44×44 target, and it says what it does — the old 18px icon
                    had neither a label nor a usable tap area. */}
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  aria-pressed={showPassword}
                  className="absolute right-1 top-1/2 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-lg text-ink-400 transition-colors hover:bg-sahaay-500/10 hover:text-ink-700"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
              <label
                htmlFor={rememberId}
                className="flex cursor-pointer items-center gap-2 py-2.5 text-ink-600"
              >
                <input
                  id={rememberId}
                  type="checkbox"
                  className="h-4 w-4 rounded border-ink-200 accent-sahaay-deep"
                />
                {t('login.remember')}
              </label>
              <button
                type="button"
                className="rounded-lg px-1 py-2.5 font-semibold text-sahaay-deep hover:underline"
              >
                {t('login.forgot')}
              </button>
            </div>

            <button
              onClick={() => onNavigate(selectedRole.route)}
              className="sahaay-btn-primary group flex min-h-[48px] w-full items-center justify-center gap-2 text-base"
            >
              {t('login.submit')}
              <ArrowRight size={18} className="transition-transform duration-300 group-hover:translate-x-1" />
            </button>
          </form>
          </>
          )}

          <p className="mt-6 flex flex-wrap items-center justify-center gap-1 text-center text-xs text-ink-400">
            {t('login.needHelp')}
            <button className="inline-flex items-center gap-0.5 font-semibold text-sahaay-deep hover:underline">
              {t('login.contactSupport')}
              <ChevronRight size={12} />
            </button>
          </p>

          <p className="mt-4 border-t border-ink-200/40 pt-4 text-center text-sm text-ink-500">
            New to SAHAAY?{' '}
            <button
              onClick={() => onNavigate('/signup')}
              className="inline-flex items-center gap-0.5 font-semibold text-sahaay-deep hover:underline"
            >
              Create an account
              <ArrowRight size={13} />
            </button>
          </p>
        </motion.div>
      </div>

      {/* ── Carousel side ──────────────────────────────────────────────── */}
      <div className="relative hidden flex-1 lg:block">
        <HealthcareCarousel variant="login" />
      </div>
    </div>
  );
}
