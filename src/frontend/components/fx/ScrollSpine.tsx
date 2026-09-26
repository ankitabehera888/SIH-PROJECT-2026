import { useEffect, useState } from 'react';
import { motion, useScroll, useSpring, useTransform, useReducedMotion } from 'framer-motion';

export interface SpineSection {
  id: string;
  label: string;
}

interface ScrollSpineProps {
  sections: SpineSection[];
}

/**
 * Fixed vertical progress rail with clickable section jumps.
 *
 * Desktop-only by design: on small screens a fixed side rail steals thumb
 * space and overlaps content. The labels expand on hover/focus so the rail is
 * never a row of unlabelled dots.
 */
export function ScrollSpine({ sections }: ScrollSpineProps) {
  const reduce = useReducedMotion();
  const [active, setActive] = useState(0);
  const { scrollYProgress } = useScroll();
  const smooth = useSpring(scrollYProgress, { stiffness: 120, damping: 30, mass: 0.3 });
  const fill = useTransform(smooth, [0, 1], [0, 1]);

  useEffect(() => {
    const nodes = sections
      .map((s) => document.getElementById(s.id))
      .filter((n): n is HTMLElement => Boolean(n));
    if (!nodes.length) return;

    const io = new IntersectionObserver(
      (entries) => {
        // Pick the entry closest to the top third of the viewport.
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (!visible.length) return;
        const idx = sections.findIndex((s) => s.id === visible[0].target.id);
        if (idx >= 0) setActive(idx);
      },
      { rootMargin: '-30% 0px -55% 0px', threshold: 0 },
    );

    nodes.forEach((n) => io.observe(n));
    return () => io.disconnect();
  }, [sections]);

  const jump = (id: string) => {
    document.getElementById(id)?.scrollIntoView({
      behavior: reduce ? 'auto' : 'smooth',
      block: 'start',
    });
  };

  return (
    <nav
      aria-label="Page sections"
      className="fixed right-5 top-1/2 z-40 hidden -translate-y-1/2 lg:block"
    >
      <div className="relative flex flex-col items-end gap-1">
        {/* Rail */}
        <div className="pointer-events-none absolute right-[6px] top-2 bottom-2 w-[2px] rounded-full bg-ink-200/70">
          <motion.div
            className="holo-line h-full w-full origin-top rounded-full"
            style={{ scaleY: fill }}
          />
        </div>

        {sections.map((s, i) => {
          const on = i === active;
          return (
            <button
              key={s.id}
              onClick={() => jump(s.id)}
              aria-current={on}
              className="group relative flex items-center gap-2.5 py-1.5 pl-2 pr-0"
            >
              <span
                className={`whitespace-nowrap rounded-full px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.14em] transition-all duration-300 ${
                  on
                    ? 'bg-white/90 text-sahaay-deep opacity-100 shadow-[var(--shadow-1)]'
                    : 'bg-white/80 text-ink-500 opacity-0 shadow-[var(--shadow-1)] group-hover:opacity-100 group-focus-visible:opacity-100'
                }`}
              >
                {s.label}
              </span>

              <span className="relative flex h-3.5 w-3.5 items-center justify-center">
                {on && !reduce && (
                  <motion.span
                    layoutId="spine-halo"
                    className="absolute inset-0 rounded-full"
                    style={{ background: 'rgba(23,179,102,0.22)' }}
                    transition={{ type: 'spring', stiffness: 320, damping: 26 }}
                  />
                )}
                <span
                  className={`relative rounded-full transition-all duration-300 ${
                    on ? 'h-[7px] w-[7px] bg-sahaay-500' : 'h-[5px] w-[5px] bg-ink-300 group-hover:bg-sahaay-400'
                  }`}
                />
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
