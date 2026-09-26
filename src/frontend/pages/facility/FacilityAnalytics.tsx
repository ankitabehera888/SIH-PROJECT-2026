import { motion } from 'framer-motion';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { Clock, ClipboardList, Stethoscope, Pill, TrendingUp } from 'lucide-react';
import { StatCard } from '../../components/ui/StatCard';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { PageBanner } from '../../components/ui/PageBanner';
import { analyticsData } from '../../../mock-data/mockData';

export function FacilityAnalytics() {
  const { kpis } = analyticsData;

  return (
    <div className="space-y-6">
      <PageBanner
        title="Facility Analytics"
        subtitle="Performance and operational metrics for PHC Chandrapur."
        image="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80"
      />

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Referral Completion" value={kpis.referralCompletionRate} icon={<ClipboardList size={22} />} trend={{ value: '↑ 2 pts', positive: true }} delay={0} />
        <StatCard title="Avg. Waiting Time" value={kpis.avgWaitingTime} icon={<Clock size={22} />} trend={{ value: '↓ 4 min', positive: true }} delay={0.05} />
        <StatCard title="Follow-up Completion" value={kpis.followupCompletionRate} icon={<Stethoscope size={22} />} delay={0.1} />
        <StatCard title="Medicine Availability" value={kpis.medicineAvailability} icon={<Pill size={22} />} trend={{ value: '↓ 3 pts', positive: false }} delay={0.15} />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Patient flow */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Patient Flow — Registrations vs Consultations</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={analyticsData.patientFlow}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="registrations" fill="#1F6849" radius={[4, 4, 0, 0]} />
              <Bar dataKey="consultations" fill="#46A780" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Referral completion trend */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Referral Completion Rate (%)</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={analyticsData.referralCompletion}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis domain={[75, 100]} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="rate" stroke="#1F6849" strokeWidth={2} dot={{ r: 4, fill: '#1F6849' }} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Follow-up completion */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Follow-ups — Completed vs Missed</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={analyticsData.followupCompletion}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="completed" stackId="a" fill="#2DA84D" />
              <Bar dataKey="missed" stackId="a" fill="#F59E0B" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Waiting time across network */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Avg. Waiting Time — Network Comparison (min)</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={analyticsData.waitingTime} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis dataKey="facility" type="category" tick={{ fontSize: 11 }} width={120} />
              <Tooltip />
              <Bar dataKey="avgTime" fill="#7C5CFF" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Occupancy + impact */}
      <div className="grid lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-card-elevated p-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Occupancy Across Referral Network</h3>
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

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }} className="glass-card-elevated p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={16} className="text-sahaay-deep" />
            <h3 className="text-sm font-bold text-gray-900">Impact Highlights</h3>
          </div>
          <div className="space-y-3">
            {[
              { label: 'Avg. travel distance avoided per patient', value: kpis.avgTravelDistanceAvoided },
              { label: 'Referral turnaround time', value: kpis.referralTurnaround },
              { label: 'Diagnostic availability', value: kpis.diagnosticAvailability },
              { label: 'Medicine availability', value: kpis.medicineAvailability },
            ].map((row, i) => (
              <div key={i} className="flex items-center justify-between rounded-xl bg-sahaay-surface/60 px-4 py-3">
                <span className="text-xs text-gray-600">{row.label}</span>
                <span className="text-sm font-bold text-gray-900">{row.value}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
