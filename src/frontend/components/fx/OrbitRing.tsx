import { useEffect, useRef, useState, type ComponentType } from 'react';
import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  useReducedMotion,
  type MotionValue,
} from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export interface OrbitItem {
  icon: ComponentType<{ size?: number | string; className?: string }>;
  title: string;
  subtitle: string;
  /** Bullet points shown on the front-facing card. */
  points: string[];
  accent: 'emerald' | 'oxy' | 'nerve' | 'pulse';
  ctaLabel: string;
  route: string;
}

interface OrbitRingProps {
  items: OrbitItem[];
  onSelect: (route: string) => void;
  /** ms between automatic advances. 0 disables autoplay. */
  autoplay?: number;
}

const RADIUS = 330;

const ACCENTS = {
  emerald: { ink: '#0A5F38', dot: '#17B366', soft: 'rgba(23, 179, 102, 0.12)', ring: 'rgba(23, 179, 102, 0.32)' },
  oxy:     { ink: '#076A82', dot: '#0EA5C9', soft: 'rgba(14, 165, 201, 0.12)', ring: 'rgba(14, 165, 201, 0.32)' },
  nerve:   { ink: '#5533DB', dot: '#7C5CFF', soft: 'rgba(124, 92, 255, 0.12)', ring: 'rgba(124, 92, 255, 0.32)' },
  pulse:   { ink: '#C41E3F', dot: '#FF4D6D', soft: 'rgba(255, 77, 109, 0.12)', ring: 'rgba(255, 77, 109, 0.32)' },
} as const;

function OrbitCard({
  item,
  index,
  step,
  rotation,
  isActive,
  onSelect,
}: {
  item: OrbitItem;
  index: number;
  step: number;
  rotation: MotionValue<number>;
  isActive: boolean;
  onSelect: () => void;
}) {
  const a = ACCENTS[item.accent];
  const Icon = item.icon;
  const base = index * step;

  // Cancel the accumulated ring rotation so every face stays legible.
  const counter = useTransform(rotation, (r) => -(r + base));

  // Cards on the far side of the ring dim and recede.
  const facing = useTransform(rotation, (r) => Math.cos(((r + base) * Math.PI) / 180));
  const opacity = useTransform(facing, [-1, 0.1, 1], [0.12, 0.4, 1]);
  const scale = useTransform(facing, [-1, 1], [0.82, 1]);

  return (
    <motion.div
      className="absolute left-1/2 top-1/2 w-[300px]"
      style={{
        rotateY: base,
        x: '-50%',
        y: '-50%',
        transformStyle: 'preserve-3d',
      }}
    >
      <motion.div
        style={{ z: RADIUS, rotateY: counter, opacity, scale, transformStyle: 'preserve-3d' }}
      >
        <div
          className="glass-card-elevated grain relative overflow-hidden p-6"
          style={{
            boxShadow: isActive
              ? `var(--shadow-lift), 0 0 0 1.5px ${a.ring}, var(--rim-light)`
              : `var(--shadow-2), var(--rim-light)`,
          }}
        >
          <div
            className="pointer-events-none absolute -right-12 -top-12 h-36 w-36 rounded-full blur-3xl"
            style={{ background: a.soft }}
          />

          <div
            className="relative mb-4 flex h-14 w-14 items-center justify-center rounded-2xl"
            style={{ background: a.soft, color: a.ink, boxShadow: `inset 0 0 0 1px ${a.ring}` }}
          >
            <Icon size={26} />
          </div>

          <h3 className="font-display text-lg font-bold text-ink-900">{item.title}</h3>
          <p className="mt-1 text-[13px] text-ink-500">{item.subtitle}</p>

          <ul className="mt-4 space-y-2">
            {item.points.map((p) => (
              <li key={p} className="flex items-start gap-2 text-[12.5px] text-ink-600">
                <span
                  className="mt-[6px] h-1.5 w-1.5 shrink-0 rounded-full"
                  style={{ background: a.dot }}
                />
                {p}
              </li>
            ))}
          </ul>

          <button
            onClick={onSelect}
            // Only the front card is reachable; back faces are visually hidden.
            tabIndex={isActive ? 0 : -1}
            aria-hidden={!isActive}
            className="sahaay-btn-secondary mt-5 w-full text-[13px]"
            style={{ color: a.ink, borderColor: a.ring }}
          >
            {item.ctaLabel}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

/**
 * A 3D carousel ring of role cards. This is not decoration — the front card's
 * button navigates to that role's live dashboard.
 *
 * Fully operable without a mouse: arrow keys rotate the ring, the previous /
 * next buttons are real buttons, and off-screen faces are removed from the
 * tab order so focus never lands on something the user cannot see.
 */
export function OrbitRing({ items, onSelect, autoplay = 5200 }: OrbitRingProps) {
  const reduce = useReducedMotion();
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const step = 360 / items.length;
  const target = useMotionValue(0);
  const rotation = useSpring(target, { stiffness: 70, damping: 18, mass: 0.9 });

  const go = (dir: number) => {
    const next = active + dir;
    setActive(((next % items.length) + items.length) % items.length);
    target.set(target.get() - dir * step);
  };

  useEffect(() => {
    if (!autoplay || paused || reduce) return;
    const id = setInterval(() => go(1), autoplay);
    return () => clearInterval(id);
    // `go` closes over `active`; re-arming per change keeps the cadence steady.
  }, [autoplay, paused, reduce, active]);

  /* Reduced motion: a plain, honest grid of the same cards. */
  if (reduce) {
    return (
      <div className="grid gap-4 sm:grid-cols-2">
        {items.map((item) => {
          const a = ACCENTS[item.accent];
          const Icon = item.icon;
          return (
            <div key={item.title} className="glass-card p-6">
              <div
                className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl"
                style={{ background: a.soft, color: a.ink }}
              >
                <Icon size={24} />
              </div>
              <h3 className="font-display text-lg font-bold text-ink-900">{item.title}</h3>
              <p className="mt-1 text-[13px] text-ink-500">{item.subtitle}</p>
              <ul className="mt-3 space-y-1.5">
                {item.points.map((p) => (
                  <li key={p} className="text-[12.5px] text-ink-600">· {p}</li>
                ))}
              </ul>
              <button
                onClick={() => onSelect(item.route)}
                className="sahaay-btn-secondary mt-4 w-full text-[13px]"
              >
                {item.ctaLabel}
              </button>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div
      ref={ref}
      role="group"
      aria-label="Choose your role"
      tabIndex={0}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
      onKeyDown={(e) => {
        if (e.key === 'ArrowRight') { e.preventDefault(); go(1); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
      }}
      className="relative"
    >
      <div
        className="relative h-[440px] w-full"
        style={{ perspective: 1500, perspectiveOrigin: '50% 45%' }}
      >
        <motion.div
          className="absolute inset-0"
          style={{ transformStyle: 'preserve-3d', rotateY: rotation, rotateX: 6 }}
        >
          {items.map((item, i) => (
            <OrbitCard
              key={item.title}
              item={item}
              index={i}
              step={step}
              rotation={rotation}
              isActive={i === active}
              onSelect={() => onSelect(item.route)}
            />
          ))}
        </motion.div>
      </div>

      {/* Reflection puddle — sells the ring as an object sitting in space */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 bottom-6 mx-auto h-16 w-[70%] rounded-[50%] blur-2xl"
        style={{ background: 'radial-gradient(50% 50%, rgba(14,79,58,0.16), transparent 70%)' }}
      />

      {/* Controls */}
      <div className="mt-2 flex items-center justify-center gap-3">
        <button
          onClick={() => go(-1)}
          aria-label="Previous role"
          className="flex h-11 w-11 items-center justify-center rounded-full border border-ink-200 bg-white/80 text-ink-600 shadow-[var(--shadow-1)] transition hover:border-sahaay-400 hover:text-sahaay-deep"
        >
          <ChevronLeft size={18} />
        </button>

        <div className="flex items-center gap-2">
          {items.map((item, i) => (
            <button
              key={item.title}
              onClick={() => { setActive(i); target.set(-i * step); }}
              aria-label={`Show ${item.title}`}
              aria-current={i === active}
              className="h-2.5 rounded-full transition-all duration-300"
              style={{
                width: i === active ? 28 : 10,
                background: i === active ? '#17B366' : 'rgba(14,79,58,0.2)',
              }}
            />
          ))}
        </div>

        <button
          onClick={() => go(1)}
          aria-label="Next role"
          className="flex h-11 w-11 items-center justify-center rounded-full border border-ink-200 bg-white/80 text-ink-600 shadow-[var(--shadow-1)] transition hover:border-sahaay-400 hover:text-sahaay-deep"
        >
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  );
}
