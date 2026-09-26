import { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, AlertCircle, CheckCircle2, Phone, Calendar } from 'lucide-react';
import { followups } from '../../../mock-data/mockData';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Button } from '../../components/ui/Button';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { PageBanner } from '../../components/ui/PageBanner';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

export function WorkerFollowups() {
  const [filter, setFilter] = useState('all');
  const { t } = useLanguage();
  const { showToast } = useToast();

  const filtered = followups.filter(f => filter === 'all' || f.status === filter);

  const statusIcon: Record<string, any> = {
    upcoming: Clock,
    missed: AlertCircle,
    completed: CheckCircle2,
  };

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.followups')}
        subtitle="Track community follow-up appointments."
        image="https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=1200&q=80"
      />

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Upcoming', count: followups.filter(f => f.status === 'upcoming').length, color: 'text-amber-600' },
          { label: 'Missed', count: followups.filter(f => f.status === 'missed').length, color: 'text-rose-600' },
          { label: 'Completed', count: followups.filter(f => f.status === 'completed').length, color: 'text-sahaay-deep' },
        ].map((s, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }} className="glass-card p-4 text-center">
            <p className={`text-2xl font-bold ${s.color}`}>{s.count}</p>
            <p className="text-xs text-gray-500">{s.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {['all', 'upcoming', 'missed', 'completed'].map(f => (
          <button key={f} onClick={() => setFilter(f)} className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${filter === f ? 'bg-sahaay-deep text-white' : 'bg-white/60 text-gray-600 hover:bg-white border border-gray-200'}`}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Follow-up list */}
      <div className="space-y-3">
        {filtered.map((fu, i) => {
          const Icon = statusIcon[fu.status] || Clock;
          return (
            <motion.div
              key={fu.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.04 * i }}
              className="glass-card p-5 hover:-translate-y-0.5 transition-all duration-200"
            >
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${fu.status === 'missed' ? 'bg-rose-50 text-rose-500' : fu.status === 'completed' ? 'bg-sahaay-surface text-sahaay-deep' : 'bg-amber-50 text-amber-500'}`}>
                  <Icon size={18} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-bold text-gray-900">{fu.patientName}</p>
                    <StatusBadge status={fu.status} />
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{fu.condition}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span className="flex items-center gap-1"><Calendar size={11} className="text-sahaay-deep" />Next: {fu.nextFollowup}</span>
                    <span className="flex items-center gap-1"><Clock size={11} className="text-sahaay-deep" />Last: {fu.lastConsultation}</span>
                  </div>
                  <div className="mt-2">
                    <ProgressBar value={fu.completionRate} height={6} />
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  {fu.status === 'upcoming' && (
                    <Button size="sm" onClick={() => showToast('Visit reminder sent')}><Phone size={14} /> Call</Button>
                  )}
                  {fu.status === 'missed' && (
                    <Button size="sm" onClick={() => showToast('Follow-up rescheduled')}>Reschedule</Button>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="h-4 lg:hidden" />
    </div>
  );
}
