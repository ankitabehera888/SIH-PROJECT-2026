import { useId, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Heart, Eye, EyeOff, ArrowRight, ArrowLeft, ShieldCheck, User, Stethoscope, Users, Building2, CheckCircle2 } from 'lucide-react';
import { AuroraField } from '../components/fx/AuroraField';
import { LanguageSelector } from '../components/ui/LanguageSelector';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { useToast } from '../components/ui/Toast';
import { useLanguage } from '../context/providers';
import { useUserProfile, type Role } from '../context/providers';

interface SignUpPageProps {
  onNavigate: (route: string) => void;
}

const ROLE_OPTIONS: { role: Role; label: string; blurb: string; icon: typeof User; tint: string; home: string }[] = [
  { role: 'patient', label: 'Patient', blurb: 'Track your own care', icon: User, tint: '#17B366', home: '/patient/dashboard' },
  { role: 'doctor', label: 'Doctor', blurb: 'Consult and refer', icon: Stethoscope, tint: '#0EA5C9', home: '/doctor/dashboard' },
  { role: 'worker', label: 'Health Worker', blurb: 'Field registration', icon: Users, tint: '#7C5CFF', home: '/worker/dashboard' },
  { role: 'facility', label: 'Facility', blurb: 'Operate the centre', icon: Building2, tint: '#F59E0B', home: '/facility/dashboard' },
];

const looksLikeEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value.trim());
const looksLikePhone = (value: string) => /^[+]?[\d\s-]{10,15}$/.test(value.trim());
/* Ayushman Bharat (ABHA) card numbers are 14 digits. */
const looksLikeAyushman = (value: string) => /^\d{14}$/.test(value.replace(/[\s-]/g, ''));

export function SignUpPage({ onNavigate }: SignUpPageProps) {
  const { t } = useLanguage();
  const { showToast } = useToast();
  const { updateProfileFor } = useUserProfile();
  const reduce = useReducedMotion();
  const uid = useId();

  const [role, setRole] = useState<Role>('patient');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [hasAyushman, setHasAyushman] = useState(false);
  const [ayushmanNumber, setAyushmanNumber] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const selected = ROLE_OPTIONS.find((o) => o.role === role)!;

  const validate = () => {
    const next: Record<string, string> = {};
    if (fullName.trim().length < 3) next.fullName = 'Enter your full name (at least 3 characters).';
    if (!looksLikeEmail(email)) next.email = 'Enter a valid email address.';
    if (!looksLikePhone(phone)) next.phone = 'Enter a valid 10-digit mobile number.';
    if (password.length < 6) next.password = 'Use at least 6 characters.';
    if (password !== confirm) next.confirm = 'Passwords do not match.';
    if (hasAyushman && !looksLikeAyushman(ayushmanNumber))
      next.ayushmanNumber = 'Enter your 14-digit Ayushman card number.';
    if (!agreed) next.agreed = 'Please accept the terms to continue.';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    /* The account's identity is written into that role's profile, so the
       dashboard, topbar and settings all greet the new user by name. */
    updateProfileFor(role, { fullName: fullName.trim(), email: email.trim(), phone: phone.trim() });
    showToast(hasAyushman
      ? `Account created with Ayushman benefits — welcome, ${fullName.trim().split(/\s+/)[0]}`
      : `Account created — welcome, ${fullName.trim().split(/\s+/)[0]}`);
    onNavigate(selected.home);
  };

  const fieldClass = (key: string) =>
    `sahaay-input ${errors[key] ? 'border-rose-400 focus:border-rose-400' : ''}`;


  return (
    <div className="sahaay-page-bg relative flex min-h-screen items-center justify-center overflow-hidden p-4 lg:p-8">
      <AuroraField intensity={0.6} />
      <div aria-hidden="true" className="grid-paper pointer-events-none absolute inset-0 opacity-50" />
      <span aria-hidden="true" className="holo-line absolute inset-x-0 top-0 h-[2px]" />

      <motion.div
        initial={reduce ? { opacity: 0 } : { opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-2xl"
      >
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => onNavigate('/login')}
            className="flex items-center gap-1.5 text-sm font-semibold text-ink-500 transition-colors hover:text-sahaay-deep"
          >
            <ArrowLeft size={15} /> Back to login
          </button>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <LanguageSelector />
          </div>
        </div>

        <div className="glass-card-elevated p-6 lg:p-8">
          <div className="mb-6 flex items-center gap-2.5">
            <span className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sahaay-deep to-sahaay-600">
              <Heart size={20} className="relative text-white" fill="currentColor" />
            </span>
            <div>
              <p className="font-display text-xl font-bold tracking-tight text-sahaay-deep">Create your SAHAAY account</p>
              <p className="text-xs text-ink-500">One platform, four kinds of access.</p>
            </div>
          </div>

          <form onSubmit={submit} className="space-y-5" noValidate>
            {/* Role picker */}
            <fieldset>
              <legend className="mb-2 text-xs font-semibold text-ink-600">I am signing up as</legend>
              <div className="grid grid-cols-2 gap-2 lg:grid-cols-4">
                {ROLE_OPTIONS.map((option) => {
                  const Icon = option.icon;
                  const active = option.role === role;
                  return (
                    <button
                      key={option.role}
                      type="button"
                      onClick={() => setRole(option.role)}
                      aria-pressed={active}
                      className={`flex flex-col items-start gap-1.5 rounded-xl border p-3 text-left transition-all ${
                        active ? 'border-sahaay-deep bg-sahaay-deep/6' : 'border-ink-200/60 hover:bg-white/60'
                      }`}
                    >
                      <span
                        aria-hidden="true"
                        className="flex h-8 w-8 items-center justify-center rounded-lg"
                        style={{ color: option.tint, background: `${option.tint}1A`, boxShadow: `inset 0 0 0 1px ${option.tint}2E` }}
                      >
                        <Icon size={16} />
                      </span>
                      <span className="text-xs font-bold text-ink-800">{option.label}</span>
                      <span className="text-[10px] leading-tight text-ink-500">{option.blurb}</span>
                    </button>
                  );
                })}
              </div>
            </fieldset>

            {/* Identity */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor={`${uid}-name`} className="mb-1.5 block text-xs font-semibold text-ink-600">Full name</label>
                <input
                  id={`${uid}-name`}
                  type="text"
                  value={fullName}
                  onChange={(e) => { setFullName(e.target.value); setErrors((p) => ({ ...p, fullName: '' })); }}
                  placeholder={role === 'doctor' ? 'Dr. Ananya Sharma' : 'Your full name'}
                  aria-invalid={!!errors.fullName}
                  className={fieldClass('fullName')}
                />
                {errors.fullName && <p className="mt-1 text-xs font-medium text-rose-600">{errors.fullName}</p>}
              </div>
              <div>
                <label htmlFor={`${uid}-email`} className="mb-1.5 block text-xs font-semibold text-ink-600">Email</label>
                <input
                  id={`${uid}-email`}
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setErrors((p) => ({ ...p, email: '' })); }}
                  placeholder="you@example.com"
                  aria-invalid={!!errors.email}
                  className={fieldClass('email')}
                />
                {errors.email && <p className="mt-1 text-xs font-medium text-rose-600">{errors.email}</p>}
              </div>
            </div>


            {/* Credentials */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor={`${uid}-phone`} className="mb-1.5 block text-xs font-semibold text-ink-600">Mobile number</label>
                <input
                  id={`${uid}-phone`}
                  type="tel"
                  value={phone}
                  onChange={(e) => { setPhone(e.target.value); setErrors((p) => ({ ...p, phone: '' })); }}
                  placeholder="+91 98765 43210"
                  aria-invalid={!!errors.phone}
                  className={fieldClass('phone')}
                />
                {errors.phone && <p className="mt-1 text-xs font-medium text-rose-600">{errors.phone}</p>}
              </div>
              <div>
                <label htmlFor={`${uid}-password`} className="mb-1.5 block text-xs font-semibold text-ink-600">Password</label>
                <div className="relative">
                  <input
                    id={`${uid}-password`}
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => { setPassword(e.target.value); setErrors((p) => ({ ...p, password: '' })); }}
                    placeholder="At least 6 characters"
                    aria-invalid={!!errors.password}
                    className={`${fieldClass('password')} pr-11`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-400 transition-colors hover:text-ink-700"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {errors.password && <p className="mt-1 text-xs font-medium text-rose-600">{errors.password}</p>}
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor={`${uid}-confirm`} className="mb-1.5 block text-xs font-semibold text-ink-600">Confirm password</label>
                <input
                  id={`${uid}-confirm`}
                  type={showPassword ? 'text' : 'password'}
                  value={confirm}
                  onChange={(e) => { setConfirm(e.target.value); setErrors((p) => ({ ...p, confirm: '' })); }}
                  placeholder="Re-enter your password"
                  aria-invalid={!!errors.confirm}
                  className={fieldClass('confirm')}
                />
                {errors.confirm && <p className="mt-1 text-xs font-medium text-rose-600">{errors.confirm}</p>}
              </div>
              <div className="flex items-end">
                <p className="flex items-center gap-1.5 text-xs text-ink-500">
                  <CheckCircle2 size={13} className="text-sahaay-deep" />
                  {selected.label} access · sign in anytime
                </p>
              </div>
            </div>

            {/* Ayushman Bharat card — optional, but required if claimed */}
            <fieldset>
              <legend className="mb-2 text-xs font-semibold text-ink-600">Do you have an Ayushman Bharat card?</legend>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { value: false, label: 'No' },
                  { value: true, label: 'Yes — I have a card' },
                ].map((option) => {
                  const active = hasAyushman === option.value;
                  return (
                    <button
                      key={option.label}
                      type="button"
                      onClick={() => {
                        setHasAyushman(option.value);
                        if (!option.value) setErrors((p) => ({ ...p, ayushmanNumber: '' }));
                      }}
                      aria-pressed={active}
                      className={`rounded-xl border p-3 text-sm font-bold transition-all ${
                        active ? 'border-sahaay-deep bg-sahaay-deep/6 text-sahaay-deep' : 'border-ink-200/60 text-ink-600 hover:bg-white/60'
                      }`}
                    >
                      {option.label}
                    </button>
                  );
                })}
              </div>
              {hasAyushman && (
                <div className="mt-4">
                  <label htmlFor={`${uid}-ayushman`} className="mb-1.5 block text-xs font-semibold text-ink-600">
                    Ayushman card number
                  </label>
                  <input
                    id={`${uid}-ayushman`}
                    type="text"
                    inputMode="numeric"
                    autoComplete="off"
                    value={ayushmanNumber}
                    onChange={(e) => { setAyushmanNumber(e.target.value); setErrors((p) => ({ ...p, ayushmanNumber: '' })); }}
                    placeholder="14-digit number on your Ayushman card"
                    aria-invalid={!!errors.ayushmanNumber}
                    className={fieldClass('ayushmanNumber')}
                  />
                  {errors.ayushmanNumber ? (
                    <p className="mt-1 text-xs font-medium text-rose-600">{errors.ayushmanNumber}</p>
                  ) : (
                    <p className="mt-1 flex items-center gap-1.5 text-xs text-ink-500">
                      <CheckCircle2 size={13} className="text-sahaay-deep" />
                      Linking your card unlocks Ayushman Bharat benefits on SAHAAY.
                    </p>
                  )}
                </div>
              )}
            </fieldset>

            {/* Terms */}
            <div>
              <label htmlFor={`${uid}-terms`} className="flex items-start gap-2.5 text-xs text-ink-600">
                <input
                  id={`${uid}-terms`}
                  type="checkbox"
                  checked={agreed}
                  onChange={(e) => { setAgreed(e.target.checked); setErrors((p) => ({ ...p, agreed: '' })); }}
                  className="mt-0.5 h-4 w-4 rounded border-ink-200 accent-sahaay-deep"
                />
                <span>
                  I agree to the SAHAAY terms of use and consent to my health data being processed for care coordination.
                </span>
              </label>
              {errors.agreed && <p className="mt-1 text-xs font-medium text-rose-600">{errors.agreed}</p>}
            </div>

            <button type="submit" className="sahaay-btn-primary group flex min-h-[48px] w-full items-center justify-center gap-2 text-base">
              Create account
              <ArrowRight size={18} className="transition-transform duration-300 group-hover:translate-x-1" />
            </button>
          </form>

          <p className="mt-4 flex items-center justify-center gap-1.5 text-center text-xs text-ink-400">
            <ShieldCheck size={13} /> Demo sign-up — no data leaves your browser
          </p>

          <p className="mt-4 text-center text-sm text-ink-500">
            Already registered?{' '}
            <button onClick={() => onNavigate('/login')} className="font-semibold text-sahaay-deep hover:underline">
              {t('nav.login')}
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
