import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, MapPin, Plus, Stethoscope, CheckCircle2 } from 'lucide-react';
import { facilities, patients, doctors } from '../../../mock-data/mockData';
import { Button } from '../../components/ui/Button';
import { PageBanner } from '../../components/ui/PageBanner';
import { Modal } from '../../components/ui/Modal';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';
import { useReferrals, nextStatus, STATUS_ACTION_LABEL, type Referral } from '../../context/providers';

const PRIORITIES = ['low', 'medium', 'high'];
/* The field worker's own facility — referrals are raised from here. */
const SOURCE_FACILITY = 'PHC Chandrapur';

export function WorkerReferrals() {
  const { t } = useLanguage();
  const { showToast } = useToast();
  const { referrals, createReferral, advance } = useReferrals();

  const [selected, setSelected] = useState<Referral | null>(null);
  const [formOpen, setFormOpen] = useState(false);

  // Draft
  const [patientId, setPatientId] = useState(patients[0].id);
  const [destinationFacility, setDestinationFacility] = useState(facilities[1].name);
  const [priority, setPriority] = useState('medium');
  const [assignedDoctor, setAssignedDoctor] = useState(doctors[1].name);
  const [reason, setReason] = useState('');
  const [notes, setNotes] = useState('');
  const [expectedDate, setExpectedDate] = useState('');
  const [error, setError] = useState('');

  const statusColors: Record<string, string> = {
    pending: 'bg-amber-50 text-amber-700 border-amber-200',
    accepted: 'bg-sahaay-surface text-sahaay-deep border-sahaay-deep/20',
    completed: 'bg-blue-50 text-blue-700 border-blue-200',
    in_transit: 'bg-purple-50 text-purple-700 border-purple-200',
    followup_required: 'bg-rose-50 text-rose-700 border-rose-200',
    appointment_scheduled: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  };

  const openForm = () => {
    setPatientId(patients[0].id);
    setDestinationFacility(facilities[1].name);
    setPriority('medium');
    setAssignedDoctor(doctors[1].name);
    setReason('');
    setNotes('');
    setExpectedDate('');
    setError('');
    setFormOpen(true);
  };

  const submit = () => {
    const patient = patients.find((p) => p.id === patientId);
    if (!patient) return;
    if (!reason.trim()) return setError('Describe why this patient is being referred.');
    if (!expectedDate) return setError('Pick an expected date for the referral.');

    const created = createReferral({
      patientId: patient.id,
      patientName: patient.name,
      sourceFacility: SOURCE_FACILITY,
      destinationFacility,
      reason: reason.trim(),
      priority,
      expectedDate,
      assignedDoctor,
      notes: notes.trim(),
    });

    setFormOpen(false);
    showToast(`Referral ${created.id} created for ${patient.name}`);
  };

  const advanceSelected = (referral: Referral) => {
    const next = nextStatus(referral.status);
    if (!next) return;
    advance(referral.id);
    setSelected({ ...referral, status: next });
    showToast(`Referral ${referral.id} → ${next.replace(/_/g, ' ')}`);
  };

  const summary = [
    { label: 'Pending', count: referrals.filter(r => r.status === 'pending').length, color: 'text-amber-600' },
    { label: 'In Transit', count: referrals.filter(r => r.status === 'in_transit').length, color: 'text-purple-600' },
    { label: 'Completed', count: referrals.filter(r => r.status === 'completed').length, color: 'text-sahaay-deep' },
  ];

  const selectedPatient = patients.find((p) => p.id === patientId) ?? patients[0];


  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.referrals')}
        subtitle="Create and track referrals for patients."
        image="https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=1200&q=80"
      />
      <div className="flex justify-end">
        <Button onClick={openForm}><Plus size={16} /> New Referral</Button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        {summary.map((s, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }} className="glass-card p-4 text-center">
            <p className={`text-2xl font-bold ${s.color}`}>{s.count}</p>
            <p className="text-xs text-gray-500">{s.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Referral list */}
      <div className="space-y-3">
        {referrals.map((ref, i) => (
          <motion.div
            key={ref.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: Math.min(0.04 * i, 0.24) }}
            className="glass-card p-4 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
            onClick={() => setSelected(ref)}
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-bold text-gray-900">{ref.patientName}</p>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${statusColors[ref.status] || 'bg-gray-50 text-gray-600 border-gray-200'}`}>
                {ref.status.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </span>
            </div>
            <p className="text-xs text-gray-500 mb-2">{ref.reason}</p>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <MapPin size={11} className="text-sahaay-deep" />
              <span>{ref.sourceFacility}</span>
              <ArrowRight size={11} className="text-gray-400" />
              <span>{ref.destinationFacility}</span>
              <span className="ml-auto text-gray-400">{ref.createdDate}</span>
            </div>
          </motion.div>
        ))}
        {referrals.length === 0 && (
          <div className="py-16 text-center">
            <MapPin size={40} className="mx-auto mb-3 text-gray-300" />
            <p className="font-medium text-gray-500">No referrals yet — raise the first one</p>
            <Button className="mt-4" onClick={openForm}>New Referral</Button>
          </div>
        )}
      </div>

      <div className="h-4 lg:hidden" />


      {/* Details + status transitions */}
      <Modal isOpen={!!selected} onClose={() => setSelected(null)} title="Referral Details" size="lg">
        {selected && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-sahaay-surface space-y-3">
              <div><p className="text-xs text-gray-500">Patient</p><p className="text-sm font-semibold">{selected.patientName}</p></div>
              <div><p className="text-xs text-gray-500">Reason</p><p className="text-sm font-semibold">{selected.reason}</p></div>
              <div className="flex items-center gap-2 text-sm">
                <span className="font-semibold">{selected.sourceFacility}</span>
                <ArrowRight size={14} className="text-gray-400" />
                <span className="font-semibold">{selected.destinationFacility}</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><p className="text-xs text-gray-500">Assigned Doctor</p><p className="text-sm font-semibold">{selected.assignedDoctor}</p></div>
                <div><p className="text-xs text-gray-500">Expected</p><p className="text-sm font-semibold">{selected.expectedDate}</p></div>
                <div><p className="text-xs text-gray-500">Priority</p><p className="text-sm font-semibold capitalize">{selected.priority}</p></div>
                <div><p className="text-xs text-gray-500">Status</p><p className="text-sm font-semibold capitalize">{selected.status.replace(/_/g, ' ')}</p></div>
              </div>
              {selected.notes && <div><p className="text-xs text-gray-500">Notes</p><p className="text-sm text-gray-600">{selected.notes}</p></div>}
            </div>
            <div className="flex flex-wrap gap-3">
              {nextStatus(selected.status) ? (
                <Button onClick={() => advanceSelected(selected)}>
                  <CheckCircle2 size={15} />
                  {STATUS_ACTION_LABEL[nextStatus(selected.status)!] ?? 'Advance status'}
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


      {/* Create referral */}
      <Modal isOpen={formOpen} onClose={() => setFormOpen(false)} title="New Referral" size="lg">
        <div className="space-y-5">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="ref-patient" className="mb-1.5 block text-xs font-semibold text-gray-600">Patient</label>
              <select id="ref-patient" value={patientId} onChange={(e) => setPatientId(e.target.value)} className="sahaay-input">
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>{p.name} · {p.age}y · {p.location}</option>
                ))}
              </select>
              <p className="mt-1.5 text-xs text-gray-500">{selectedPatient.bloodGroup} · {selectedPatient.gender} · {selectedPatient.phone}</p>
            </div>
            <div>
              <label htmlFor="ref-dest" className="mb-1.5 block text-xs font-semibold text-gray-600">Destination facility</label>
              <select id="ref-dest" value={destinationFacility} onChange={(e) => setDestinationFacility(e.target.value)} className="sahaay-input">
                {facilities.filter((f) => f.name !== SOURCE_FACILITY).map((f) => (
                  <option key={f.id} value={f.name}>{f.name} · {f.distance} km</option>
                ))}
              </select>
              <p className="mt-1.5 text-xs text-gray-500">Referred from {SOURCE_FACILITY}</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="ref-doctor" className="mb-1.5 block text-xs font-semibold text-gray-600">Assign to doctor</label>
              <select id="ref-doctor" value={assignedDoctor} onChange={(e) => setAssignedDoctor(e.target.value)} className="sahaay-input">
                {doctors.map((d) => (
                  <option key={d.id} value={d.name}>{d.name} · {d.speciality}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="ref-date" className="mb-1.5 block text-xs font-semibold text-gray-600">Expected date</label>
              <input
                id="ref-date"
                type="date"
                value={expectedDate}
                min={new Date().toISOString().slice(0, 10)}
                onChange={(e) => { setExpectedDate(e.target.value); setError(''); }}
                className="sahaay-input"
              />
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold text-gray-600">Priority</label>
            <div className="grid grid-cols-3 gap-2">
              {PRIORITIES.map((level) => (
                <button
                  key={level}
                  onClick={() => setPriority(level)}
                  className={`rounded-xl border px-3 py-2 text-xs font-semibold capitalize transition-all ${
                    priority === level ? 'border-sahaay-deep bg-sahaay-deep/6 text-sahaay-deep' : 'border-gray-200 text-gray-600 hover:bg-white/60'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label htmlFor="ref-reason" className="mb-1.5 block text-xs font-semibold text-gray-600">Reason for referral</label>
            <input
              id="ref-reason"
              type="text"
              value={reason}
              onChange={(e) => { setReason(e.target.value); setError(''); }}
              placeholder="e.g. Cardiac evaluation — elevated blood pressure"
              className="sahaay-input"
            />
          </div>

          <div>
            <label htmlFor="ref-notes" className="mb-1.5 block text-xs font-semibold text-gray-600">Clinical notes (optional)</label>
            <textarea
              id="ref-notes"
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Tests already done, medication, observations"
              className="sahaay-input resize-none"
            />
          </div>

          {error && (
            <p role="alert" className="rounded-xl border border-amber-200/60 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-800">
              {error}
            </p>
          )}

          <div className="flex gap-3">
            <Button onClick={submit}><Stethoscope size={15} /> Create referral</Button>
            <Button variant="secondary" onClick={() => setFormOpen(false)}>{t('common.cancel')}</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
