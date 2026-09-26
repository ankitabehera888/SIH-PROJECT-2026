import { useEffect, useRef } from 'react';
import { useReducedMotion } from 'framer-motion';

interface VitalsCanvasProps {
  className?: string;
  /** Beats per minute for the ECG sweep. */
  bpm?: number;
  /** Draw the constellation particle field. */
  particles?: boolean;
  /** Draw the rolling ECG trace. */
  ecg?: boolean;
  /** Global opacity multiplier, 0-1. */
  intensity?: number;
}

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  r: number;
  hue: [number, number, number];
}

const PALETTE: [number, number, number][] = [
  [23, 179, 102],  // emerald
  [14, 165, 201],  // oxygen cyan
  [124, 92, 255],  // neural violet
];

const gauss = (t: number, mu: number, s: number) =>
  Math.exp(-((t - mu) ** 2) / (2 * s * s));

/**
 * One cardiac cycle, normalised to roughly [-0.3, 1].
 * Sum of Gaussians approximating the P-Q-R-S-T complex — the shape is what
 * makes it read as a real monitor rather than a decorative squiggle.
 */
function beat(t: number): number {
  return (
    0.13 * gauss(t, 0.15, 0.024) -   // P wave
    0.10 * gauss(t, 0.246, 0.008) +  // Q
    1.00 * gauss(t, 0.272, 0.009) -  // R spike
    0.30 * gauss(t, 0.301, 0.012) +  // S
    0.27 * gauss(t, 0.45, 0.040)     // T wave
  );
}

/**
 * Living vitals backdrop: a rolling ECG sweep plus a constellation particle
 * field that leans toward the pointer.
 *
 * Everything is decorative (aria-hidden). The rAF loop is suspended whenever
 * the canvas leaves the viewport, and under prefers-reduced-motion a single
 * static frame is drawn instead of looping.
 */
export function VitalsCanvas({
  className = '',
  bpm = 68,
  particles = true,
  ecg = true,
  intensity = 1,
}: VitalsCanvasProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const reduce = useReducedMotion();

  useEffect(() => {
    const wrap = wrapRef.current;
    const canvas = canvasRef.current;
    if (!wrap || !canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let w = 0;
    let h = 0;
    let dpr = 1;

    const pts: Particle[] = [];
    let trace: number[] = [];
    const STEP = 3;          // px between ECG samples
    let phase = 0;
    let raf = 0;
    let running = true;
    let last = performance.now();

    const pointer = { x: -9999, y: -9999, active: false };

    function resize() {
      const r = wrap!.getBoundingClientRect();
      w = Math.max(1, Math.round(r.width));
      h = Math.max(1, Math.round(r.height));
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas!.width = w * dpr;
      canvas!.height = h * dpr;
      canvas!.style.width = `${w}px`;
      canvas!.style.height = `${h}px`;
      ctx!.setTransform(dpr, 0, 0, dpr, 0, 0);

      // Particle count scales with area but is hard-capped for weak GPUs.
      const target = Math.min(72, Math.round((w * h) / 16000));
      pts.length = 0;
      for (let i = 0; i < target; i++) {
        pts.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.22,
          vy: (Math.random() - 0.5) * 0.22,
          r: 1 + Math.random() * 2.2,
          hue: PALETTE[Math.floor(Math.random() * PALETTE.length)],
        });
      }

      const cols = Math.ceil(w / STEP) + 2;
      trace = new Array(cols).fill(0);
    }

    function drawParticles() {
      // Constellation links first so dots sit on top of their own lines.
      for (let i = 0; i < pts.length; i++) {
        for (let j = i + 1; j < pts.length; j++) {
          const dx = pts[i].x - pts[j].x;
          const dy = pts[i].y - pts[j].y;
          const d2 = dx * dx + dy * dy;
          if (d2 > 15000) continue;
          const a = (1 - Math.sqrt(d2) / 122) * 0.20 * intensity;
          if (a <= 0) continue;
          ctx!.strokeStyle = `rgba(14, 79, 58, ${a})`;
          ctx!.lineWidth = 0.7;
          ctx!.beginPath();
          ctx!.moveTo(pts[i].x, pts[i].y);
          ctx!.lineTo(pts[j].x, pts[j].y);
          ctx!.stroke();
        }
      }

      for (const p of pts) {
        const [r, g, b] = p.hue;
        const grd = ctx!.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 5);
        grd.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${0.55 * intensity})`);
        grd.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
        ctx!.fillStyle = grd;
        ctx!.beginPath();
        ctx!.arc(p.x, p.y, p.r * 5, 0, Math.PI * 2);
        ctx!.fill();

        ctx!.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.75 * intensity})`;
        ctx!.beginPath();
        ctx!.arc(p.x, p.y, p.r * 0.62, 0, Math.PI * 2);
        ctx!.fill();
      }
    }

    function stepParticles(dt: number) {
      for (const p of pts) {
        p.x += p.vx * dt;
        p.y += p.vy * dt;

        if (pointer.active) {
          const dx = pointer.x - p.x;
          const dy = pointer.y - p.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < 40000 && d2 > 1) {
            const f = (1 - Math.sqrt(d2) / 200) * 0.05;
            p.vx += (dx / Math.sqrt(d2)) * f;
            p.vy += (dy / Math.sqrt(d2)) * f;
          }
        }

        // Friction keeps pointer nudges from compounding into chaos.
        p.vx *= 0.994;
        p.vy *= 0.994;

        if (p.x < -20) p.x = w + 20;
        if (p.x > w + 20) p.x = -20;
        if (p.y < -20) p.y = h + 20;
        if (p.y > h + 20) p.y = -20;
      }
    }

    function drawEcg() {
      const mid = h * 0.62;
      const amp = Math.min(h * 0.26, 96);
      const n = trace.length;

      // Trailing gradient: the newest samples are brightest.
      ctx!.lineJoin = 'round';
      ctx!.lineCap = 'round';

      const grad = ctx!.createLinearGradient(0, 0, w, 0);
      grad.addColorStop(0, `rgba(23, 179, 102, 0)`);
      grad.addColorStop(0.35, `rgba(23, 179, 102, ${0.22 * intensity})`);
      grad.addColorStop(0.8, `rgba(23, 179, 102, ${0.6 * intensity})`);
      grad.addColorStop(1, `rgba(14, 165, 201, ${0.9 * intensity})`);

      ctx!.save();
      ctx!.shadowColor = `rgba(23, 179, 102, ${0.55 * intensity})`;
      ctx!.shadowBlur = 14;
      ctx!.strokeStyle = grad;
      ctx!.lineWidth = 2.1;
      ctx!.beginPath();
      for (let i = 0; i < n; i++) {
        const x = i * STEP;
        const y = mid - trace[i] * amp;
        if (i === 0) ctx!.moveTo(x, y);
        else ctx!.lineTo(x, y);
      }
      ctx!.stroke();
      ctx!.restore();

      // Leading indicator dot at the sweep head.
      const hx = (n - 1) * STEP;
      const hy = mid - trace[n - 1] * amp;
      const hg = ctx!.createRadialGradient(hx, hy, 0, hx, hy, 16);
      hg.addColorStop(0, `rgba(255, 255, 255, ${0.95 * intensity})`);
      hg.addColorStop(0.3, `rgba(23, 179, 102, ${0.8 * intensity})`);
      hg.addColorStop(1, 'rgba(23, 179, 102, 0)');
      ctx!.fillStyle = hg;
      ctx!.beginPath();
      ctx!.arc(hx, hy, 16, 0, Math.PI * 2);
      ctx!.fill();
    }

    function frame(now: number) {
      if (!running) return;
      // Clamp dt so a backgrounded tab does not fast-forward the sim.
      const dt = Math.min((now - last) / 16.67, 3);
      last = now;

      ctx!.clearRect(0, 0, w, h);

      if (particles) {
        stepParticles(dt);
        drawParticles();
      }

      if (ecg) {
        const beatsPerSec = bpm / 60;
        const secPerFrame = (dt * 16.67) / 1000;
        phase = (phase + beatsPerSec * secPerFrame) % 1;
        trace.shift();
        trace.push(beat(phase));
        drawEcg();
      }

      raf = requestAnimationFrame(frame);
    }

    function drawStatic() {
      ctx!.clearRect(0, 0, w, h);
      if (particles) drawParticles();
      if (ecg) {
        for (let i = 0; i < trace.length; i++) {
          trace[i] = beat((i / (trace.length / 3)) % 1);
        }
        drawEcg();
      }
    }

    resize();

    const ro = new ResizeObserver(() => {
      resize();
      if (reduce) drawStatic();
    });
    ro.observe(wrap);

    const onPointer = (e: PointerEvent) => {
      const r = wrap!.getBoundingClientRect();
      pointer.x = e.clientX - r.left;
      pointer.y = e.clientY - r.top;
      pointer.active = e.pointerType === 'mouse';
    };
    const onLeave = () => { pointer.active = false; };

    if (reduce) {
      drawStatic();
    } else {
      window.addEventListener('pointermove', onPointer, { passive: true });
      window.addEventListener('pointerleave', onLeave);

      // Suspend the loop while scrolled away — no wasted frames, no heat.
      const io = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting && !running) {
            running = true;
            last = performance.now();
            raf = requestAnimationFrame(frame);
          } else if (!entry.isIntersecting && running) {
            running = false;
            cancelAnimationFrame(raf);
          }
        },
        { threshold: 0 },
      );
      io.observe(wrap);

      raf = requestAnimationFrame(frame);

      return () => {
        running = false;
        cancelAnimationFrame(raf);
        ro.disconnect();
        io.disconnect();
        window.removeEventListener('pointermove', onPointer);
        window.removeEventListener('pointerleave', onLeave);
      };
    }

    return () => {
      running = false;
      cancelAnimationFrame(raf);
      ro.disconnect();
    };
  }, [bpm, particles, ecg, intensity, reduce]);

  return (
    <div ref={wrapRef} aria-hidden="true" className={`pointer-events-none ${className}`}>
      <canvas ref={canvasRef} className="block h-full w-full" />
    </div>
  );
}
