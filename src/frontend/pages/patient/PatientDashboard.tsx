import { motion } from 'framer-motion';
import {
  Calendar, ClipboardList, Stethoscope, Heart, MapPin, Clock, Video, FileText,
  Search, Activity, AlertCircle, ChevronRight, Users, Mic, Upload
} from 'lucide-react';
import { StatCard } from '../../components/ui/StatCard';
import { CareJourney } from '../../components/ui/CareJourney';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { facilities } from '../../../mock-data/mockData';
import { useTimeGreeting } from '../../hooks/useTimeGreeting';
import { useLanguage } from '../../context/providers';
import { useUserProfile } from '../../context/providers';

interface PatientDashboardProps {
  onNavigate: (route: string) => void;
}

export function PatientDashboard({ onNavigate }: PatientDashboardProps) {
  const { t } = useLanguage();
  const { greeting, Icon: TimeIcon, tint } = useTimeGreeting();
  const { firstName } = useUserProfile();

  const journeySteps = [
    { label: t('dash.registration'), status: 'completed' as const, date: 'Aug 1' },
    { label: t('dash.initialAssessment'), status: 'completed' as const, date: 'Aug 5' },
    { label: t('dash.phcConsultation'), status: 'completed' as const, date: 'Aug 12' },
    { label: t('dash.diagnosticsJourney'), status: 'current' as const },
    { label: t('dash.treatment'), status: 'upcoming' as const },
    { label: t('dash.followupJourney'), status: 'upcoming' as const },
  ];
  const journeyCompleted = journeySteps.filter((s) => s.status === 'completed').length;
  const journeyTotal = journeySteps.length;
  const journeyPercent = Math.round((journeyCompleted / journeyTotal) * 100);

  const quickActions = [
    { icon: Stethoscope, label: t('dash.symptomChecker'), route: '/patient/symptom-checker', color: 'from-sahaay-deep/15 to-sahaay-500/8', textColor: 'text-sahaay-deep' },
    { icon: Mic, label: t('dash.aiAssistant'), route: '/patient/ai-assistant', color: 'from-emerald-500/12 to-emerald-400/5', textColor: 'text-emerald-600' },
    { icon: Activity, label: t('dash.myVitals'), route: '/patient/vitals', color: 'from-red-500/10 to-red-400/5', textColor: 'text-red-500' },
    { icon: Upload, label: t('dash.labReports'), route: '/patient/lab-reports', color: 'from-blue-500/10 to-blue-400/5', textColor: 'text-blue-500' },
    { icon: Calendar, label: t('dash.bookAppointment'), route: '/patient/appointments', color: 'from-violet-500/10 to-violet-400/5', textColor: 'text-violet-600' },
    { icon: Search, label: t('dash.findDoctor'), route: '/patient/facilities', color: 'from-amber-500/10 to-amber-400/5', textColor: 'text-amber-600' },
    { icon: Video, label: t('dash.videoConsultation'), route: '/patient/consultation', color: 'from-purple-500/10 to-purple-400/5', textColor: 'text-purple-600' },
    { icon: FileText, label: t('dash.healthRecords'), route: '/patient/records', color: 'from-teal-500/10 to-teal-400/5', textColor: 'text-teal-600' },
  ];

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden glass-card-elevated p-6 lg:p-8"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-sahaay-200/30 to-transparent rounded-full blur-3xl -translate-y-1/3 translate-x-1/3" />
        <img
          src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80"
          alt=""
          loading="lazy"
          className="pointer-events-none absolute inset-y-0 right-0 hidden w-2/5 object-cover opacity-20 lg:block [mask-image:linear-gradient(to_left,black_35%,transparent)]"
        />
        <div className="relative">
          {/* The greeting tracks the real clock, and the glyph moves with it:
              sunrise → sun → sunset → moon. A lucide icon rather than the 👋
              emoji, which renders differently on every platform and is read out
              literally by screen readers. */}
          <h1 className="flex flex-wrap items-center gap-x-3 gap-y-2 font-display text-2xl font-bold text-ink-900 lg:text-3xl">
            <span
              aria-hidden="true"
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl"
              style={{ color: tint, background: `${tint}1A`, boxShadow: `inset 0 0 0 1px ${tint}33` }}
            >
              <TimeIcon size={19} />
            </span>
            <span>{greeting}, {firstName}</span>
          </h1>
          <p className="mt-1.5 text-ink-500">{t('dash.greeting')}</p>

          {/* Urgent alert */}
          <div className="mt-4 p-3 rounded-xl bg-amber-50 border border-amber-200/60 flex items-center gap-3">
            <AlertCircle size={18} className="text-amber-500 shrink-0" />
            <p className="text-sm text-amber-700">
              <span className="font-semibold">{t('dash.followupReminder')}</span> {t('dash.bpReview')}
            </p>
            <button onClick={() => onNavigate('/patient/followups')} className="ml-auto text-xs font-semibold text-amber-600 hover:underline whitespace-nowrap">
              {t('dash.view')}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Status cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title={t('dash.nextAppointment')}
          value="11:30 AM"
          subtitle="Dr. Ananya Sharma · Video"
          icon={<Calendar size={22} />}
          delay={0.05}
        />
        <StatCard
          title={t('dash.referralStatus')}
          value={t('dash.accepted')}
          subtitle="District Hospital · Cardiology"
          icon={<ClipboardList size={22} />}
          trend={{ value: t('dash.onTrack'), positive: true }}
          delay={0.1}
        />
        <StatCard
          title={t('dash.followup')}
          value={t('dash.inDays')}
          subtitle={t('dash.bpReviewShort')}
          icon={<Stethoscope size={22} />}
          delay={0.15}
        />
        <StatCard
          title={t('dash.healthJourney')}
          value={`${journeyPercent}%`}
          subtitle={t('dash.stepsCompleted', { n: journeyCompleted, total: journeyTotal })}
          icon={<Heart size={22} />}
          delay={0.2}
        />
      </div>

      {/* Care Journey */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="glass-card-elevated p-6"
      >
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-bold text-gray-900">{t('dash.yourCareJourney')}</h2>
            <p className="text-sm text-gray-500">{t('dash.careDesc')}</p>
          </div>
          <button onClick={() => onNavigate('/patient/records')} className="text-sm font-semibold text-sahaay-deep hover:underline flex items-center gap-1">
            {t('dash.viewDetails')} <ChevronRight size={14} />
          </button>
        </div>

        {/* Horizontal on desktop */}
        <div className="hidden md:block">
          <CareJourney steps={journeySteps} orientation="horizontal" />
        </div>

        {/* Vertical on mobile */}
        <div className="md:hidden">
          <CareJourney steps={journeySteps} orientation="vertical" />
        </div>

        <div className="mt-5 pt-4 border-t border-gray-100">
          <ProgressBar value={journeyPercent} label="Overall Progress" showLabel height={10} />
        </div>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="lg:col-span-2 glass-card-elevated p-6"
        >
          <h2 className="text-lg font-bold text-gray-900 mb-4">{t('dash.quickActions')}</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {quickActions.map((action, i) => {
              const Icon = action.icon;
              return (
                <motion.button
                  key={i}
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onNavigate(action.route)}
                  className={`flex flex-col items-center gap-2 p-4 rounded-2xl bg-gradient-to-br ${action.color} hover:shadow-md transition-shadow text-center`}
                >
                  <Icon size={24} className={action.textColor} />
                  <span className="text-xs font-semibold text-gray-700">{action.label}</span>
                </motion.button>
              );
            })}
          </div>
        </motion.div>

        {/* Upcoming Appointment */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="glass-card-elevated p-6"
        >
          <h2 className="text-lg font-bold text-gray-900 mb-4">{t('dash.upcomingAppointment')}</h2>
          <div className="space-y-3">
            <div className="p-4 rounded-xl bg-sahaay-surface border border-sahaay-deep/6">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sahaay-deep to-sahaay-500 flex items-center justify-center text-white text-sm font-bold">
                  AS
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-900">Dr. Ananya Sharma</p>
                  <p className="text-xs text-gray-500">{t('dash.generalPhysician')}</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar size={14} className="text-sahaay-deep" />
                  {t('dash.today')}, 11:30 AM
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Video size={14} className="text-sahaay-deep" />
                  {t('dash.video')}
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin size={14} className="text-sahaay-deep" />
                  PHC Chandrapur
                </div>
              </div>
              <button
                onClick={() => onNavigate('/patient/consultation')}
                className="sahaay-btn-primary w-full mt-4 py-2.5 text-sm"
              >
                <Video size={16} className="inline mr-2" />
                {t('dash.joinConsultation')}
              </button>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Recommended Facilities */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card-elevated p-6"
      >
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-bold text-gray-900">{t('dash.recommendedFacilities')}</h2>
            <p className="text-sm text-gray-500">{t('dash.basedOnNeeds')}</p>
          </div>
          <button onClick={() => onNavigate('/patient/facilities')} className="text-sm font-semibold text-sahaay-deep hover:underline flex items-center gap-1">
            {t('dash.viewAll')} <ChevronRight size={14} />
          </button>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {facilities.slice(0, 4).map((facility) => (
            <motion.div
              key={facility.id}
              whileHover={{ y: -2 }}
              className="p-4 rounded-2xl bg-white/60 border border-sahaay-deep/6 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-sm font-bold text-gray-900">{facility.name}</p>
                  <p className="text-[11px] text-gray-500">{facility.type}</p>
                </div>
                <StatusBadge status={facility.medicines} />
              </div>
              <div className="space-y-2 text-xs text-gray-600">
                <div className="flex items-center gap-1.5">
                  <MapPin size={12} className="text-sahaay-deep" />
                  {facility.distance} {t('dash.kmAway')}
                </div>
                <div className="flex items-center gap-1.5">
                  <Users size={12} className="text-sahaay-deep" />
                  {facility.doctorsAvailable} {t('dash.doctorsAvailable')}
                </div>
                <div className="flex items-center gap-1.5">
                  <Clock size={12} className="text-sahaay-deep" />
                  ~{facility.waitingTime} {t('dash.minWait')}
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <button className="flex-1 py-1.5 text-xs font-semibold text-sahaay-deep bg-sahaay-deep/8 rounded-lg hover:bg-sahaay-deep/15 transition-colors">
                  {t('common.view')}
                </button>
                <button className="flex-1 py-1.5 text-xs font-semibold text-white bg-sahaay-deep rounded-lg hover:bg-sahaay-700 transition-colors">
                  {t('dash.select')}
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Bottom padding for mobile nav */}
      <div className="h-4 lg:hidden" />
    </div>
  );
}
