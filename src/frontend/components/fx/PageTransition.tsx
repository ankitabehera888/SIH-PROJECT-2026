import type { ReactNode } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';

interface PageTransitionProps {
  /** Change this to trigger the transition — typically the current route. */
  routeKey: string;
  children: ReactNode;
}

/**
 * Route-change choreography: a crossfade of the whole view plus a thin emerald
 * sweep across the top, so navigation reads as a deliberate change rather than
 * a flash.
 *
 * `mode="wait"` guarantees only one view is mounted at a time, so the app never
 * shows two dashboards stacked mid-transition.
 *
 * IMPORTANT — this wrapper animates `opacity` only, deliberately. A non-`none`
 * `transform` or `filter` on an element makes it the containing block for every
 * `position: fixed` descendant, which would tear the fixed nav, the sidebar and
 * the scroll rail out of the viewport and pin them to this div. Opacity creates
 * a stacking context but not a containing block, so it is safe. The rise-and-
 * settle motion is supplied by each page's own entrance animations instead.
 */
export function PageTransition({ routeKey, children }: PageTransitionProps) {
  const reduce = useReducedMotion();

  if (reduce) return <>{children}</>;

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={routeKey}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0, transition: { duration: 0.1, ease: 'easeOut' } }}
        /* 0.28s in AND 0.28s out (mode="wait") made every navigation feel like
           a page load. Snappier fade + fast exit keeps the polish without the
           dead time. */
        transition={{ duration: 0.16, ease: [0.16, 1, 0.3, 1] }}
      >
        {/* Sweep: reads as the new screen "loading in" without a fake spinner */}
        <motion.div
          aria-hidden="true"
          className="holo-line pointer-events-none fixed inset-x-0 top-0 z-[60] h-[2px] origin-left"
          initial={{ scaleX: 0, opacity: 1 }}
          animate={{ scaleX: 1, opacity: 0 }}
          transition={{ duration: 0.62, ease: [0.16, 1, 0.3, 1] }}
        />
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
