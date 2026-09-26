import { useEffect, useRef, useState } from 'react';
import {
  motion,
  useScroll,
  useTransform,
  useSpring,
  useMotionValue,
  useMotionValueEvent,
  useReducedMotion,
} from 'framer-motion';
import {
  Heart, ArrowRight, Shield, Users, Stethoscope, Activity, Building2, Pill,
  FileText, Clock, Play, Star, Quote, MapPin, Phone, ScanLine, Video,
  Sparkles, Menu, X,
} from 'lucide-react';
import { HealthcareCarousel } from '../components/ui/HealthcareCarousel';
import { LanguageSelector } from '../components/ui/LanguageSelector';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { useLanguage } from '../context/providers';

import { Reveal } from '../components/fx/Reveal';
import { SplitText } from '../components/fx/SplitText';
import { Counter } from '../components/fx/Counter';
import { TiltCard } from '../components/fx/TiltCard';
import { AuroraField } from '../components/fx/AuroraField';
import { Marquee3D } from '../components/fx/Marquee3D';
import { VitalsCanvas } from '../components/fx/VitalsCanvas';
import { CareCorridor, type CorridorStage } from '../components/fx/CareCorridor';
import { OrbitRing, type OrbitItem } from '../components/fx/OrbitRing';
import { ScrollSpine } from '../components/fx/ScrollSpine';

interface LandingPageProps {
  onNavigate: (route: string) => void;
}

/* ── Hero pointer parallax ─────────────────────────────────────────────────
   Returns two springs in the range [-1, 1] tracking the pointer across the
   viewport. Stays at rest for touch and reduced-motion users.            */
function usePointerParallax(disabled: boolean) {
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 60, damping: 20, mass: 0.6 });
  const sy = useSpring(my, { stiffness: 60, damping: 20, mass: 0.6 });

  useEffect(() => {
    if (disabled) return;
    const onMove = (e: PointerEvent) => {
      if (e.pointerType !== 'mouse') return;
      mx.set((e.clientX / window.innerWidth) * 2 - 1);
      my.set((e.clientY / window.innerHeight) * 2 - 1);
    };
    window.addEventListener('pointermove', onMove, { passive: true });
    return () => window.removeEventListener('pointermove', onMove);
  }, [disabled, mx, my]);

  return { sx, sy };
}

export function LandingPage({ onNavigate }: LandingPageProps) {
  const { t } = useLanguage();
  const reduce = useReducedMotion();
  const heroRef = useRef<HTMLDivElement>(null);
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  /* Hero scroll parallax — unchanged behaviour, deeper travel */
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] });
  const heroImageY = useTransform(scrollYProgress, [0, 1], [0, 110]);
  const heroImageScale = useTransform(scrollYProgress, [0, 1], [1, 1.16]);
  const heroContentY = useTransform(scrollYProgress, [0, 1], [0, -70]);
  const heroFade = useTransform(scrollYProgress, [0, 0.85], [1, 0]);

  /* Global scroll progress for the nav hairline */
  const { scrollYProgress: pageProgress, scrollY } = useScroll();
  const navBar = useSpring(pageProgress, { stiffness: 140, damping: 30, mass: 0.3 });

  useMotionValueEvent(scrollY, 'change', (v) => setScrolled(v > 24));

  const { sx, sy } = usePointerParallax(Boolean(reduce));
  const tiltY = useTransform(sx, [-1, 1], [10, -10]);
  const tiltX = useTransform(sy, [-1, 1], [-7, 7]);
  const floatX = useTransform(sx, [-1, 1], [26, -26]);
  const floatY = useTransform(sy, [-1, 1], [18, -18]);

  /* ── Data ──────────────────────────────────────────────────────────────── */

  const journeySteps = [
    { icon: Users, label: 'Patient', desc: 'Registration & intake' },
    { icon: Stethoscope, label: 'PHC', desc: 'Primary assessment' },
    { icon: Heart, label: 'Doctor', desc: 'Consultation' },
    { icon: Shield, label: 'Referral', desc: 'Coordination' },
    { icon: Activity, label: 'Diagnostics', desc: 'Tests & reports' },
    { icon: Pill, label: 'Pharmacy', desc: 'Medicine' },
    { icon: FileText, label: 'Records', desc: 'Health timeline' },
    { icon: Clock, label: 'Follow-up', desc: 'Continued care' },
  ];

  /* Same eight stages, now flown through in 3D. */
  const corridorStages: CorridorStage[] = [
    { icon: Users,       label: 'Patient',     desc: 'Registration & intake — one identity across every facility, village to city.', metric: 'intake · 90 sec', accent: 'emerald' },
    { icon: Stethoscope, label: 'PHC',         desc: 'Primary assessment at the nearest health centre, with vitals captured on device.', metric: 'avg wait · 12 min', accent: 'emerald' },
    { icon: Heart,       label: 'Doctor',      desc: 'Consultation opens with the full history already on screen — no retelling.', metric: 'history · 0 sec load', accent: 'pulse' },
    { icon: Shield,      label: 'Referral',    desc: 'Coordination to a specialist, tracked end to end instead of over the phone.', metric: 'no phone calls', accent: 'nerve' },
    { icon: ScanLine,    label: 'Diagnostics', desc: 'Tests & reports attach straight to the record the moment they are ready.', metric: 'reports · auto-linked', accent: 'oxy' },
    { icon: Pill,        label: 'Pharmacy',    desc: 'Medicine dispensed against the live prescription, with stock visibility.', metric: 'stock · live', accent: 'oxy' },
    { icon: FileText,    label: 'Records',     desc: 'A single health timeline the patient owns and can carry anywhere.', metric: 'patient-owned', accent: 'emerald' },
    { icon: Clock,       label: 'Follow-up',   desc: 'Continued care with reminders that reach the worker and the household.', metric: 'adherence · +34%', accent: 'nerve' },
  ];

  const roleRing: OrbitItem[] = [
    {
      icon: Users, title: 'Patient', accent: 'emerald',
      subtitle: 'Own your health timeline',
      points: ['Vitals, records & reports', 'Book appointments', 'AI symptom checker'],
      ctaLabel: 'Open patient view', route: '/patient/dashboard',
    },
    {
      icon: Stethoscope, title: 'Doctor', accent: 'pulse',
      subtitle: 'Full context before you speak',
      points: ['Patient history at a glance', 'Referrals & follow-ups', 'Video consultation'],
      ctaLabel: 'Open clinical view', route: '/doctor/dashboard',
    },
    {
      icon: Activity, title: 'Health Worker', accent: 'nerve',
      subtitle: 'The field, coordinated',
      points: ['Household visit lists', 'Facility referrals', 'Offline-first capture'],
      ctaLabel: 'Open field view', route: '/worker/dashboard',
    },
    {
      icon: Building2, title: 'Facility', accent: 'oxy',
      subtitle: 'Operations you can see',
      points: ['Bed & queue status', 'Incoming referrals', 'Resource planning'],
      ctaLabel: 'Open facility view', route: '/facility/dashboard',
    },
  ];

  const features = [
    { icon: Shield, title: t('features.connectedCare'), desc: t('features.connectedCareDesc'), image: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&h=600&fit=crop&auto=format' },
    { icon: Users, title: t('features.humanCentered'), desc: t('features.humanCenteredDesc'), image: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=800&h=600&fit=crop&auto=format' },
    { icon: Activity, title: t('features.continuity'), desc: t('features.continuityDesc'), image: 'https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&h=600&fit=crop&auto=format' },
    { icon: Building2, title: t('features.facilityCoord'), desc: t('features.facilityCoordDesc'), image: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&h=600&fit=crop&auto=format' },
  ];

  /* Values split from their display strings so they can count up. */
  const impactStats = [
    { to: 50, suffix: 'K+', label: t('impact.patients'), image: 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=600&h=400&fit=crop&auto=format' },
    { to: 200, suffix: '+', label: t('impact.facilities'), image: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600&h=400&fit=crop&auto=format' },
    { to: 1000, suffix: '+', label: t('impact.doctors'), image: 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=600&h=400&fit=crop&auto=format' },
  ];

  const testimonials = [
    {
      name: 'Priya Sharma',
      role: 'Community Health Worker, Raipur',
      text: 'SAHAAY has transformed how I coordinate care for my patients. No more phone calls to track referrals.',
      avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=120&h=120&fit=crop&auto=format',
    },
    {
      name: 'Dr. Rajesh Kumar',
      role: 'General Physician, PHC Chandrapur',
      text: 'I can see the full patient history before consultation. This saves time and improves diagnosis quality.',
      avatar: 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=120&h=120&fit=crop&auto=format',
    },
    {
      name: 'Anita Devi',
      role: 'Patient, Nagpur',
      text: 'My mother\'s treatment records are always available. We don\'t have to carry papers to every visit anymore.',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=120&h=120&fit=crop&auto=format',
    },
  ];

  const galleryImages = [
    { src: 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=700&h=500&fit=crop&auto=format', alt: 'Medical consultation', span: 'col-span-2 row-span-2' },
    { src: 'https://images.unsplash.com/photo-1581056771107-24ca5f033842?w=500&h=300&fit=crop&auto=format', alt: 'Healthcare technology', span: 'col-span-1 row-span-1' },
    { src: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=500&h=300&fit=crop&auto=format', alt: 'Hospital building', span: 'col-span-1 row-span-1' },
    { src: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=500&h=600&fit=crop&auto=format', alt: 'Medical equipment', span: 'col-span-1 row-span-2' },
    { src: 'https://images.unsplash.com/photo-1584515933487-779824d29309?w=500&h=300&fit=crop&auto=format', alt: 'Nurse with patient', span: 'col-span-1 row-span-1' },
    { src: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=500&h=300&fit=crop&auto=format', alt: 'Pharmacy', span: 'col-span-1 row-span-1' },
  ];

  /* Live readouts that float around the hero console. */
  const vitalChips = [
    { label: 'Heart rate', value: '72', unit: 'bpm', tone: '#C41E3F', bg: 'rgba(255,77,109,0.12)', pos: 'left-[-8%] top-[14%]', z: 90 },
    { label: 'SpO₂', value: '98', unit: '%', tone: '#076A82', bg: 'rgba(14,165,201,0.12)', pos: 'right-[-6%] top-[34%]', z: 130 },
    { label: 'Referrals today', value: '14', unit: 'open', tone: '#5533DB', bg: 'rgba(124,92,255,0.12)', pos: 'left-[-4%] bottom-[10%]', z: 60 },
  ];

  const trustItems = [
    'District Hospital · Raipur', 'PHC Chandrapur', 'Sub-centre Dhamtari',
    'CHC Bhilai', 'Wellness Centre Durg', 'Rural PHC Mahasamund',
    'District Hospital · Nagpur', 'PHC Kanker',
  ];

  const spineSections = [
    { id: 'hero', label: 'Start' },
    { id: 'journey', label: 'Journey' },
    { id: 'features', label: 'Platform' },
    { id: 'roles', label: 'Roles' },
    { id: 'impact', label: 'Impact' },
    { id: 'voices', label: 'Voices' },
    { id: 'about', label: 'About' },
  ];

  const navLinks = [
    { href: '#features', label: t('nav.features') },
    { href: '#journey', label: t('nav.howItWorks') },
    { href: '#impact', label: t('nav.impact') },
    { href: '#about', label: t('nav.about') },
  ];

  return (
    /* overflow-x-clip (not hidden) so the sticky care corridor still pins */
    <div className="min-h-screen bg-sahaay-surface overflow-x-clip">
      <ScrollSpine sections={spineSections} />

      {/* ═══════════════════ NAV ═══════════════════ */}
      <nav
        className={`fixed left-0 right-0 top-0 z-50 border-b transition-all duration-500 ${
          scrolled
            ? 'border-sahaay-deep/8 bg-white/80 shadow-[var(--shadow-1)] backdrop-blur-2xl'
            : 'border-transparent bg-white/50 backdrop-blur-xl'
        }`}
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-8">
          <a href="#hero" className="group flex items-center gap-2.5">
            <span className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-sahaay-deep to-sahaay-600 shadow-[0_4px_12px_rgba(14,79,58,0.28)]">
              <span
                aria-hidden="true"
                className="animate-halo absolute inset-0 rounded-xl"
                style={{ background: 'rgba(23,179,102,0.35)' }}
              />
              <Heart size={18} className="relative text-white" fill="white" />
            </span>
            <span className="font-display text-xl font-bold tracking-tight text-sahaay-deep">
              SAHAAY
            </span>
          </a>

          <div className="hidden items-center gap-8 md:flex">
            {navLinks.map((l) => (
              <a
                key={l.href}
                href={l.href}
                className="relative text-sm font-medium text-ink-500 transition-colors hover:text-sahaay-deep
                           after:absolute after:-bottom-1.5 after:left-0 after:h-[2px] after:w-0 after:rounded-full
                           after:bg-sahaay-500 after:transition-all after:duration-300 hover:after:w-full"
              >
                {l.label}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <LanguageSelector />
            <ThemeToggle />
            <button
              onClick={() => onNavigate('/login')}
              className="hidden rounded-xl px-4 py-2 text-sm font-semibold text-sahaay-deep transition-colors hover:bg-sahaay-deep/6 sm:block"
            >
              {t('nav.login')}
            </button>
            <button
              onClick={() => onNavigate('/signup')}
              className="sahaay-btn-primary whitespace-nowrap px-3.5 py-2.5 text-xs sm:px-5 sm:text-sm"
            >
              {t('nav.getStarted')}
            </button>
            <button
              onClick={() => setMenuOpen((v) => !v)}
              aria-label={menuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={menuOpen}
              className="flex h-11 w-11 items-center justify-center rounded-xl text-ink-600 transition hover:bg-sahaay-deep/6 md:hidden"
            >
              {menuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Scroll progress hairline */}
        <motion.div
          aria-hidden="true"
          className="holo-line absolute inset-x-0 bottom-0 h-[2px] origin-left"
          style={{ scaleX: navBar }}
        />

        {/* Mobile menu */}
        <motion.div
          initial={false}
          animate={{ height: menuOpen ? 'auto' : 0, opacity: menuOpen ? 1 : 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="overflow-hidden border-t border-sahaay-deep/6 bg-white/95 backdrop-blur-2xl md:hidden"
        >
          <div className="flex flex-col px-4 py-3">
            {navLinks.map((l) => (
              <a
                key={l.href}
                href={l.href}
                onClick={() => setMenuOpen(false)}
                className="flex min-h-[44px] items-center rounded-xl px-3 text-sm font-medium text-ink-600 transition hover:bg-sahaay-50 hover:text-sahaay-deep"
              >
                {l.label}
              </a>
            ))}
            <button
              onClick={() => { setMenuOpen(false); onNavigate('/login'); }}
              className="flex min-h-[44px] items-center rounded-xl px-3 text-left text-sm font-semibold text-sahaay-deep transition hover:bg-sahaay-50"
            >
              {t('nav.login')}
            </button>
          </div>
        </motion.div>
      </nav>

      {/* ═══════════════════ HERO ═══════════════════ */}
      <section
        id="hero"
        ref={heroRef}
        className="relative flex min-h-[100dvh] items-center overflow-hidden pb-16 pt-24 lg:pb-24 lg:pt-32"
      >
        {/* Photographic bed, pushed far back */}
        <motion.div className="absolute inset-0 z-0" style={{ y: heroImageY, scale: heroImageScale }}>
          <img
            src="https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1920&h=1200&fit=crop&auto=format"
            alt=""
            className="img-faded-wash h-full w-full object-cover"
            loading="eager"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-sahaay-surface via-sahaay-surface/94 to-sahaay-surface/55" />
          <div className="absolute inset-0 bg-gradient-to-t from-sahaay-surface via-transparent to-sahaay-surface/60" />
        </motion.div>

        <AuroraField intensity={0.85} />
        <div className="grid-paper pointer-events-none absolute inset-0 opacity-50" aria-hidden="true" />

        {/* The living monitor — real ECG maths, not a decorative squiggle */
        }
        <VitalsCanvas className="absolute inset-0 z-[1]" bpm={72} intensity={0.9} />

        <motion.div
          className="relative z-10 mx-auto w-full max-w-7xl px-4 lg:px-8"
          style={{ y: heroContentY, opacity: heroFade }}
        >
          <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
            {/* ── Left: kinetic type ── */}
            <div>
              <motion.div
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                className="mb-6 inline-flex items-center gap-2 rounded-full border border-sahaay-deep/10 bg-white/70 px-3.5 py-2 text-xs font-semibold text-sahaay-deep shadow-[var(--shadow-1)] backdrop-blur-md"
              >
                <span className="relative flex h-2 w-2">
                  <span className="animate-halo absolute inset-0 rounded-full bg-sahaay-500" />
                  <span className="relative h-2 w-2 rounded-full bg-sahaay-500" />
                </span>
                {t('hero.badge')}
              </motion.div>

              <h1 className="mb-5 font-display text-4xl font-bold leading-[1.05] text-ink-900 lg:text-6xl">
                {/* Split by words, not chars: Devanagari (hi/mr) conjuncts and
                    matras break apart if each code point gets its own box. */}
                <SplitText text={t('hero.title1')} immediate by="words" stagger={0.075} delay={0.15} as="span" />
                <br />
                <SplitText
                  text={t('hero.title2')}
                  immediate
                  by="words"
                  stagger={0.075}
                  delay={0.15 + t('hero.title1').split(' ').length * 0.075}
                  as="span"
                  unitClassName="holo-text"
                />
              </h1>

              <motion.p
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="mb-8 max-w-lg text-base leading-relaxed text-ink-500 lg:text-lg"
              >
                {t('hero.subtitle')}
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.62, ease: [0.16, 1, 0.3, 1] }}
                className="mb-10 flex flex-wrap gap-3"
              >
                <button
                  onClick={() => onNavigate('/login')}
                  className="sahaay-btn-primary px-7 py-3.5 text-base"
                >
                  {t('hero.cta')} <ArrowRight size={18} />
                </button>
                <button
                  onClick={() => onNavigate('/login')}
                  className="sahaay-btn-secondary px-7 py-3.5 text-base"
                >
                  <Play size={16} /> {t('hero.explore')}
                </button>
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                className="flex flex-wrap items-center gap-x-6 gap-y-3"
              >
                <button
                  onClick={() => onNavigate('/doctor/dashboard')}
                  className="sahaay-btn-ghost text-sm"
                >
                  {t('hero.professionals')} <ArrowRight size={15} />
                </button>

                {/* Micro-stats: real numbers, counted up */}
                <div className="flex items-center gap-5">
                  {[
                    { to: 50, suffix: 'K+', label: t('impact.patients') },
                    { to: 200, suffix: '+', label: t('impact.facilities') },
                  ].map((s) => (
                    <div key={s.label} className="border-l border-ink-200 pl-4">
                      <div className="font-display text-lg font-bold text-sahaay-deep">
                        <Counter to={s.to} suffix={s.suffix} duration={2} />
                      </div>
                      <div className="text-[11px] font-medium text-ink-400">{s.label}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>

            {/* ── Right: 3D console ── */}
            <div
              className="relative hidden h-[460px] lg:block"
              style={{ perspective: 1300, perspectiveOrigin: '50% 50%' }}
            >
              <motion.div
                className="relative h-full w-full"
                style={{ rotateX: tiltX, rotateY: tiltY, transformStyle: 'preserve-3d' }}
              >
                {/* Carousel sits on the mid plane, in a glass bezel */}
                <div
                  className="glass-card-elevated grain absolute inset-0 overflow-hidden p-3"
                  style={{ transform: 'translateZ(0px)' }}
                >
                  <div className="h-full w-full overflow-hidden rounded-[22px]">
                    <HealthcareCarousel variant="hero" />
                  </div>
                </div>

                {/* Floating vitals readouts at varying depths */}
                {vitalChips.map((c) => (
                  <motion.div
                    key={c.label}
                    className={`absolute ${c.pos}`}
                    style={{ x: floatX, y: floatY, z: c.z, transformStyle: 'preserve-3d' }}
                  >
                    <div className="glass-card-elevated flex items-center gap-3 px-4 py-3">
                      <span
                        className="flex h-9 w-9 items-center justify-center rounded-xl"
                        style={{ background: c.bg, color: c.tone }}
                      >
                        <Activity size={16} />
                      </span>
                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-400">
                          {c.label}
                        </div>
                        <div className="font-display text-lg font-bold leading-none text-ink-900">
                          {c.value}
                          <span className="ml-1 text-[11px] font-semibold text-ink-400">{c.unit}</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}

                {/* Depth frame behind everything */}
                <div
                  aria-hidden="true"
                  className="absolute -inset-8 rounded-[44px] border border-sahaay-deep/8"
                  style={{ transform: 'translateZ(-120px)' }}
                />
              </motion.div>
            </div>

            {/* Mobile carousel — same component, no 3D */}
            <div className="h-[300px] lg:hidden">
              <div className="glass-card-elevated h-full overflow-hidden p-2">
                <div className="h-full overflow-hidden rounded-[20px]">
                  <HealthcareCarousel variant="hero" />
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Scroll invitation */}
        {!reduce && (
          <motion.div
            aria-hidden="true"
            className="absolute inset-x-0 bottom-6 z-10 flex flex-col items-center gap-2"
            style={{ opacity: heroFade }}
          >
            <span className="font-mono text-[10px] uppercase tracking-[0.24em] text-ink-400">
              scroll
            </span>
            <motion.span
              className="h-8 w-[2px] rounded-full bg-gradient-to-b from-sahaay-500 to-transparent"
              animate={{ scaleY: [0.3, 1, 0.3], opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              style={{ originY: 0 }}
            />
          </motion.div>
        )}
      </section>

      {/* ═══════════════════ TRUST TICKER ═══════════════════ */}
      <section className="relative border-y border-sahaay-deep/6 bg-white/60 py-9">
        <p className="mb-5 px-4 text-center font-mono text-[10px] font-bold uppercase tracking-[0.22em] text-ink-400">
          Trusted by healthcare providers across India
        </p>
        <Marquee3D speed={42} tilt={8}>
          {trustItems.map((name) => (
            <div
              key={name}
              className="mx-2 flex shrink-0 items-center gap-2.5 rounded-2xl border border-sahaay-deep/8 bg-white/80 px-5 py-3 shadow-[var(--shadow-1)]"
            >
              <Building2 size={15} className="shrink-0 text-sahaay-600" />
              <span className="whitespace-nowrap text-[13px] font-semibold text-ink-600">{name}</span>
            </div>
          ))}
        </Marquee3D>
      </section>

      {/* ═══════════════════ THE CARE CORRIDOR · 3D scroll-through ═══════════════════ */}
      <div id="journey" className="relative">
        <CareCorridor
          stages={corridorStages}
          eyebrow="The care corridor"
          title={t('journey.title')}
          subtitle={t('journey.subtitle')}
          ctaLabel={t('hero.cta')}
          onCta={() => onNavigate('/login')}
          topOffset={88}
        />
      </div>

      {/* Journey summary — the same 8 steps, readable at a glance after the flight */}
      <section className="relative py-14 lg:py-20">
        <div className="mx-auto max-w-7xl px-4 lg:px-8">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-8">
            {journeySteps.map((step, i) => {
              const Icon = step.icon;
              return (
                <Reveal key={step.label} delay={i * 0.05} direction="rise" className="text-center">
                  <div className="stage-3d group flex flex-col items-center">
                    <div className="relative mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-sahaay-deep/10 to-sahaay-500/5 text-sahaay-deep transition-transform duration-500 group-hover:-translate-y-1.5">
                      <span
                        aria-hidden="true"
                        className="absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                        style={{ boxShadow: 'var(--glow-emerald)' }}
                      />
                      <Icon size={24} />
                    </div>
                    <p className="font-display text-sm font-bold text-ink-800">{step.label}</p>
                    <p className="mt-0.5 text-[11px] text-ink-400">{step.desc}</p>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════════════ FEATURES ═══════════════════ */}
      <section id="features" className="relative py-16 lg:py-24">
        <div className="mx-auto max-w-7xl px-4 lg:px-8">
          <div className="mb-12 text-center">
            <Reveal>
              <p className="mb-3 font-mono text-[10px] font-bold uppercase tracking-[0.22em] text-sahaay-600">
                The platform
              </p>
            </Reveal>
            <SplitText
              text={t('features.title')}
              as="h2"
              by="words"
              stagger={0.06}
              className="font-display text-3xl font-bold text-ink-900 lg:text-4xl"
            />
            <Reveal delay={0.15}>
              <p className="mx-auto mt-4 max-w-2xl text-ink-500">{t('features.subtitle')}</p>
            </Reveal>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <Reveal key={feature.title} delay={i * 0.1} amount={0.15}>
                  <TiltCard
                    strength={6}
                    lift={22}
                    className="glass-card-elevated grain group h-full overflow-hidden"
                  >
                    <div className="relative h-48 overflow-hidden">
                      <img
                        src={feature.image}
                        alt={feature.title}
                        className="h-full w-full object-cover transition-transform duration-[1100ms] ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-[1.07]"
                        loading="lazy"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-white via-white/35 to-transparent" />
                      <div
                        className="absolute bottom-4 left-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/92 text-sahaay-deep shadow-[var(--shadow-2)] backdrop-blur-md"
                        style={{ transform: 'translateZ(50px)' }}
                      >
                        <Icon size={22} />
                      </div>
                    </div>
                    <div className="relative p-6" style={{ transform: 'translateZ(28px)' }}>
                      <h3 className="mb-2 font-display text-lg font-bold text-ink-900">
                        {feature.title}
                      </h3>
                      <p className="text-sm leading-relaxed text-ink-500">{feature.desc}</p>
                    </div>
                  </TiltCard>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════════════ ROLE ORBIT · 3D, and it actually navigates ═══════════════════ */}
      <section id="roles" className="relative overflow-x-clip py-16 lg:py-24">
        <AuroraField intensity={0.5} />
        <div className="relative mx-auto max-w-7xl px-4 lg:px-8">
          {/* Copy sits above the ring: the ring sweeps ~960px wide, which would
              otherwise reach across a side-by-side column and cover the text. */}
          <div className="mx-auto mb-12 max-w-2xl text-center">
            <Reveal>
              <p className="mb-3 inline-flex items-center gap-2 font-mono text-[10px] font-bold uppercase tracking-[0.22em] text-sahaay-600">
                <Sparkles size={13} /> One platform, four vantage points
              </p>
            </Reveal>
            <SplitText
              text="Step into any role"
              as="h2"
              by="words"
              stagger={0.07}
              className="font-display text-3xl font-bold text-ink-900 lg:text-5xl"
            />
            <Reveal delay={0.15}>
              <p className="mx-auto mt-4 max-w-lg text-ink-500">
                Spin the ring and open a live dashboard. Every view reads from the same
                record — the difference is what each person needs to see first.
              </p>
            </Reveal>
          </div>

          <OrbitRing items={roleRing} onSelect={onNavigate} />

          <Reveal delay={0.2}>
            <p className="mt-2 text-center font-mono text-[11px] text-ink-400">
              ← → arrow keys to rotate
            </p>
          </Reveal>
        </div>
      </section>

      {/* ═══════════════════ GALLERY ═══════════════════ */}
      <section className="relative bg-white/45 py-16 lg:py-24">
        <div className="mx-auto max-w-7xl px-4 lg:px-8">
          <div className="mb-10 text-center">
            <SplitText
              text="Healthcare in Action"
              as="h2"
              by="words"
              stagger={0.07}
              className="font-display text-3xl font-bold text-ink-900 lg:text-4xl"
            />
            <Reveal delay={0.15}>
              <p className="mx-auto mt-4 max-w-2xl text-ink-500">
                From rural health centers to specialist consultations, SAHAAY connects every
                part of the care journey.
              </p>
            </Reveal>
          </div>

          <div className="grid-mosaic grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4">
            {galleryImages.map((img, i) => (
              <Reveal
                key={img.src}
                delay={i * 0.08}
                direction="scale"
                amount={0.1}
                className={`${img.span} group relative overflow-hidden rounded-2xl`}
              >
                <img
                  src={img.src}
                  alt={img.alt}
                  className="h-full w-full object-cover transition-all duration-[900ms] ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-[1.06]"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-sahaay-deep/70 via-sahaay-deep/10 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                <div className="absolute inset-x-3 bottom-3 translate-y-2 opacity-0 transition-all duration-500 group-hover:translate-y-0 group-hover:opacity-100">
                  <p className="font-display text-sm font-semibold text-white drop-shadow">
                    {img.alt}
                  </p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════ IMPACT ═══════════════════ */}
      <section id="impact" className="relative overflow-hidden py-16 lg:py-24">
        <div className="sahaay-gradient-deep absolute inset-0" />
        <div className="absolute inset-0 opacity-10">
          <img
            src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1920&h=1080&fit=crop&auto=format"
            alt=""
            className="img-ken-burns h-full w-full object-cover"
          />
        </div>
        <div
          className="grid-paper pointer-events-none absolute inset-0 opacity-[0.12] mix-blend-overlay"
          aria-hidden="true"
        />

        <div className="relative z-10 mx-auto max-w-7xl px-4 lg:px-8">
          <div className="mb-12 text-center">
            <SplitText
              text={t('impact.title')}
              as="h2"
              by="words"
              stagger={0.07}
              className="font-display text-3xl font-bold text-white lg:text-4xl"
            />
            <Reveal delay={0.15}>
              <p className="mx-auto mt-4 max-w-2xl text-sahaay-50/80">{t('impact.subtitle')}</p>
            </Reveal>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {impactStats.map((stat, i) => (
              <Reveal key={stat.label} delay={i * 0.12} amount={0.2}>
                <TiltCard
                  strength={7}
                  lift={20}
                  spotlight={false}
                  className="group relative h-full overflow-hidden rounded-[28px]"
                >
                  <div className="h-52 overflow-hidden">
                    <img
                      src={stat.image}
                      alt=""
                      className="h-full w-full object-cover transition-transform duration-[1100ms] ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-110"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-sahaay-950/92 via-sahaay-950/45 to-transparent" />
                  </div>
                  <div
                    className="absolute inset-x-0 bottom-0 p-6"
                    style={{ transform: 'translateZ(40px)' }}
                  >
                    <p className="mb-1 font-display text-4xl font-bold text-white lg:text-5xl">
                      <Counter to={stat.to} suffix={stat.suffix} duration={2.2} />
                    </p>
                    <p className="text-sm font-medium text-sahaay-50/85">{stat.label}</p>
                  </div>
                </TiltCard>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════ TESTIMONIALS ═══════════════════ */}
      <section id="voices" className="relative py-16 lg:py-24">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-sahaay-50/40 to-transparent" />
        <div className="relative mx-auto max-w-7xl px-4 lg:px-8">
          <div className="mb-12 text-center">
            <SplitText
              text={t('testimonials.title')}
              as="h2"
              by="words"
              stagger={0.07}
              className="font-display text-3xl font-bold text-ink-900 lg:text-4xl"
            />
            <Reveal delay={0.15}>
              <p className="mx-auto mt-4 max-w-2xl text-ink-500">{t('testimonials.subtitle')}</p>
            </Reveal>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {testimonials.map((tm, i) => (
              <Reveal key={tm.name} delay={i * 0.12} amount={0.2}>
                <TiltCard strength={6} lift={18} className="glass-card-elevated grain h-full p-6">
                  <Quote
                    size={34}
                    className="absolute right-4 top-4 text-sahaay-deep/8"
                    aria-hidden="true"
                  />
                  <p
                    className="relative z-10 mb-6 text-sm leading-relaxed text-ink-600"
                    style={{ transform: 'translateZ(24px)' }}
                  >
                    &ldquo;{tm.text}&rdquo;
                  </p>
                  <div className="relative flex items-center gap-3">
                    <div className="h-12 w-12 shrink-0 overflow-hidden rounded-full border-2 border-sahaay-deep/10">
                      <img
                        src={tm.avatar}
                        alt={tm.name}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />
                    </div>
                    <div className="min-w-0">
                      <p className="font-display text-sm font-bold text-ink-900">{tm.name}</p>
                      <p className="truncate text-xs text-ink-400">{tm.role}</p>
                    </div>
                    <div
                      className="ml-auto flex shrink-0 gap-0.5"
                      role="img"
                      aria-label="Rated 5 out of 5"
                    >
                      {[1, 2, 3, 4, 5].map((s) => (
                        <Star key={s} size={14} className="fill-vital-sun text-vital-sun" />
                      ))}
                    </div>
                  </div>
                </TiltCard>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════ ABOUT ═══════════════════ */}
      <section id="about" className="relative bg-white/50 py-16 lg:py-24">
        <div className="mx-auto max-w-7xl px-4 lg:px-8">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            {/* 3D staggered collage */}
            <div className="stage-3d grid grid-cols-2 gap-3">
              {[
                { src: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=500&h=600&fit=crop&auto=format', alt: 'Rural healthcare', h: 'h-64', z: 40 },
                { src: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=500&h=400&fit=crop&auto=format', alt: 'Medical supplies', h: 'h-40', z: 10 },
                { src: 'https://images.unsplash.com/photo-1581056771107-24ca5f033842?w=500&h=400&fit=crop&auto=format', alt: 'Healthcare tech', h: 'h-40', z: 24 },
                { src: 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=500&h=600&fit=crop&auto=format', alt: 'Doctor consultation', h: 'h-64', z: 55 },
              ].map((img, i) => (
                <Reveal
                  key={img.src}
                  delay={i * 0.12}
                  direction="scale"
                  amount={0.2}
                  className={`${img.h} img-shimmer overflow-hidden rounded-2xl shadow-[var(--shadow-3)] ${
                    i % 2 === 0 ? 'mt-0' : 'mt-6'
                  }`}
                >
                  <img
                    src={img.src}
                    alt={img.alt}
                    className="img-zoom-hover img-faded-wash h-full w-full object-cover"
                    loading="lazy"
                  />
                </Reveal>
              ))}
            </div>

            <div>
              <SplitText
                text={t('about.title')}
                as="h2"
                by="words"
                stagger={0.07}
                className="mb-6 font-display text-3xl font-bold text-ink-900 lg:text-4xl"
              />
              <Reveal delay={0.1}>
                <p className="mb-6 leading-relaxed text-ink-500">{t('about.text1')}</p>
              </Reveal>
              <Reveal delay={0.18}>
                <p className="mb-8 leading-relaxed text-ink-500">{t('about.text2')}</p>
              </Reveal>

              <div className="space-y-4">
                {[
                  { icon: MapPin, text: t('about.serving') },
                  { icon: Phone, text: t('about.works') },
                  { icon: Shield, text: t('about.secure') },
                ].map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <Reveal key={i} delay={0.24 + i * 0.08} direction="left" distance={20}>
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sahaay-deep/8 text-sahaay-deep">
                          <Icon size={18} />
                        </div>
                        <p className="text-sm font-medium text-ink-600">{item.text}</p>
                      </div>
                    </Reveal>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════ CTA ═══════════════════ */}
      <section className="relative overflow-hidden py-20 lg:py-28">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=1920&h=1080&fit=crop&auto=format"
            alt=""
            className="h-full w-full object-cover"
            loading="lazy"
          />
          <div className="sahaay-gradient-deep absolute inset-0 opacity-92" />
        </div>

        {/* ECG-only heartbeat across the dark band */}
        <VitalsCanvas className="absolute inset-0 opacity-70" bpm={64} particles={false} />

        <div className="absolute left-[5%] top-10 hidden h-24 w-24 overflow-hidden rounded-xl opacity-15 lg:block img-float-slow">
          <img src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=200&h=200&fit=crop&auto=format" alt="" className="h-full w-full object-cover" />
        </div>
        <div className="absolute bottom-10 right-[8%] hidden h-20 w-20 rotate-6 overflow-hidden rounded-xl opacity-15 lg:block img-float-medium">
          <img src="https://images.unsplash.com/photo-1551076805-e1869033e561?w=200&h=200&fit=crop&auto=format" alt="" className="h-full w-full object-cover" />
        </div>

        <div className="relative z-10 mx-auto max-w-4xl px-4 text-center lg:px-8">
          <SplitText
            text={t('cta.title')}
            as="h2"
            by="words"
            stagger={0.07}
            className="mb-4 font-display text-3xl font-bold text-white lg:text-5xl"
          />
          <Reveal delay={0.15}>
            <p className="mx-auto mb-9 max-w-xl text-lg text-sahaay-50/90">{t('cta.subtitle')}</p>
          </Reveal>
          <Reveal delay={0.25}>
            <div className="flex flex-wrap justify-center gap-4">
              <button
                onClick={() => onNavigate('/login')}
                className="lum-sheen inline-flex min-h-[44px] items-center gap-2 rounded-xl bg-white px-8 py-3.5 font-display text-base font-bold text-sahaay-deep shadow-[0_10px_30px_rgba(0,0,0,0.22)] transition-all duration-300 hover:-translate-y-0.5 hover:bg-sahaay-50"
              >
                {t('cta.free')} <ArrowRight size={18} />
              </button>
              <button
                onClick={() => onNavigate('/doctor/dashboard')}
                className="inline-flex min-h-[44px] items-center gap-2 rounded-xl border-2 border-white/35 px-8 py-3.5 font-display text-base font-bold text-white transition-all duration-300 hover:-translate-y-0.5 hover:border-white/60 hover:bg-white/10"
              >
                <Video size={17} /> {t('cta.professional')}
              </button>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══════════════════ FOOTER ═══════════════════ */}
      <footer className="relative overflow-hidden bg-sahaay-950 py-12 text-white/60">
        <div
          className="grid-paper pointer-events-none absolute inset-0 opacity-[0.07]"
          aria-hidden="true"
        />
        <div className="relative mx-auto max-w-7xl px-4 lg:px-8">
          <div className="mb-8 grid gap-8 md:grid-cols-4">
            <div>
              <div className="mb-4 flex items-center gap-2">
                <Heart size={20} className="text-sahaay-400" fill="currentColor" />
                <span className="font-display text-lg font-bold text-white">SAHAAY</span>
              </div>
              <p className="text-sm leading-relaxed">{t('footer.tagline')}</p>
              <p className="mt-2 text-sm">{t('footer.desc')}</p>
              <div className="mt-4 h-24 w-full overflow-hidden rounded-xl opacity-40">
                <img
                  src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&h=150&fit=crop&auto=format"
                  alt=""
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
              </div>
            </div>

            {[
              {
                heading: t('footer.platform'),
                links: [t('footer.forPatients'), t('footer.forDoctors'), t('footer.forWorkers'), t('footer.forFacilities')],
              },
              {
                heading: t('footer.resources'),
                links: [t('footer.docs'), t('footer.api'), t('footer.community'), t('footer.support')],
              },
              {
                heading: t('footer.legal'),
                links: [t('footer.privacy'), t('footer.terms'), t('footer.security'), t('footer.compliance')],
              },
            ].map((col) => (
              <div key={col.heading}>
                <h4 className="mb-3 font-display text-sm font-bold text-white">{col.heading}</h4>
                <ul className="space-y-2 text-sm">
                  {col.links.map((link) => (
                    <li key={link}>
                      <a
                        href="#"
                        className="inline-block transition-colors duration-300 hover:text-sahaay-300"
                      >
                        {link}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="border-t border-white/10 pt-6 text-center text-sm">
            <p>&copy; 2026 SAHAAY. All rights reserved. Built for hackathon demonstration.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
