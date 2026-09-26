import { useState } from 'react';
import { motion } from 'framer-motion';
import { Stethoscope, Calendar, Clock, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Tabs } from '../../components/ui/Tabs';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { PageBanner } from '../../components/ui/PageBanner';
import { Button } from '../../components/ui/Button';
import { followups } from '../../../mock-data/mockData';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

export function PatientFollowups() {
  const [activeTab, setActiveTab] = useState('upcoming');
  const { t } = useLanguage();
  const { showToast } = useToast();

  const tabs = [
    { id: 'upcoming', label: 'Upcoming', count: followups.filter(f => f.status === 'upcoming').length },
    { id: 'missed', label: 'Missed', count: followups.filter(f => f.status === 'missed').length },
    { id: 'completed', label: 'Completed', count: followups.filter(f => f.status === 'completed').length },
  ];

  const filtered = followups.filter(f => f.status === activeTab);

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.followups')}
        subtitle="Stay on track with your healthcare follow-ups."
        image="https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=1200&q=80"
      />

      {/* Summary */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="grid grid-cols-3 gap-4">
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-sahaay-deep">{followups.filter(f => f.status === 'upcoming').length}</p>
          <p className="text-xs text-gray-500 font-medium">Upcoming</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-red-500">{followups.filter(f => f.status === 'missed').length}</p>
          <p className="text-xs text-gray-500 font-medium">Missed</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-emerald-600">{followups.filter(f => f.status === 'completed').length}</p>
          <p className="text-xs text-gray-500 font-medium">Completed</p>
        </div>
      </motion.div>

      <Tabs tabs={tabs} onChange={setActiveTab} />

      <div className="space-y-3">
        {filtered.map((fu, i) => (
          <motion.div key={fu.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.04 * i }}
            className="glass-card-elevated p-5 hover:-translate-y-0.5 transition-all"
          >
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                  fu.status === 'missed' ? 'bg-red-50 text-red-500' : fu.status === 'completed' ? 'bg-emerald-50 text-emerald-500' : 'bg-sahaay-deep/8 text-sahaay-deep'
                }`}>
                  {fu.status === 'missed' ? <AlertTriangle size={18} /> : fu.status === 'completed' ? <CheckCircle2 size={18} /> : <Stethoscope size={18} />}
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-bold text-gray-900">{fu.patientName}</p>
                    <StatusBadge status={fu.priority} />
                  </div>
                  <p className="text-xs text-gray-500 truncate">{fu.condition}</p>
                </div>
              </div>

              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1"><Calendar size={12} className="text-sahaay-deep" />{fu.nextFollowup}</span>
                <span className="flex items-center gap-1"><Clock size={12} className="text-sahaay-deep" />{fu.assignedDoctor}</span>
              </div>

              <div className="w-32 shrink-0">
                <ProgressBar value={fu.completionRate} showLabel label="Completion" height={6} />
              </div>

              <Button size="sm" variant={fu.status === 'missed' ? 'primary' : 'secondary'} onClick={() => showToast(fu.status === 'missed' ? 'Follow-up rescheduled' : 'Follow-up details viewed')}>
                {fu.status === 'missed' ? 'Reschedule' : 'View'}
              </Button>
            </div>
          </motion.div>
        ))}
        {filtered.length === 0 && (
          <div className="text-center py-16">
            <Stethoscope size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 font-medium">No {activeTab} follow-ups</p>
          </div>
        )}
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
