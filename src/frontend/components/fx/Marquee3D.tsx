import type { ReactNode } from 'react';

interface Marquee3DProps {
  children: ReactNode;
  /** Seconds for one full loop. Lower = faster. */
  speed?: number;
  reverse?: boolean;
  className?: string;
  /** Tilts the strip in 3D so it reads as a rotating band, not a flat row. */
  tilt?: number;
}

/**
 * Infinite ticker on a 3D-tilted plane. The track is duplicated once and
 * translated -50%, which loops seamlessly without a JS scroll listener.
 *
 * Hovering pauses the track (CSS), so users can actually read an item they
 * want — an infinite marquee that cannot be stopped is a usability trap.
 */
export function Marquee3D({
  children,
  speed = 38,
  reverse = false,
  className = '',
  tilt = 0,
}: Marquee3DProps) {
  return (
    <div
      className={`marquee-mask overflow-hidden ${className}`}
      style={tilt ? { perspective: 900 } : undefined}
    >
      <div
        style={
          tilt
            ? { transform: `rotateX(${tilt}deg)`, transformStyle: 'preserve-3d' }
            : undefined
        }
      >
        <div
          className={`marquee-track ${reverse ? 'marquee-track-rev' : ''}`}
          style={{ animationDuration: `${speed}s` }}
        >
          {/* Duplicated for the seamless -50% loop; the copy is decorative. */}
          <div className="flex shrink-0">{children}</div>
          <div className="flex shrink-0" aria-hidden="true">{children}</div>
        </div>
      </div>
    </div>
  );
}
