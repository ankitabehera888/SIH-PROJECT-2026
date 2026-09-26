import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Phone, MapPin, ChevronRight, FileText, Activity, Pill, TriangleAlert, Clock, MessageCircle, Syringe } from 'lucide-react';
import { patients, healthRecords, patientHealthRecords, messageHandoff } from '../../../mock-data/mockData';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { PageBanner } from '../../components/ui/PageBanner';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

interface DoctorPatientsProps {
  onNavigate?: (route: string) => void;
}

export function DoctorPatients({ onNavigate }: DoctorPatientsProps) {
  const [search, setSearch] = useState('');
  const { t } = useLanguage();
  const { showToast } = useToast();
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [recordsOpen, setRecordsOpen] = useState(false);
  const [filter, setFilter] = useState('all');

  const filtered = patients.filter(p => {
    const matchSearch = p.name.toLowerCase().includes(search.toLowerCase()) || p.id.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'all' || p.status === filter;
    return matchSearch && matchFilter;
  });

  /* Each patient gets their own chart; fall back to the base record if an id
     has no dedicated entry yet. */
  const recordFor = (id: string) => patientHealthRecords[id] ?? healthRecords;

  const openMessages = (patientId: string) => {
    messageHandoff.patientId = patientId;
    setSelectedPatient(null);
    setRecordsOpen(false);
    onNavigate?.('/doctor/messages');
  };

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.patients')}
        subtitle="Manage your patient list and clinical records."
        image="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80"
      />

      {/* Search and filters */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search patients by name or ID..." className="sahaay-input pl-9" />
        </div>
        <div className="flex gap-2">
          {['all', 'active', 'followup'].map(f => (
            <button key={f} onClick={() => setFilter(f)} className={`px-3 py-2 rounded-xl text-xs font-semibold transition-colors ${filter === f ? 'bg-sahaay-deep text-white' : 'bg-white/60 text-gray-600 hover:bg-white'}`}>
              {f === 'all' ? 'All' : f === 'active' ? 'Active' : 'Follow-up'}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Patient list */}
      <div className="space-y-3">
        {filtered.map((patient, i) => (
          <motion.div
            key={patient.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.03 * i }}
            className="glass-card p-5 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
            onClick={() => setSelectedPatient(patient)}
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-sahaay-deep to-sahaay-500 flex items-center justify-center text-white text-sm font-bold shrink-0">
                {patient.avatar}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-bold text-gray-900">{patient.name}</p>
                  <StatusBadge status={patient.status} />
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{patient.id} · {patient.age}y {patient.gender} · {patient.bloodGroup}</p>
              </div>
              <div className="hidden sm:flex items-center gap-4 text-xs text-gray-500 shrink-0">
                <span className="flex items-center gap-1"><MapPin size={12} className="text-sahaay-deep" />{patient.location.split(',')[0]}</span>
                <span className="flex items-center gap-1"><Phone size={12} className="text-sahaay-deep" />{patient.phone}</span>
              </div>
              <ChevronRight size={16} className="text-gray-400 shrink-0" />
            </div>
          </motion.div>
        ))}
        {filtered.length === 0 && (
          <div className="text-center py-16">
            <Search size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 font-medium">No patients found</p>
          </div>
        )}
      </div>

      <div className="h-4 lg:hidden" />

      {/* Patient detail modal */}
      <Modal isOpen={!!selectedPatient && !recordsOpen} onClose={() => setSelectedPatient(null)} title="Patient Details" size="lg">
        {selectedPatient && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-sahaay-deep to-sahaay-500 flex items-center justify-center text-white font-bold text-lg">
                {selectedPatient.avatar}
              </div>
              <div>
                <p className="text-lg font-bold text-gray-900">{selectedPatient.name}</p>
                <p className="text-sm text-gray-500">{selectedPatient.id} · {selectedPatient.age}y {selectedPatient.gender}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-sahaay-surface">
                <p className="text-xs text-gray-500">Blood Group</p>
                <p className="text-sm font-semibold">{selectedPatient.bloodGroup}</p>
              </div>
              <div className="p-3 rounded-xl bg-sahaay-surface">
                <p className="text-xs text-gray-500">Location</p>
                <p className="text-sm font-semibold">{selectedPatient.location}</p>
              </div>
              <div className="p-3 rounded-xl bg-sahaay-surface">
                <p className="text-xs text-gray-500">Phone</p>
                <p className="text-sm font-semibold">{selectedPatient.phone}</p>
              </div>
              <div className="p-3 rounded-xl bg-sahaay-surface">
                <p className="text-xs text-gray-500">Registered</p>
                <p className="text-sm font-semibold">{selectedPatient.registeredDate}</p>
              </div>
              <div className="p-3 rounded-xl bg-sahaay-surface col-span-2">
                <p className="text-xs text-gray-500">Emergency Contact</p>
                <p className="text-sm font-semibold">{selectedPatient.emergencyContact}</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button onClick={() => showToast(`Calling ${selectedPatient.name} on ${selectedPatient.phone} …`)}>
                <Phone size={14} /> Call Patient
              </Button>
              <Button variant="secondary" onClick={() => openMessages(selectedPatient.id)}>
                <MessageCircle size={14} /> Send Message
              </Button>
              <Button variant="secondary" onClick={() => setRecordsOpen(true)}>
                <FileText size={14} /> View Records
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Patient health records */}
      <Modal isOpen={recordsOpen && !!selectedPatient} onClose={() => setRecordsOpen(false)} title="Patient Health Records" size="lg">
        {selectedPatient && (() => {
          const record = recordFor(selectedPatient.id);
          return (
          <div className="space-y-5">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-sahaay-deep to-sahaay-500 flex items-center justify-center text-white font-bold">
                {selectedPatient.avatar}
              </div>
              <div>
                <p className="font-bold text-gray-900">{selectedPatient.name}</p>
                <p className="text-xs text-gray-500">{selectedPatient.id} · {selectedPatient.age}y {selectedPatient.gender} · {selectedPatient.bloodGroup}</p>
              </div>
            </div>

            {/* Allergies first — clinically they gate everything else */}
            {record.allergies.length > 0 && (
              <div className="rounded-xl border border-amber-200/60 bg-amber-50 p-3">
                <p className="flex items-center gap-1.5 text-xs font-bold text-amber-800">
                  <TriangleAlert size={13} /> Allergies
                </p>
                <p className="mt-1 text-sm font-semibold text-amber-800">{record.allergies.join(' · ')}</p>
              </div>
            )}

            {/* Timeline */}
            <div>
              <p className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-gray-500">
                <Clock size={13} /> Health timeline
              </p>
              <div className="max-h-48 space-y-2 overflow-y-auto pr-1">
                {record.timeline.map((entry) => (
                  <div key={entry.date + entry.event} className="flex items-start gap-3 rounded-xl bg-sahaay-surface p-3">
                    <span className="shrink-0 font-mono text-[10px] font-bold text-sahaay-deep">{entry.date}</span>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-gray-900">{entry.event}</p>
                      <p className="text-xs text-gray-500">{entry.details} · {entry.facility}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Conditions + prescriptions */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-gray-500">
                  <Activity size={13} /> Conditions
                </p>
                <div className="space-y-2">
                  {record.conditions.length === 0 && (
                    <p className="rounded-xl bg-sahaay-surface p-3 text-xs text-gray-500">No chronic conditions recorded</p>
                  )}
                  {record.conditions.map((c) => (
                    <div key={c.name} className="rounded-xl bg-sahaay-surface p-3">
                      <p className="text-sm font-semibold text-gray-900">{c.name}</p>
                      <p className="text-xs text-gray-500">Since {c.diagnosedDate} · {c.status}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-gray-500">
                  <Pill size={13} /> Prescriptions
                </p>
                <div className="space-y-2">
                  {record.prescriptions.length === 0 && (
                    <p className="rounded-xl bg-sahaay-surface p-3 text-xs text-gray-500">No active prescriptions</p>
                  )}
                  {record.prescriptions.map((p) => (
                    <div key={p.date} className="rounded-xl bg-sahaay-surface p-3">
                      <p className="text-sm font-semibold text-gray-900">{p.doctor} · {p.date}</p>
                      <p className="text-xs text-gray-500">{p.medicines.join(' · ')}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Diagnostics */}
            <div>
              <p className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-gray-500">
                <FileText size={13} /> Diagnostics
              </p>
              <div className="space-y-2">
                {record.diagnostics.length === 0 && (
                  <p className="rounded-xl bg-sahaay-surface p-3 text-xs text-gray-500">No diagnostic results yet</p>
                )}
                {record.diagnostics.map((d) => (
                  <div key={d.test + d.date} className="rounded-xl bg-sahaay-surface p-3">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-gray-900">{d.test}</p>
                      <StatusBadge status={d.status === 'Available' ? 'active' : d.status} />
                    </div>
                    <p className="text-xs text-gray-500">{d.results} · {d.date} · {d.facility}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Vaccinations */}
            <div>
              <p className="mb-2 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-gray-500">
                <Syringe size={13} /> Vaccinations
              </p>
              <div className="space-y-2">
                {record.vaccinations.length === 0 && (
                  <p className="rounded-xl bg-sahaay-surface p-3 text-xs text-gray-500">No vaccination records on file</p>
                )}
                {record.vaccinations.map((v) => (
                  <div key={v.name + v.date} className="rounded-xl bg-sahaay-surface p-3">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-gray-900">{v.name}</p>
                      <StatusBadge status={v.status === 'Completed' ? 'completed' : 'pending'} />
                    </div>
                    <p className="text-xs text-gray-500">{v.date}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick clinical summary */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 rounded-xl bg-sahaay-surface">
                <p className="text-xs text-gray-500">Timeline events</p>
                <p className="text-sm font-semibold">{record.timeline.length}</p>
              </div>
              <div className="p-3 rounded-xl bg-sahaay-surface">
                <p className="text-xs text-gray-500">Active meds lists</p>
                <p className="text-sm font-semibold">{record.prescriptions.length}</p>
              </div>
              <div className="p-3 rounded-xl bg-sahaay-surface">
                <p className="text-xs text-gray-500">Allergies</p>
                <p className="text-sm font-semibold">{record.allergies.length || 'None'}</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button variant="secondary" onClick={() => { setRecordsOpen(false); setSelectedPatient(null); }}>Close</Button>
              <Button onClick={() => openMessages(selectedPatient.id)}>
                <MessageCircle size={14} /> Message Patient
              </Button>
            </div>
          </div>
          );
        })()}
      </Modal>
    </div>
  );
}
