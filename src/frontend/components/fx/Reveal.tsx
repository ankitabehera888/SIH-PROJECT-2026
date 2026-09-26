import { motion, useReducedMotion } from 'framer-motion';
import type { ReactNode } from 'react';

type Direction = 'up' | 'down' | 'left' | 'right' | 'scale' | 'rise';

interface RevealProps {
  children: ReactNode;
  /** Seconds of stagger delay. */
  delay?: number;
  direction?: Direction;
  /** Travel distance in px. */
  distance?: number;
  className?: string;
  once?: boolean;
  /** Fraction of the element that must be visible to trigger. */
  amount?: number;
  as?: 'div' | 'section' | 'li' | 'span';
}

const offsets: Record<Direction, { x?: number; y?: number; scale?: number; rotateX?: number }> = {
  up: { y: 1 },
  down: { y: -1 },
  left: { x: 1 },
  right: { x: -1 },
  scale: { scale: 0.92 },
  rise: { y: 1, rotateX: 12 },
};

/**
 * Scroll-triggered entrance. Collapses to a no-op when the user has asked
 * for reduced motion, so content is never hidden behind an animation that
 * will not play.
 */
export function Reveal({
  children,
  delay = 0,
  direction = 'up',
  distance = 28,
  className = '',
  once = true,
  amount = 0.25,
  as = 'div',
}: RevealProps) {
  const reduce = useReducedMotion();
  const MotionTag = motion[as];

  if (reduce) {
    const Tag = as;
    return <Tag className={className}>{children}</Tag>;
  }

  const o = offsets[direction];

  return (
    <MotionTag
      className={className}
      initial={{
        opacity: 0,
        x: (o.x ?? 0) * distance,
        y: (o.y ?? 0) * distance,
        scale: o.scale ?? 1,
        rotateX: o.rotateX ?? 0,
      }}
      whileInView={{ opacity: 1, x: 0, y: 0, scale: 1, rotateX: 0 }}
      viewport={{ once, amount }}
      transition={{
        duration: 0.75,
        delay,
        ease: [0.16, 1, 0.3, 1],
      }}
      style={o.rotateX ? { transformPerspective: 900 } : undefined}
    >
      {children}
    </MotionTag>
  );
}
