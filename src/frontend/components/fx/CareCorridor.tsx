import { useRef, useState, type ComponentType } from 'react';
import {
  motion,
  useScroll,
  useSpring,
  useTransform,
  useMotionValueEvent,
  useReducedMotion,
  type MotionValue,
} from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export interface CorridorStage {
  icon: ComponentType<{ size?: number | string; className?: string }>;
  label: string;
  desc: string;
  /** Short data readout shown in the card footer, e.g. "avg 4 min". */
  metric?: string;
  /** One of the vital-spectrum accents. */
  accent: 'emerald' | 'oxy' | 'nerve' | 'pulse';
}

interface CareCorridorProps {
  stages: CorridorStage[];
  eyebrow?: string;
  title?: string;
  subtitle?: string;
  ctaLabel?: string;
  onCta?: () => void;
  /**
   * Extra top padding for the pinned HUD, in px. The section pins at
   * `top: 0`, so a fixed site header would otherwise cover the eyebrow and
   * the stage counter.
   */
  topOffset?: number;
}

/* World geometry, in px of CSS 3D space. */
const GAP = 900;          // distance between consecutive stages
const PERSPECTIVE = 1150; // camera focal length
const RINGS = 16;         // depth-cue rings
const RING_GAP = 420;
const RING_SPAN = RINGS * RING_GAP;

const ACCENTS = {
  emerald: { ink: '#0A5F38', dot: '#17B366', soft: 'rgba(23, 179, 102, 0.13)', ring: 'rgba(23, 179, 102, 0.34)' },
  oxy:     { ink: '#076A82', dot: '#0EA5C9', soft: 'rgba(14, 165, 201, 0.13)', ring: 'rgba(14, 165, 201, 0.34)' },
  nerve:   { ink: '#5533DB', dot: '#7C5CFF', soft: 'rgba(124, 92, 255, 0.13)', ring: 'rgba(124, 92, 255, 0.34)' },
  pulse:   { ink: '#C41E3F', dot: '#FF4D6D', soft: 'rgba(255, 77, 109, 0.13)', ring: 'rgba(255, 77, 109, 0.34)' },
} as const;

/* ────────────────────────────────────────────────────────────────────────
   A single stage card, positioned in Z relative to the moving camera.
   ──────────────────────────────────────────────────────────────────────── */
function CorridorCard({
  stage,
  index,
  camZ,
}: {
  stage: CorridorStage;
  index: number;
  camZ: MotionValue<number>;
}) {
  const a = ACCENTS[stage.accent];
  const Icon = stage.icon;

  // Translate world position into camera-relative depth.
  const tz = useTransform(camZ, (c) => c - index * GAP);

  const opacity = useTransform(
    tz,
    [-2.45 * GAP, -1.15 * GAP, 240, 470],
    [0, 1, 1, 0],
  );

  const filter = useTransform(
    tz,
    [-2.45 * GAP, -1.0 * GAP, 200, 470],
    ['blur(11px)', 'blur(0px)', 'blur(0px)', 'blur(14px)'],
  );

  // Gentle off-axis drift so the stack reads as a corridor, not a deck.
  // Expressed in vw and capped in px: a flat 88px shove is ~6% of a desktop
  // viewport but a quarter of a phone's, which pushed cards off-screen.
  const dir = Math.sin(index * 1.15);
  const mag = `min(${(Math.abs(dir) * 6.2).toFixed(2)}vw, ${(Math.abs(dir) * 88).toFixed(1)}px)`;
  const xExpr = dir >= 0 ? `calc(-50% + ${mag})` : `calc(-50% - ${mag})`;
  const yOffset = Math.cos(index * 0.82) * 46;
  const yaw = dir * -6;

  return (
    <motion.div
      className="absolute left-1/2 top-1/2 w-[min(560px,86vw)]"
      style={{
        z: tz,
        opacity,
        filter,
        x: xExpr,
        y: `calc(-50% + ${yOffset}px)`,
        rotateY: yaw,
        transformStyle: 'preserve-3d',
      }}
    >
      <div
        className="glass-card-elevated grain relative overflow-hidden p-6 sm:p-8"
        style={{ boxShadow: `var(--shadow-lift), 0 0 0 1px ${a.ring}, var(--rim-light)` }}
      >
        {/* Accent wash */}
        <div
          className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full blur-3xl"
          style={{ background: a.soft }}
        />

        <div className="relative flex items-start gap-4 sm:gap-5">
          <div
            className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl sm:h-16 sm:w-16"
            style={{ background: a.soft, color: a.ink, boxShadow: `inset 0 0 0 1px ${a.ring}` }}
          >
            <Icon size={26} />
          </div>

          <div className="min-w-0 flex-1">
            <div className="mb-1.5 flex items-center gap-2">
              <span
                className="font-mono text-[11px] font-bold tracking-[0.16em]"
                style={{ color: a.ink }}
              >
                {String(index + 1).padStart(2, '0')}
              </span>
              <span className="h-px flex-1" style={{ background: a.ring }} />
            </div>

            <h3 className="font-display text-xl font-bold text-ink-900 sm:text-2xl">
              {stage.label}
            </h3>
            <p className="mt-1.5 text-sm leading-relaxed text-ink-500">{stage.desc}</p>

            {stage.metric && (
              <div className="mt-4 flex items-center gap-2 border-t border-ink-200/60 pt-3">
                <span
                  className="h-1.5 w-1.5 rounded-full animate-pulse-soft"
                  style={{ background: a.dot }}
                />
                <span className="font-mono text-[11px] font-medium tracking-wide text-ink-400">
                  {stage.metric}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

/* ────────────────────────────────────────────────────────────────────────
   Receding rings. The strongest depth cue in the scene — without these the
   cards just look like they are scaling, not travelling.
   ──────────────────────────────────────────────────────────────────────── */
function DepthRing({ index, camZ }: { index: number; camZ: MotionValue<number> }) {
  // Wrap a finite set of rings into an endless tunnel: each ring recycles to
  // the far end once it passes the camera.
  const tz = useTransform(camZ, (c) => {
    const raw = c - index * RING_GAP;
    const m = ((raw % RING_SPAN) + RING_SPAN) % RING_SPAN;
    return m - RING_SPAN + 400;
  });

  const opacity = useTransform(
    tz,
    [-RING_SPAN, -0.55 * RING_SPAN, 300, 430],
    [0, 0.5, 0.5, 0],
  );

  return (
    <motion.div
      className="absolute left-1/2 top-1/2 h-[min(760px,92vh)] w-[min(1180px,94vw)] -translate-x-1/2 -translate-y-1/2 rounded-[48px] border"
      style={{
        z: tz,
        opacity,
        borderColor: 'rgba(14, 79, 58, 0.16)',
        transformStyle: 'preserve-3d',
      }}
    />
  );
}

/* ──────────────────────────────────────────────────────────────────────── */

export function CareCorridor({
  stages,
  eyebrow = 'The care corridor',
  title = 'Scroll through a real patient journey',
  subtitle = 'Eight coordinated stages. One continuous record.',
  ctaLabel = 'Enter SAHAAY',
  onCta,
  topOffset = 0,
}: CareCorridorProps) {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const [active, setActive] = useState(0);

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end end'],
  });

  // Smoothing the driver is what separates "premium" from "twitchy".
  const progress = useSpring(scrollYProgress, {
    stiffness: 90,
    damping: 26,
    mass: 0.4,
    restDelta: 0.0005,
  });

  const camZ = useTransform(progress, [0, 1], [-0.85 * GAP, (stages.length - 0.25) * GAP]);

  // A stage is "active" when the camera is closest to its world position.
  useMotionValueEvent(camZ, 'change', (z) => {
    const i = Math.round(z / GAP);
    setActive(Math.max(0, Math.min(stages.length - 1, i)));
  });

  const barScale = useTransform(progress, [0, 1], [0, 1]);

  /* ── Reduced motion: same content, honest static layout ───────────────── */
  if (reduce) {
    return (
      <section className="relative py-20">
        <div className="mx-auto max-w-6xl px-4 lg:px-8">
          <p className="font-mono text-xs font-bold uppercase tracking-[0.2em] text-sahaay-600">
            {eyebrow}
          </p>
          <h2 className="mt-3 font-display text-3xl font-bold text-ink-900 lg:text-4xl">{title}</h2>
          <p className="mt-3 max-w-2xl text-ink-500">{subtitle}</p>

          <ol className="mt-10 grid gap-4 sm:grid-cols-2">
            {stages.map((s, i) => {
              const a = ACCENTS[s.accent];
              const Icon = s.icon;
              return (
                <li key={i} className="glass-card flex items-start gap-4 p-5">
                  <div
                    className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl"
                    style={{ background: a.soft, color: a.ink }}
                  >
                    <Icon size={22} />
                  </div>
                  <div>
                    <h3 className="font-display text-base font-bold text-ink-900">
                      {String(i + 1).padStart(2, '0')} · {s.label}
                    </h3>
                    <p className="mt-1 text-sm text-ink-500">{s.desc}</p>
                    {s.metric && (
                      <p className="mt-2 font-mono text-[11px] text-ink-400">{s.metric}</p>
                    )}
                  </div>
                </li>
              );
            })}
          </ol>

          {onCta && (
            <button onClick={onCta} className="sahaay-btn-primary mt-8">
              {ctaLabel} <ArrowRight size={17} />
            </button>
          )}
        </div>
      </section>
    );
  }

  /* ── The corridor ────────────────────────────────────────────────────── */
  return (
    <section
      ref={ref}
      aria-label={title}
      style={{ height: `${stages.length * 62 + 90}vh` }}
      className="relative"
    >
      <div className="sticky top-0 h-screen overflow-hidden">
        {/* Vignette + graph paper floor to ground the scene */}
        <div className="absolute inset-0 grid-paper opacity-60" aria-hidden="true" />
        <div
          className="pointer-events-none absolute inset-0"
          aria-hidden="true"
          style={{
            background:
              'radial-gradient(72% 62% at 50% 48%, rgba(242,251,245,0) 0%, rgba(242,251,245,0.55) 62%, #F2FBF5 100%)',
          }}
        />

        {/* 3D stage */}
        <div
          className="absolute inset-0"
          style={{ perspective: `${PERSPECTIVE}px`, perspectiveOrigin: '50% 48%' }}
        >
          <div className="relative h-full w-full" style={{ transformStyle: 'preserve-3d' }}>
            {Array.from({ length: RINGS }).map((_, i) => (
              <DepthRing key={`r${i}`} index={i} camZ={camZ} />
            ))}
            {stages.map((s, i) => (
              <CorridorCard key={i} stage={s} index={i} camZ={camZ} />
            ))}
          </div>
        </div>

        {/* ── HUD ──────────────────────────────────────────────────────── */}
        <div
          className="pointer-events-none absolute inset-x-0 top-0 z-20 px-4 pt-6 lg:px-10 lg:pt-10"
          style={topOffset ? { paddingTop: topOffset } : undefined}
        >
          <div className="mx-auto flex max-w-7xl items-start justify-between gap-6">
            <div>
              <p className="font-mono text-[10px] font-bold uppercase tracking-[0.22em] text-sahaay-600">
                {eyebrow}
              </p>
              <h2 className="mt-2 max-w-md font-display text-2xl font-bold leading-tight text-ink-900 lg:text-4xl">
                {title}
              </h2>
              <p className="mt-2 hidden max-w-sm text-sm text-ink-500 sm:block">{subtitle}</p>
            </div>

            <div className="shrink-0 text-right">
              <div className="font-mono text-4xl font-bold leading-none text-ink-900 lg:text-6xl">
                {String(active + 1).padStart(2, '0')}
              </div>
              <div className="font-mono text-xs text-ink-400">
                / {String(stages.length).padStart(2, '0')}
              </div>
            </div>
          </div>
        </div>

        {/* Progress rail + CTA */}
        <div className="absolute inset-x-0 bottom-0 z-20 px-4 pb-7 lg:px-10 lg:pb-10">
          <div className="mx-auto flex max-w-7xl items-center gap-5">
            <div className="h-[3px] flex-1 overflow-hidden rounded-full bg-ink-200/70">
              <motion.div
                className="holo-line h-full origin-left rounded-full"
                style={{ scaleX: barScale }}
              />
            </div>

            {onCta && (
              <button onClick={onCta} className="sahaay-btn-primary shrink-0 text-[13px]">
                {ctaLabel} <ArrowRight size={16} />
              </button>
            )}
          </div>

          <p className="mx-auto mt-3 max-w-7xl font-mono text-[10px] uppercase tracking-[0.2em] text-ink-300">
            keep scrolling
          </p>
        </div>
      </div>
    </section>
  );
}
