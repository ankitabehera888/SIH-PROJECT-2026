import { motion, type Variants } from 'framer-motion';
import { ArrowLeft, ArrowRight, Calendar, FileText, Users, Clock, MapPin, Phone, Mail, Shield, Activity, Star } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useLanguage } from '../context/providers';

interface GenericPageProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  onBack?: () => void;
  actions?: { label: string; onClick: () => void }[];
  role?: 'doctor' | 'worker' | 'facility';
}

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

const imageReveal: Variants = {
  hidden: { opacity: 0, scale: 1.06 },
  visible: (i: number) => ({
    opacity: 1,
    scale: 1,
    transition: { duration: 0.8, delay: i * 0.12, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

const roleThemes: Record<string, {
  heroImage: string;
  bgImages: string[];
  features: { icon: typeof Calendar; title: string; desc: string; image: string }[];
  quickStats: { label: string; value: string; image: string }[];
  galleryImages: string[];
}> = {
  doctor: {
    heroImage: 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=1200&h=600&fit=crop&auto=format',
    bgImages: [
      'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&h=300&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1551076805-e1869033e561?w=400&h=300&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=400&h=300&fit=crop&auto=format',
    ],
    features: [
      { icon: Users, title: 'Patient Management', desc: 'Access complete patient histories, vitals, and treatment records in one place.', image: 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=600&h=400&fit=crop&auto=format' },
      { icon: Calendar, title: 'Schedule & Appointments', desc: 'Manage your consultation schedule with smart reminders and conflict detection.', image: 'https://images.unsplash.com/photo-1581056771107-24ca5f033842?w=600&h=400&fit=crop&auto=format' },
      { icon: Activity, title: 'Clinical Analytics', desc: 'Track patient outcomes, referral success rates, and consultation metrics.', image: 'https://images.unsplash.com/photo-1551076805-e1869033e561?w=600&h=400&fit=crop&auto=format' },
      { icon: FileText, title: 'Digital Prescriptions', desc: 'Create and send digital prescriptions directly to connected pharmacies.', image: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600&h=400&fit=crop&auto=format' },
    ],
    quickStats: [
      { label: 'Patients Today', value: '24', image: 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=400&h=300&fit=crop&auto=format' },
      { label: 'Consultations', value: '8', image: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&h=300&fit=crop&auto=format' },
      { label: 'Referrals Sent', value: '3', image: 'https://images.unsplash.com/photo-1584515933487-779824d29309?w=400&h=300&fit=crop&auto=format' },
    ],
    galleryImages: [
      'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=500&h=400&fit=crop&auto=format',
    ],
  },
  worker: {
    heroImage: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=1200&h=600&fit=crop&auto=format',
    bgImages: [
      'https://images.unsplash.com/photo-1584515933487-779824d29309?w=400&h=300&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=400&h=300&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=400&h=300&fit=crop&auto=format',
    ],
    features: [
      { icon: Users, title: 'Patient Registration', desc: 'Register new patients in your community with complete intake profiles.', image: 'https://images.unsplash.com/photo-1584515933487-779824d29309?w=600&h=400&fit=crop&auto=format' },
      { icon: MapPin, title: 'Facility Finder', desc: 'Locate the nearest healthcare facilities with real-time availability.', image: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=600&h=400&fit=crop&auto=format' },
      { icon: Phone, title: 'Community Outreach', desc: 'Connect with patients through phone and messaging for follow-ups.', image: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=600&h=400&fit=crop&auto=format' },
      { icon: Shield, title: 'Referral Coordination', desc: 'Create and track referrals from community to specialist care.', image: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600&h=400&fit=crop&auto=format' },
    ],
    quickStats: [
      { label: 'Patients Registered', value: '156', image: 'https://images.unsplash.com/photo-1584515933487-779824d29309?w=400&h=300&fit=crop&auto=format' },
      { label: 'Visits This Week', value: '42', image: 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=400&h=300&fit=crop&auto=format' },
      { label: 'Active Referrals', value: '12', image: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=400&h=300&fit=crop&auto=format' },
    ],
    galleryImages: [
      'https://images.unsplash.com/photo-1584515933487-779824d29309?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=500&h=400&fit=crop&auto=format',
    ],
  },
  facility: {
    heroImage: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1200&h=600&fit=crop&auto=format',
    bgImages: [
      'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=400&h=300&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=400&h=300&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=300&fit=crop&auto=format',
    ],
    features: [
      { icon: Users, title: 'Patient Management', desc: 'Track incoming patients, bed availability, and treatment progress.', image: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=600&h=400&fit=crop&auto=format' },
      { icon: Shield, title: 'Referral Handling', desc: 'Accept and manage inbound referrals from community health workers.', image: 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=600&h=400&fit=crop&auto=format' },
      { icon: Activity, title: 'Operations Dashboard', desc: 'Monitor facility performance, resource utilization, and wait times.', image: 'https://images.unsplash.com/photo-1581056771107-24ca5f033842?w=600&h=400&fit=crop&auto=format' },
      { icon: FileText, title: 'Inventory Tracking', desc: 'Manage medicine and supply inventory with automatic reorder alerts.', image: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600&h=400&fit=crop&auto=format' },
    ],
    quickStats: [
      { label: 'Bed Occupancy', value: '78%', image: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=400&h=300&fit=crop&auto=format' },
      { label: 'Patients Today', value: '89', image: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=400&h=300&fit=crop&auto=format' },
      { label: 'Staff On Duty', value: '34', image: 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=300&fit=crop&auto=format' },
    ],
    galleryImages: [
      'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=500&h=400&fit=crop&auto=format',
      'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=500&h=400&fit=crop&auto=format',
    ],
  },
};

export function GenericPage({ title, description, icon, onBack, actions, role = 'doctor' }: GenericPageProps) {
  const theme = roleThemes[role] || roleThemes.doctor;
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      {onBack && (
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-gray-500 hover:text-sahaay-deep transition-colors">
          <ArrowLeft size={16} /> {t('common.back')} {t('dash.overview')}
        </button>
      )}

      {/* Hero banner with image */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl h-56 lg:h-72"
      >
        <img
          src={theme.heroImage}
          alt={title}
          className="w-full h-full object-cover img-ken-burns"
          loading="eager"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-sahaay-deep/85 via-sahaay-deep/60 to-transparent" />
        <div className="absolute inset-0 flex items-end p-6 lg:p-8">
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center text-white">
                {icon || <Shield size={24} />}
              </div>
              <div>
                <h1 className="text-2xl lg:text-3xl font-bold text-white">{title}</h1>
                <p className="text-sahaay-50/80 text-sm mt-0.5">{description}</p>
              </div>
            </div>
            {actions && (
              <div className="flex gap-3 mt-4">
                {actions.map((action, i) => (
                  <Button key={i} onClick={action.onClick} className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30">
                    {action.label} <ArrowRight size={14} className="inline ml-1" />
                  </Button>
                ))}
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Quick stats with images */}
      <motion.div
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 sm:grid-cols-3 gap-4"
      >
        {theme.quickStats.map((stat, i) => (
          <motion.div
            key={i}
            variants={fadeUp}
            custom={i}
            className="glass-card-elevated overflow-hidden group"
          >
            <div className="relative h-24 overflow-hidden">
              <img
                src={stat.image}
                alt={stat.label}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105 img-faded-wash"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/35 to-transparent" />
              <div className="absolute bottom-2 left-3 right-3">
                <p className="text-2xl font-bold text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.6)]">{stat.value}</p>
                <p className="text-xs text-white/85 font-medium drop-shadow-[0_1px_2px_rgba(0,0,0,0.6)]">{stat.label}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Feature cards with images */}
      <motion.div
        initial="hidden"
        animate="visible"
        className="grid md:grid-cols-2 gap-4"
      >
        {theme.features.map((feature, i) => {
          const Icon = feature.icon;
          return (
            <motion.div
              key={i}
              variants={fadeUp}
              custom={i + 3}
              className="glass-card-elevated overflow-hidden group hover:-translate-y-0.5 transition-transform duration-300"
            >
              <div className="relative h-36 overflow-hidden">
                <img
                  src={feature.image}
                  alt={feature.title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-white via-white/40 to-transparent" />
                <div className="absolute bottom-3 left-3 w-10 h-10 rounded-xl bg-white/90 backdrop-blur-sm flex items-center justify-center text-sahaay-deep shadow-md">
                  <Icon size={18} />
                </div>
              </div>
              <div className="p-5">
                <h3 className="text-base font-bold text-gray-900 mb-1.5">{feature.title}</h3>
                <p className="text-sm text-gray-600 leading-relaxed">{feature.desc}</p>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Image gallery mosaic */}
      <motion.div
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
      >
        <h3 className="text-lg font-bold text-gray-900 mb-4">Healthcare Gallery</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {theme.galleryImages.map((src, i) => (
            <motion.div
              key={i}
              variants={imageReveal}
              custom={i}
              className="rounded-2xl overflow-hidden aspect-[4/3] img-shimmer group"
            >
              <img
                src={src}
                alt={`Healthcare ${i + 1}`}
                className="w-full h-full object-cover img-zoom-hover img-faded-wash transition-all duration-500 group-hover:brightness-110"
                loading="lazy"
              />
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Info cards row */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="grid grid-cols-2 md:grid-cols-4 gap-3"
      >
        {[
          { icon: Phone, label: 'Emergency Helpline', value: '108' },
          { icon: Mail, label: 'Support Email', value: 'help@sahaay.in' },
          { icon: Clock, label: 'Available', value: '24/7' },
          { icon: Star, label: 'Rating', value: '4.8/5.0' },
        ].map((item, i) => {
          const Icon = item.icon;
          return (
            <div key={i} className="glass-card p-4 text-center">
              <div className="w-10 h-10 rounded-xl bg-sahaay-deep/8 flex items-center justify-center text-sahaay-deep mx-auto mb-2">
                <Icon size={18} />
              </div>
              <p className="text-xs text-gray-500 font-medium">{item.label}</p>
              <p className="text-sm font-bold text-gray-900 mt-0.5">{item.value}</p>
            </div>
          );
        })}
      </motion.div>

      {/* Bottom CTA with image background */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="relative overflow-hidden rounded-2xl h-40"
      >
        <img
          src={theme.bgImages[0]}
          alt=""
          className="w-full h-full object-cover"
          loading="lazy"
        />
        <div className="absolute inset-0 sahaay-gradient-deep opacity-85" />
        <div className="absolute inset-0 flex items-center justify-center text-center px-6">
          <div>
            <h3 className="text-xl font-bold text-white mb-2">Need assistance with {title.toLowerCase()}?</h3>
            <p className="text-sahaay-50/80 text-sm mb-4">Our support team is here to help you get started.</p>
            <button className="px-6 py-2.5 bg-white text-sahaay-deep font-bold rounded-xl hover:bg-sahaay-50 transition-colors text-sm">
              Contact Support
            </button>
          </div>
        </div>
      </motion.div>

      {/* Bottom padding for mobile nav */}
      <div className="h-4 lg:hidden" />
    </div>
  );
}
