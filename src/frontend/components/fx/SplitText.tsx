import { motion, useReducedMotion } from 'framer-motion';

interface SplitTextProps {
  text: string;
  className?: string;
  /** Seconds before the first character animates. */
  delay?: number;
  /** Seconds between consecutive characters. */
  stagger?: number;
  /** 'chars' animates letter by letter, 'words' word by word. */
  by?: 'chars' | 'words';
  /**
   * Class applied to each animated unit rather than the wrapper. Needed for
   * gradient text: `background-clip: text` cannot paint through descendants
   * that carry their own transform, so the gradient must live on the same
   * element that moves.
   */
  unitClassName?: string;
  /** Play on mount instead of waiting for scroll. */
  immediate?: boolean;
  as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
}

/**
 * Kinetic per-character (or per-word) reveal. Characters rise out of a 3D
 * fold, which reads as depth rather than a plain fade.
 *
 * Accessibility: the animated glyphs are aria-hidden and the full string is
 * exposed once via aria-label, so screen readers read a sentence, not a
 * stream of single letters.
 */
export function SplitText({
  text,
  className = '',
  delay = 0,
  stagger = 0.028,
  by = 'chars',
  immediate = false,
  as = 'span',
  unitClassName,
}: SplitTextProps) {
  const reduce = useReducedMotion();
  const Tag = as;

  if (reduce) {
    return (
      <Tag className={className}>
        {unitClassName ? <span className={unitClassName}>{text}</span> : text}
      </Tag>
    );
  }

  const words = text.split(' ');
  let index = 0;

  const animateProp = immediate
    ? { animate: 'visible' as const }
    : { whileInView: 'visible' as const, viewport: { once: true, amount: 0.4 } };

  return (
    <Tag className={className} aria-label={text}>
      <motion.span
        aria-hidden="true"
        initial="hidden"
        {...animateProp}
        style={{ display: 'inline-block', perspective: 700 }}
      >
        {words.map((word, wi) => (
          <span
            key={wi}
            style={{ display: 'inline-block', whiteSpace: 'nowrap' }}
          >
            {(by === 'chars' ? word.split('') : [word]).map((unit) => {
              const i = index++;
              return (
                <motion.span
                  key={i}
                  className={unitClassName}
                  style={{ display: 'inline-block', transformOrigin: '50% 100%' }}
                  variants={{
                    hidden: { opacity: 0, y: '0.7em', rotateX: -72 },
                    visible: {
                      opacity: 1,
                      y: 0,
                      rotateX: 0,
                      transition: {
                        duration: 0.85,
                        delay: delay + i * stagger,
                        ease: [0.16, 1, 0.3, 1],
                      },
                    },
                  }}
                >
                  {unit}
                </motion.span>
              );
            })}
            {wi < words.length - 1 && <span>&nbsp;</span>}
          </span>
        ))}
      </motion.span>
    </Tag>
  );
}
