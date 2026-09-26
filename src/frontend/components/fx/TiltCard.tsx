import { useRef, type ReactNode, type CSSProperties } from 'react';
import { motion, useMotionValue, useSpring, useTransform, useReducedMotion } from 'framer-motion';

interface TiltCardProps {
  children: ReactNode;
  className?: string;
  /** Max rotation in degrees on each axis. */
  strength?: number;
  /** How far the card lifts toward the viewer on hover, in px. */
  lift?: number;
  /** Adds the cursor-tracked radial spotlight. */
  spotlight?: boolean;
  /** Adds the iridescent top edge on hover. */
  edge?: boolean;
  style?: CSSProperties;
  onClick?: () => void;
  as?: 'div' | 'button' | 'article';
  ariaLabel?: string;
}

/**
 * Pointer-tracked 3D tilt with a spring return, plus an optional radial
 * spotlight driven by CSS custom properties (--mx / --my).
 *
 * The tilt is decoration only: it is skipped entirely under
 * prefers-reduced-motion, and pointer handlers never gate interaction, so
 * keyboard and touch users get the same card with the same click target.
 */
export function TiltCard({
  children,
  className = '',
  strength = 9,
  lift = 26,
  spotlight = true,
  edge = true,
  style,
  onClick,
  as = 'div',
  ariaLabel,
}: TiltCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();

  const px = useMotionValue(0.5);
  const py = useMotionValue(0.5);

  const spring = { stiffness: 220, damping: 22, mass: 0.5 };
  const rotateY = useSpring(useTransform(px, [0, 1], [-strength, strength]), spring);
  const rotateX = useSpring(useTransform(py, [0, 1], [strength, -strength]), spring);
  const z = useSpring(0, { stiffness: 260, damping: 26 });

  const handleMove = (e: React.PointerEvent<HTMLDivElement>) => {
    // Coarse pointers (touch) fire this on tap; tilting there just looks like a glitch.
    if (reduce || e.pointerType !== 'mouse') return;
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const nx = (e.clientX - r.left) / r.width;
    const ny = (e.clientY - r.top) / r.height;
    px.set(nx);
    py.set(ny);
    el.style.setProperty('--mx', `${nx * 100}%`);
    el.style.setProperty('--my', `${ny * 100}%`);
  };

  const handleEnter = (e: React.PointerEvent<HTMLDivElement>) => {
    if (reduce || e.pointerType !== 'mouse') return;
    z.set(lift);
  };

  const handleLeave = () => {
    px.set(0.5);
    py.set(0.5);
    z.set(0);
  };

  // Indexing `motion[as]` gives a union whose props intersect across all three
  // tags, which makes the div-typed ref and pointer handlers unassignable.
  // Resolve to one component and keep the div-shaped prop types.
  const MotionTag = (
    as === 'button' ? motion.button : as === 'article' ? motion.article : motion.div
  ) as typeof motion.div;

  return (
    <div className="stage-3d" style={{ perspective: 1000 }}>
      <MotionTag
        ref={ref}
        onPointerMove={handleMove}
        onPointerEnter={handleEnter}
        onPointerLeave={handleLeave}
        onClick={onClick}
        aria-label={ariaLabel}
        className={`${className} ${spotlight ? 'spotlight' : ''} ${edge ? 'lum-edge' : ''}`}
        style={{
          ...style,
          rotateX: reduce ? 0 : rotateX,
          rotateY: reduce ? 0 : rotateY,
          z: reduce ? 0 : z,
          transformStyle: 'preserve-3d',
        }}
      >
        {children}
      </MotionTag>
    </div>
  );
}
