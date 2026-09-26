import { motion } from 'framer-motion';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Users, Clock, ClipboardList, Stethoscope, Activity, Pill, Bed } from 'lucide-react';
import { StatCard } from '../../components/ui/StatCard';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { analyticsData, facilityStats } from '../../../mock-data/mockData';
import { useTimeGreeting } from '../../hooks/useTimeGreeting';
import { useLanguage } from '../../context/providers';

interface FacilityDashboardProps {
  onNavigate: (route: string) => void;
}

export function FacilityDashboard(_props: FacilityDashboardProps) {
  const { t } = useLanguage();
  const { greeting, Icon: TimeIcon, tint } = useTimeGreeting();
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="relative overflow-hidden glass-card-elevated p-6 lg:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-purple-100/40 to-transparent rounded-full blur-3xl -translate-y-1/3 translate-x-1/3" />
        <img
          src="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=800&q=80"
          alt=""
          loading="lazy"
          className="pointer-events-none absolute inset-y-0 right-0 hidden w-2/5 object-cover opacity-20 lg:block [mask-image:linear-gradient(to_left,black_35%,transparent)]"
        />
        <div className="relative">
          {/* This screen is a console, not a personal dashboard, so the live
              greeting sits above the title as a chip rather than replacing it. */}
          <span
            className="mb-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-mono text-[10px] font-bold uppercase tracking-[0.16em]"
            style={{ color: tint, background: `${tint}14`, boxShadow: `inset 0 0 0 1px ${tint}33` }}
          >
            <TimeIcon size={12} />
            {greeting}
          </span>
          <h1 className="font-display text-2xl font-bold text-ink-900 lg:text-3xl">{t('fac.intelligence')}</h1>
          <p className="mt-1.5 text-ink-500">PHC Chandrapur — Operational Overview</p>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Patient Load (Today)" value={facilityStats.patientLoad.today} icon={<Users size={22} />} subtitle={`${facilityStats.patientLoad.thisWeek} this week`} delay={0} />
        <StatCard title="Avg. Wait Time" value={`${facilityStats.avgWaitingTime} min`} icon={<Clock size={22} />} trend={{ value: '↓ 4 min', positive: true }} delay={0.05} />
        <StatCard title="Pending Referrals" value={facilityStats.pendingReferrals} icon={<ClipboardList size={22} />} delay={0.1} />
        <StatCard title="Follow-up Gaps" value={facilityStats.followupGaps} icon={<Stethoscope size={22} />} delay={0.15} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Available Doctors" value={facilityStats.availableDoctors} icon={<Activity size={22} />} delay={0.2} />
        <StatCard title="Diagnostic Capacity" value={`${facilityStats.diagnosticCapacity}%`} icon={<Activity size={22} />} delay={0.25} />
        <StatCard title="Medicine Stock" value={`${facilityStats.medicineStockLevel}%`} icon={<Pill size={22} />} delay={0.3} />
        <StatCard title="Bed Occupancy" value="65%" icon={<Bed size={22} />} delay={0.35} />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Patient flow chart */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Patient Flow (5 months)</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={analyticsData.patientFlow}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="registrations" fill="#1F6849" radius={[4, 4, 0, 0]} />
              <Bar dataKey="consultations" fill="#46A780" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Facility load */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Facility Occupancy</h3>
          <div className="space-y-4">
            {analyticsData.facilityLoad.map((f, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-gray-700">{f.name}</span>
                  <span className="text-xs font-bold text-sahaay-deep">{f.occupancy}%</span>
                </div>
                <ProgressBar value={f.occupancy} height={8} color={f.occupancy > 80 ? 'from-red-500 to-red-400' : f.occupancy > 60 ? 'from-amber-500 to-amber-400' : 'from-sahaay-deep to-sahaay-500'} />
              </div>
            ))}
          </div>
        </motion.div>

        {/* Referral completion */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Referral Completion Rate</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={analyticsData.referralCompletion}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="rate" stroke="#1F6849" strokeWidth={2} dot={{ r: 4, fill: '#1F6849' }} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Waiting time */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Waiting Time by Facility</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={analyticsData.waitingTime} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis dataKey="facility" type="category" tick={{ fontSize: 11 }} width={120} />
              <Tooltip />
              <Bar dataKey="avgTime" fill="#2DA84D" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
