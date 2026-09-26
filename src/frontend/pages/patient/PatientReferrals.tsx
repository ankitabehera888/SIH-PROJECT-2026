import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, MapPin, CheckCircle2, Circle, Clock3, Truck, CalendarCheck } from 'lucide-react';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';
import { useReferrals, SELF_PATIENT_ID } from '../../context/providers';

const statusIcons: Record<string, any> = {
  pending: Circle, accepted: CheckCircle2, in_transit: Truck, appointment_scheduled: CalendarCheck, completed: CheckCircle2, followup_required: Clock3,
};

const lifecycleSteps = ['Created', 'Accepted', 'Appointment', 'Arrived', 'Consultation', 'Diagnostics', 'Treatment', 'Follow-up'];

/* How far along the 8-step tracker each status sits. */
const STATUS_STEP: Record<string, number> = {
  pending: 0,
  accepted: 1,
  appointment_scheduled: 2,
  in_transit: 3,
  followup_required: 7,
  completed: 7,
};

export function PatientReferrals() {
  const [selectedReferral, setSelectedReferral] = useState<any>(null);
  const { t } = useLanguage();
  const { showToast } = useToast();
  const { referrals } = useReferrals();

  const myReferrals = referrals.filter((r) => r.patientId === SELF_PATIENT_ID);
  /* The tracker follows the most active referral — the newest one still open. */
  const activeReferral = myReferrals.find((r) => r.status !== 'completed') ?? myReferrals[0];
  const currentStep = activeReferral ? STATUS_STEP[activeReferral.status] ?? 0 : 0;

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-gray-900">{t('dash.referrals')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('ref.trackJourney')}</p>
      </motion.div>

      {/* Lifecycle */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="glass-card-elevated p-6">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
          <h2 className="text-sm font-bold text-gray-900">{t('ref.lifecycle')}</h2>
          {activeReferral && (
            <span className="text-xs text-gray-500">
              Tracking <span className="font-semibold text-gray-800">{activeReferral.id}</span> · {activeReferral.reason}
            </span>
          )}
        </div>
        <div className="flex items-center gap-0 overflow-x-auto pb-2">
          {lifecycleSteps.map((step, i) => {
            const isCompleted = i < currentStep;
            const isCurrent = i === currentStep;
            return (
              <div key={i} className="flex items-center">
                <div className="flex flex-col items-center min-w-[70px]">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 ${
                    isCompleted ? 'bg-sahaay-deep border-sahaay-deep text-white' : isCurrent ? 'bg-white border-sahaay-500 text-sahaay-deep shadow-[0_0_0_3px_rgba(31,104,73,0.1)]' : 'bg-white border-gray-200 text-gray-400'
                  }`}>
                    {isCompleted ? '✓' : i + 1}
                  </div>
                  <span className={`text-[10px] font-medium mt-1 text-center ${isCompleted ? 'text-sahaay-deep' : isCurrent ? 'text-gray-800 font-bold' : 'text-gray-400'}`}>{step}</span>
                </div>
                {i < lifecycleSteps.length - 1 && <div className={`h-[2px] w-6 ${i < currentStep ? 'bg-sahaay-deep' : 'bg-gray-200'}`} />}
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Referral cards */}
      <div className="space-y-3">
        {myReferrals.map((ref, i) => {
          const StatusIcon = statusIcons[ref.status] || Circle;
          return (
            <motion.div
              key={ref.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 * i }}
              className="glass-card p-5 hover:-translate-y-0.5 transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="w-10 h-10 rounded-xl bg-sahaay-deep/8 flex items-center justify-center text-sahaay-deep shrink-0">
                    <StatusIcon size={18} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="text-sm font-bold text-gray-900">{ref.id}</p>
                      <StatusBadge status={ref.status} />
                      <StatusBadge status={ref.priority} />
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5 truncate">{ref.reason}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1"><MapPin size={12} />{ref.sourceFacility}</span>
                  <ArrowRight size={12} className="text-sahaay-deep" />
                  <span className="flex items-center gap-1"><MapPin size={12} />{ref.destinationFacility}</span>
                </div>

                <div className="flex gap-2 shrink-0">
                  <Button size="sm" variant="secondary" onClick={() => setSelectedReferral(ref)}>View</Button>
                  <Button size="sm" variant="ghost" onClick={() => showToast('Facility contacted')}>Contact</Button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
      <div className="h-4 lg:hidden" />

      <Modal isOpen={!!selectedReferral} onClose={() => setSelectedReferral(null)} title="Referral Details" size="lg">
        {selectedReferral && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Referral ID</p><p className="text-sm font-bold">{selectedReferral.id}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Patient</p><p className="text-sm font-bold">{selectedReferral.patientName}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">From</p><p className="text-sm font-bold">{selectedReferral.sourceFacility}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">To</p><p className="text-sm font-bold">{selectedReferral.destinationFacility}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Reason</p><p className="text-sm font-bold">{selectedReferral.reason}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Assigned Doctor</p><p className="text-sm font-bold">{selectedReferral.assignedDoctor}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Created</p><p className="text-sm font-bold">{selectedReferral.createdDate}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Expected</p><p className="text-sm font-bold">{selectedReferral.expectedDate}</p></div>
            </div>
            <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500 mb-1">Notes</p><p className="text-sm text-gray-700">{selectedReferral.notes}</p></div>
            <Button onClick={() => setSelectedReferral(null)}>Close</Button>
          </div>
        )}
      </Modal>
    </div>
  );
}
