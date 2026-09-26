import { useState } from 'react';
import { motion } from 'framer-motion';
import { ClipboardList, ArrowRight, MapPin, User, CheckCircle2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { PageBanner } from '../../components/ui/PageBanner';
import { Modal } from '../../components/ui/Modal';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';
import { useReferrals, nextStatus, STATUS_ACTION_LABEL, SELF_DOCTOR_NAME } from '../../context/providers';

export function DoctorReferrals() {
  const [selected, setSelected] = useState<string | null>(null);
  const { t } = useLanguage();
  const [filter, setFilter] = useState('all');
  const { showToast } = useToast();
  const { referrals: allReferrals, advance } = useReferrals();

  /* A doctor only sees referrals addressed to them — declining isn't modelled,
     so the flow is: accept → schedule → in transit → completed. */
  const referrals = allReferrals.filter((r) => r.assignedDoctor === SELF_DOCTOR_NAME);
  const selectedReferral = referrals.find((r) => r.id === selected) ?? null;

  const advanceReferral = (id: string) => {
    const current = referrals.find((r) => r.id === id);
    const next = current ? nextStatus(current.status) : null;
    if (!next) return;
    advance(id);
    showToast(`Referral ${id} → ${next.replace(/_/g, ' ')}`);
  };

  const filtered = referrals.filter(r => filter === 'all' || r.status === filter);
  const statusColors: Record<string, string> = {
    pending: 'bg-amber-50 text-amber-700 border-amber-200',
    accepted: 'bg-sahaay-surface text-sahaay-deep border-sahaay-deep/20',
    completed: 'bg-blue-50 text-blue-700 border-blue-200',
    in_transit: 'bg-purple-50 text-purple-700 border-purple-200',
    followup_required: 'bg-rose-50 text-rose-700 border-rose-200',
    appointment_scheduled: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  };

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.referrals')}
        subtitle="Review and process patient referrals."
        image="https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=1200&q=80"
      />

      {/* Status filter pills */}
      <div className="flex flex-wrap gap-2">
        {['all', 'pending', 'accepted', 'in_transit', 'completed', 'followup_required'].map(s => (
          <button key={s} onClick={() => setFilter(s)} className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${filter === s ? 'bg-sahaay-deep text-white' : 'bg-white/60 text-gray-600 hover:bg-white border border-gray-200'}`}>
            {s === 'all' ? 'All' : s.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </button>
        ))}
      </div>

      {/* Referral cards */}
      <div className="space-y-3">
        {filtered.map((ref, i) => (
          <motion.div
            key={ref.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.04 * i }}
            className="glass-card p-5 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
            onClick={() => setSelected(ref.id)}
          >
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-sahaay-deep/8 flex items-center justify-center text-sahaay-deep shrink-0">
                    <User size={18} />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900">{ref.patientName}</p>
                    <p className="text-xs text-gray-500">{ref.reason}</p>
                  </div>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border ${statusColors[ref.status] || 'bg-gray-50 text-gray-600 border-gray-200'}`}>
                  {ref.status.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <MapPin size={12} className="text-sahaay-deep" />
                <span>{ref.sourceFacility}</span>
                <ArrowRight size={12} className="text-gray-400" />
                <span>{ref.destinationFacility}</span>
                <span className="ml-auto text-gray-400">{ref.createdDate}</span>
              </div>
              {nextStatus(ref.status) && (
                <div className="flex gap-2 pt-1">
                  <Button size="sm" onClick={(e) => { e.stopPropagation(); advanceReferral(ref.id); }}>
                    <CheckCircle2 size={14} /> {STATUS_ACTION_LABEL[nextStatus(ref.status)!] ?? 'Advance'}
                  </Button>
                </div>
              )}
            </div>
          </motion.div>
        ))}
        {filtered.length === 0 && (
          <div className="text-center py-16">
            <ClipboardList size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 font-medium">No referrals found</p>
          </div>
        )}
      </div>

      <div className="h-4 lg:hidden" />

      <Modal isOpen={!!selectedReferral} onClose={() => setSelected(null)} title="Referral Details" size="lg">
        {selectedReferral && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-sahaay-deep/10 flex items-center justify-center text-sahaay-deep">
                <ClipboardList size={20} />
              </div>
              <div>
                <p className="font-bold text-gray-900">{selectedReferral.patientName}</p>
                <p className="text-sm text-gray-500">{selectedReferral.id}</p>
              </div>
            </div>
            <div className="p-4 rounded-xl bg-sahaay-surface space-y-3">
              <div><p className="text-xs text-gray-500">Reason</p><p className="text-sm font-semibold">{selectedReferral.reason}</p></div>
              <div className="flex items-center gap-2 text-sm">
                <span className="font-semibold">{selectedReferral.sourceFacility}</span>
                <ArrowRight size={14} className="text-gray-400" />
                <span className="font-semibold">{selectedReferral.destinationFacility}</span>
              </div>
              <div className="flex gap-4">
                <div><p className="text-xs text-gray-500">Priority</p><p className="text-sm font-semibold capitalize">{selectedReferral.priority}</p></div>
                <div><p className="text-xs text-gray-500">Status</p><p className="text-sm font-semibold capitalize">{selectedReferral.status.replace(/_/g, ' ')}</p></div>
              </div>
              <div><p className="text-xs text-gray-500">Notes</p><p className="text-sm text-gray-600">{selectedReferral.notes}</p></div>
              <div className="flex gap-4">
                <div><p className="text-xs text-gray-500">Created</p><p className="text-sm font-semibold">{selectedReferral.createdDate}</p></div>
                <div><p className="text-xs text-gray-500">Expected</p><p className="text-sm font-semibold">{selectedReferral.expectedDate}</p></div>
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              {nextStatus(selectedReferral.status) ? (
                <Button onClick={() => advanceReferral(selectedReferral.id)}>
                  <CheckCircle2 size={15} />
                  {STATUS_ACTION_LABEL[nextStatus(selectedReferral.status)!] ?? 'Advance status'}
                </Button>
              ) : (
                <p className="flex items-center gap-2 text-sm font-semibold text-sahaay-deep">
                  <CheckCircle2 size={15} /> This referral is closed out
                </p>
              )}
              <Button variant="secondary" onClick={() => setSelected(null)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
