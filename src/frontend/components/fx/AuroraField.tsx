interface AuroraFieldProps {
  /** Dial the whole field up or down. 1 = as designed. */
  intensity?: number;
  className?: string;
}

/**
 * Slow-drifting colour field behind light surfaces. Three large blurred
 * blobs in the vital spectrum (emerald / oxygen cyan / neural violet) keep a
 * pale page from reading as flat white.
 *
 * Purely decorative — aria-hidden, pointer-events none, and the drift stops
 * under prefers-reduced-motion via the global media query.
 */
export function AuroraField({ intensity = 1, className = '' }: AuroraFieldProps) {
  const blobs = [
    {
      color: 'rgba(23, 179, 102, 0.30)',
      size: '46vw',
      top: '-12%',
      left: '-8%',
      anim: 'animate-drift',
    },
    {
      color: 'rgba(14, 165, 201, 0.26)',
      size: '38vw',
      top: '18%',
      left: '68%',
      anim: 'animate-drift-slow',
    },
    {
      color: 'rgba(124, 92, 255, 0.20)',
      size: '42vw',
      top: '62%',
      left: '22%',
      anim: 'animate-drift',
    },
  ];

  return (
    <div
      aria-hidden="true"
      className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}
    >
      {blobs.map((b, i) => (
        <div
          key={i}
          className={`aurora-blob ${b.anim}`}
          style={{
            width: b.size,
            height: b.size,
            top: b.top,
            left: b.left,
            background: b.color,
            opacity: intensity,
            animationDelay: `${i * -7}s`,
          }}
        />
      ))}
    </div>
  );
}
