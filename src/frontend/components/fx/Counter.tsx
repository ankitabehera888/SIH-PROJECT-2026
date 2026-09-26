import { useEffect, useRef, useState } from 'react';
import { useInView, useReducedMotion } from 'framer-motion';

interface CounterProps {
  to: number;
  from?: number;
  /** Seconds. */
  duration?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  /** Insert thousands separators (Indian or Western grouping). */
  separator?: boolean;
}

const easeOutExpo = (t: number) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t));

/**
 * Counts up when scrolled into view. Uses requestAnimationFrame rather than
 * a transition so the intermediate values are real text (selectable, and
 * announced correctly once settled).
 */
export function Counter({
  to,
  from = 0,
  duration = 1.8,
  decimals = 0,
  prefix = '',
  suffix = '',
  className = '',
  separator = false,
}: CounterProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.5 });
  const reduce = useReducedMotion();
  const [value, setValue] = useState(reduce ? to : from);

  useEffect(() => {
    if (!inView || reduce) {
      if (reduce) setValue(to);
      return;
    }

    let raf = 0;
    const start = performance.now();
    const ms = duration * 1000;

    const tick = (now: number) => {
      const t = Math.min((now - start) / ms, 1);
      setValue(from + (to - from) * easeOutExpo(t));
      if (t < 1) raf = requestAnimationFrame(tick);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, reduce, to, from, duration]);

  const shown = separator
    ? value.toLocaleString('en-IN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })
    : value.toFixed(decimals);

  return (
    <span ref={ref} className={className} style={{ fontVariantNumeric: 'tabular-nums' }}>
      {prefix}
      {shown}
      {suffix}
    </span>
  );
}
