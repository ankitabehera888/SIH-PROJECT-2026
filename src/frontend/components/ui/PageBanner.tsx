import { motion } from 'framer-motion';

interface PageBannerProps {
  title?: string;
  subtitle?: string;
  image: string;
  className?: string;
}

/* Photo hero for content pages. The scrim is an explicit black gradient and
   the text explicit white (with drop-shadows), so it stays readable in both
   light and dark themes — the same lesson as the GenericPage quick-stats fix. */
export function PageBanner({ title, subtitle, image, className = '' }: PageBannerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative overflow-hidden rounded-2xl ${title ? 'h-32 sm:h-40' : 'h-20 sm:h-24'} ${className}`}
    >
      {/* Brand wash under the photo so a failed remote image still looks intentional. */}
      <div
        aria-hidden="true"
        className="absolute inset-0"
        style={{ background: 'linear-gradient(135deg, #0E4F3A, #17B366 62%, #0EA5C9)' }}
      />
      <img
        src={image}
        alt=""
        loading="lazy"
        decoding="async"
        className="absolute inset-0 w-full h-full object-cover"
        onError={(e) => { e.currentTarget.style.visibility = 'hidden'; }}
      />
      <div className="absolute inset-0 bg-gradient-to-r from-black/75 via-black/35 to-transparent" />
      {title && (
        <div className="relative h-full flex flex-col justify-end p-5 sm:p-6">
          <h1 className="text-xl sm:text-2xl font-bold text-white drop-shadow-md">{title}</h1>
          {subtitle && <p className="text-xs sm:text-sm text-white/85 mt-1 drop-shadow">{subtitle}</p>}
        </div>
      )}
    </motion.div>
  );
}
