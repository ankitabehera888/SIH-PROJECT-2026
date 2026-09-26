import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, UserPlus, Phone, ChevronRight } from 'lucide-react';
import { patients } from '../../../mock-data/mockData';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { PageBanner } from '../../components/ui/PageBanner';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

export function WorkerPatients() {
  const [search, setSearch] = useState('');
  const { t } = useLanguage();
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const { showToast } = useToast();

  const filtered = patients.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.id.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.patients')}
        subtitle="Register and manage patients in your community."
        image="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80"
      />
      <div className="flex justify-end">
        <Button onClick={() => showToast('Registration form opened')}><UserPlus size={16} /> Register Patient</Button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-sahaay-deep">{patients.length}</p>
          <p className="text-xs text-gray-500">Total Patients</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-blue-600">{patients.filter(p => p.status === 'active').length}</p>
          <p className="text-xs text-gray-500">Active</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-amber-600">{patients.filter(p => p.status === 'followup').length}</p>
          <p className="text-xs text-gray-500">Needs Follow-up</p>
        </motion.div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search patients by name or ID..." className="sahaay-input pl-9" />
      </div>

      {/* Patient list */}
      <div className="space-y-3">
        {filtered.map((patient, i) => (
          <motion.div
            key={patient.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.03 * i }}
            className="glass-card p-4 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
            onClick={() => setSelectedPatient(patient)}
          >
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-400 flex items-center justify-center text-white text-sm font-bold shrink-0">
                {patient.avatar}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-bold text-gray-900">{patient.name}</p>
                  <StatusBadge status={patient.status} />
                </div>
                <p className="text-xs text-gray-500">{patient.id} · {patient.age}y {patient.gender} · {patient.location.split(',')[0]}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button className="w-8 h-8 rounded-lg bg-sahaay-deep/8 flex items-center justify-center text-sahaay-deep hover:bg-sahaay-deep/15 transition-colors">
                  <Phone size={14} />
                </button>
                <ChevronRight size={16} className="text-gray-400" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="h-4 lg:hidden" />

      <Modal isOpen={!!selectedPatient} onClose={() => setSelectedPatient(null)} title="Patient Details" size="lg">
        {selectedPatient && (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-400 flex items-center justify-center text-white font-bold text-lg">{selectedPatient.avatar}</div>
              <div>
                <p className="text-lg font-bold text-gray-900">{selectedPatient.name}</p>
                <p className="text-sm text-gray-500">{selectedPatient.id} · {selectedPatient.age}y {selectedPatient.gender}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Blood Group</p><p className="text-sm font-semibold">{selectedPatient.bloodGroup}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Phone</p><p className="text-sm font-semibold">{selectedPatient.phone}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Location</p><p className="text-sm font-semibold">{selectedPatient.location}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Registered</p><p className="text-sm font-semibold">{selectedPatient.registeredDate}</p></div>
              <div className="p-3 rounded-xl bg-sahaay-surface col-span-2"><p className="text-xs text-gray-500">Emergency Contact</p><p className="text-sm font-semibold">{selectedPatient.emergencyContact}</p></div>
            </div>
            <div className="flex gap-3">
              <Button onClick={() => showToast('Referral form opened')}>Create Referral</Button>
              <Button variant="secondary" onClick={() => showToast('Follow-up scheduled')}>Schedule Follow-up</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
