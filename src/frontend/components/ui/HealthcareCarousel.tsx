'use client';
import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/* Each slide carries a `wash`: a two-stop brand gradient drawn behind the
   photo. Remote images are the one part of this app that can fail on a venue's
   wifi — when they do, the panel now falls back to an on-brand colour field
   with the caption still legible, instead of a white rectangle. */
const slides = [
  {
    image: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=900&h=700&fit=crop&auto=format',
    wash: 'linear-gradient(150deg, #0E4F3A, #17B366 62%, #0EA5C9)',
    title: 'Connected Care',
    subtitle: 'Every step of your healthcare journey, tracked and coordinated.',
  },
  {
    image: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=900&h=700&fit=crop&auto=format',
    wash: 'linear-gradient(150deg, #0B3F2E, #0EA5C9 58%, #17B366)',
    title: 'Community Health',
    subtitle: 'Bridging rural health centers with specialist care.',
  },
  {
    image: 'https://images.unsplash.com/photo-1581056771107-24ca5f033842?w=900&h=700&fit=crop&auto=format',
    wash: 'linear-gradient(150deg, #123F63, #7C5CFF 60%, #17B366)',
    title: 'Digital Records',
    subtitle: 'Your health timeline travels with you, everywhere.',
  },
  {
    image: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=900&h=700&fit=crop&auto=format',
    wash: 'linear-gradient(150deg, #0E4F3A, #F59E0B 68%, #17B366)',
    title: 'Smart Facilities',
    subtitle: 'Find the right facility, doctor, and diagnostics near you.',
  },
  {
    image: 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=900&h=700&fit=crop&auto=format',
    wash: 'linear-gradient(150deg, #0B3F2E, #17B366 55%, #7C5CFF)',
    title: 'Expert Doctors',
    subtitle: 'Consult with specialists through video and in-person visits.',
  },
];

interface HealthcareCarouselProps {
  variant?: 'hero' | 'login';
}

export function HealthcareCarousel({ variant = 'hero' }: HealthcareCarouselProps) {
  const [current, setCurrent] = useState(0);

  const advance = useCallback(() => {
    setCurrent((prev) => (prev + 1) % slides.length);
  }, []);

  useEffect(() => {
    const timer = setInterval(advance, variant === 'hero' ? 5000 : 4000);
    return () => clearInterval(timer);
  }, [advance, variant]);

  const slide = slides[current];

  if (variant === 'login') {
    return (
      <div className="absolute inset-0 overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={current}
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
            className="absolute inset-0"
          >
            {/* Brand wash underneath: visible while the photo streams in, and
                the whole panel if the photo never arrives. */}
            <div aria-hidden="true" className="absolute inset-0" style={{ background: slide.wash }} />
            <img
              src={slide.image}
              alt={slide.title}
              className="relative h-full w-full object-cover"
              loading="lazy"
              decoding="async"
              onError={(e) => { e.currentTarget.style.visibility = 'hidden'; }}
            />
          </motion.div>
        </AnimatePresence>

        {/* Gradient overlays */}
        <div className="absolute inset-0 bg-gradient-to-t from-sahaay-950/80 via-sahaay-950/30 to-transparent" />
        <div className="absolute inset-0 bg-sahaay-deep/20" />

        {/* Content overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-8 lg:p-12">
          <AnimatePresence mode="wait">
            <motion.div
              key={current}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <p className="text-sahaay-300 text-sm font-semibold tracking-wide uppercase mb-2">
                {slide.title}
              </p>
              <p className="text-white/80 text-base max-w-xs leading-relaxed">
                {slide.subtitle}
              </p>
            </motion.div>
          </AnimatePresence>

          {/* Dots. The hit area is 44px tall via padding while the visible bar
              stays 1.5px — icon-sized targets were unusable on touch, and the
              buttons carried no accessible name at all. */}
          <div className="mt-4 flex gap-2">
            {slides.map((s, i) => (
              <button
                key={i}
                onClick={() => setCurrent(i)}
                aria-label={`Show slide ${i + 1}: ${s.title}`}
                aria-current={i === current ? 'true' : undefined}
                className="group flex h-11 items-center py-[21px]"
              >
                <span
                  aria-hidden="true"
                  className={`h-1.5 rounded-full transition-all duration-500 ${
                    i === current ? 'w-8 bg-white' : 'w-1.5 bg-white/30 group-hover:bg-white/60'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Hero variant
  return (
    <div className="relative w-full h-full min-h-[400px] lg:min-h-[500px]">
      <AnimatePresence mode="wait">
        <motion.div
          key={current}
          initial={{ opacity: 0, scale: 1.08 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
          className="absolute inset-0 rounded-3xl overflow-hidden"
        >
          <div aria-hidden="true" className="absolute inset-0" style={{ background: slide.wash }} />
          <img
            src={slide.image}
            alt={slide.title}
            className="relative h-full w-full object-cover"
            loading="eager"
            decoding="async"
            onError={(e) => { e.currentTarget.style.visibility = 'hidden'; }}
          />
          {/* Soft vignette overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-sahaay-deep/10 via-transparent to-sahaay-950/20" />
        </motion.div>
      </AnimatePresence>

      {/* Floating caption card */}
      <div className="absolute bottom-6 left-6 right-6 lg:left-8 lg:right-auto lg:max-w-sm">
        <AnimatePresence mode="wait">
          <motion.div
            key={current}
            initial={{ opacity: 0, y: 16, filter: 'blur(8px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -8, filter: 'blur(4px)' }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="bg-white/80 backdrop-blur-xl rounded-2xl p-5 border border-white/40 shadow-[0_8px_32px_rgba(31,104,73,0.12)]"
          >
            <p className="text-sahaay-deep text-xs font-bold tracking-wider uppercase mb-1">
              {slide.title}
            </p>
            <p className="text-gray-700 text-sm leading-relaxed">
              {slide.subtitle}
            </p>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Progress indicators */}
      <div className="absolute right-4 top-4 flex flex-col">
        {slides.map((s, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            aria-label={`Show slide ${i + 1}: ${s.title}`}
            aria-current={i === current ? 'true' : undefined}
            className="group flex h-11 w-11 items-center justify-center"
          >
            <span
              aria-hidden="true"
              className={`rounded-full transition-all duration-500 ${
                i === current
                  ? 'h-2.5 w-2.5 bg-sahaay-deep shadow-[0_0_8px_rgba(31,104,73,0.4)]'
                  : 'h-2 w-2 bg-white/60 group-hover:bg-white'
              }`}
            />
          </button>
        ))}
      </div>
    </div>
  );
}
