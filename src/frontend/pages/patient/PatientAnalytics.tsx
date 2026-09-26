import { motion } from 'framer-motion';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Clock, CheckCircle2, MapPin, Activity } from 'lucide-react';
import { analyticsData } from '../../../mock-data/mockData';
import { StatCard } from '../../components/ui/StatCard';
import { PageBanner } from '../../components/ui/PageBanner';
import { useLanguage } from '../../context/providers';

export function PatientAnalytics() {
  const { patientFlow, kpis } = analyticsData;
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.analytics')}
        subtitle="Insights into your healthcare journey and platform performance."
        image="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80"
      />

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Avg. Travel Saved" value={kpis.avgTravelDistanceAvoided} icon={<MapPin size={20} />} delay={0} />
        <StatCard title="Avg. Wait Time" value={kpis.avgWaitingTime} icon={<Clock size={20} />} delay={0.05} />
        <StatCard title="Referral Rate" value={kpis.referralCompletionRate} icon={<CheckCircle2 size={20} />} trend={{ value: '+2% this month', positive: true }} delay={0.1} />
        <StatCard title="Follow-up Rate" value={kpis.followupCompletionRate} icon={<Activity size={20} />} delay={0.15} />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Patient Flow */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Patient Flow</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={patientFlow}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="registrations" fill="#1F6849" radius={[4, 4, 0, 0]} />
              <Bar dataKey="consultations" fill="#46A780" radius={[4, 4, 0, 0]} />
              <Bar dataKey="referrals" fill="#87DBAB" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Referral Completion */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="glass-card-elevated p-6">
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

        {/* Facility Waiting Time */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Average Waiting Time by Facility</h3>
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

        {/* Follow-up completion */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Follow-up Completion</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={analyticsData.followupCompletion}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="completed" fill="#1F6849" stackId="a" radius={[0, 0, 0, 0]} />
              <Bar dataKey="missed" fill="#ef4444" stackId="a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
