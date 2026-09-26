import type { ReactNode } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Counter } from '../fx/Counter';

type Accent = 'emerald' | 'oxy' | 'nerve' | 'pulse' | 'sun';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  trend?: { value: string; positive: boolean };
  /** Accent for the icon tile and glow. */
  accent?: Accent;
  delay?: number;
}

/* Static token map. The previous version interpolated the colour into class
   names (`from-${color}/15`), which Tailwind cannot generate at build time —
   so the icon tile rendered with no background and no colour at all. */
const ACCENTS: Record<Accent, { ink: string; from: string; to: string; ring: string; glow: string }> = {
  emerald: { ink: '#0E4F3A', from: 'rgba(23,179,102,0.18)',  to: 'rgba(23,179,102,0.04)',  ring: 'rgba(23,179,102,0.22)',  glow: 'rgba(23,179,102,0.30)' },
  oxy:     { ink: '#076A82', from: 'rgba(14,165,201,0.18)',  to: 'rgba(14,165,201,0.04)',  ring: 'rgba(14,165,201,0.22)',  glow: 'rgba(14,165,201,0.30)' },
  nerve:   { ink: '#5533DB', from: 'rgba(124,92,255,0.18)',  to: 'rgba(124,92,255,0.04)',  ring: 'rgba(124,92,255,0.22)',  glow: 'rgba(124,92,255,0.30)' },
  pulse:   { ink: '#C41E3F', from: 'rgba(255,77,109,0.18)',  to: 'rgba(255,77,109,0.04)',  ring: 'rgba(255,77,109,0.22)',  glow: 'rgba(255,77,109,0.30)' },
  sun:     { ink: '#92610A', from: 'rgba(245,158,11,0.20)',  to: 'rgba(245,158,11,0.04)',  ring: 'rgba(245,158,11,0.24)',  glow: 'rgba(245,158,11,0.32)' },
};

/**
 * Splits a display value into an animatable number and its surrounding text,
 * so "65%", "12 min" and "1,240" all count up without the caller changing.
 * Returns null when there is no leading number to animate.
 */
function parseValue(value: string | number) {
  if (typeof value === 'number') return { prefix: '', n: value, suffix: '', decimals: 0 };
  const m = /^(\D*)(\d+(?:\.\d+)?)(.*)$/.exec(value);
  if (!m) return null;
  const [, prefix, digits, suffix] = m;
  const decimals = digits.includes('.') ? digits.split('.')[1].length : 0;
  return { prefix, n: parseFloat(digits), suffix, decimals };
}

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  accent = 'emerald',
  delay = 0,
}: StatCardProps) {
  const reduce = useReducedMotion();
  const a = ACCENTS[accent];
  const parsed = parseValue(value);

  // Some callers already put an arrow in the trend string; don't add a second.
  const hasArrow = trend ? /^[↑↓]/.test(trend.value.trim()) : false;

  return (
    <motion.div
      initial={reduce ? undefined : { opacity: 0, y: 16 }}
      animate={reduce ? undefined : { opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      whileHover={reduce ? undefined : { y: -4 }}
      className="glass-card lum-edge group relative flex items-start gap-4 p-5"
    >
      <div
        className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl transition-transform duration-500 group-hover:scale-105"
        style={{
          background: `linear-gradient(140deg, ${a.from}, ${a.to})`,
          boxShadow: `inset 0 0 0 1px ${a.ring}`,
          color: a.ink,
        }}
      >
        <span
          aria-hidden="true"
          className="absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100"
          style={{ boxShadow: `0 0 22px ${a.glow}` }}
        />
        {icon}
      </div>

      <div className="min-w-0 flex-1">
        <p className="text-xs font-semibold uppercase tracking-wider text-ink-400">{title}</p>
        <p className="mt-0.5 font-display text-2xl font-bold text-ink-900">
          {parsed ? (
            <>
              {parsed.prefix}
              <Counter to={parsed.n} decimals={parsed.decimals} duration={1.3} />
              {parsed.suffix}
            </>
          ) : (
            value
          )}
        </p>
        {subtitle && <p className="mt-1 text-xs text-ink-400">{subtitle}</p>}
        {trend && (
          <p
            className="mt-1 text-xs font-semibold"
            style={{ color: trend.positive ? '#0E4F3A' : '#C41E3F' }}
          >
            {hasArrow ? '' : trend.positive ? '↑ ' : '↓ '}
            {trend.value}
          </p>
        )}
      </div>
    </motion.div>
  );
}
