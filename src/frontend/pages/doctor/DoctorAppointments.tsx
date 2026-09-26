import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, Video, MapPin, Filter } from 'lucide-react';
import { Tabs } from '../../components/ui/Tabs';
import { PageBanner } from '../../components/ui/PageBanner';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { appointments } from '../../../mock-data/mockData';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

interface DoctorAppointmentsProps {
  onNavigate: (route: string) => void;
}

/* The logged-in doctor in the demo dataset. */
const SELF_DOCTOR_ID = 'D001';

export function DoctorAppointments({ onNavigate }: DoctorAppointmentsProps) {
  const [activeTab, setActiveTab] = useState('upcoming');
  const { t } = useLanguage();
  const [selected, setSelected] = useState<any>(null);
  const { showToast } = useToast();

  const doctorAppts = appointments.filter(a => a.doctorId === SELF_DOCTOR_ID);
  const tabs = [
    { id: 'upcoming', label: 'Upcoming', count: doctorAppts.filter(a => a.status === 'upcoming').length },
    { id: 'completed', label: 'Completed', count: doctorAppts.filter(a => a.status === 'completed').length },
  ];

  const filtered = doctorAppts.filter(a => a.status === activeTab);

  /* Live month grid: highlight days that actually carry appointments. */
  const bookedDays = useMemo(() => new Set(doctorAppts.map((a) => Number(a.date.split('-')[2]))), [doctorAppts]);
  const todayDay = new Date().getDate();

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.appointments')}
        subtitle="View and manage your consultation schedule."
        image="https://images.unsplash.com/photo-1506784983877-45594efa4cbe?auto=format&fit=crop&w=1200&q=80"
      />

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <Tabs tabs={tabs} onChange={setActiveTab} />
        <button className="flex items-center gap-2 px-3 py-2 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-white/60 transition-colors">
          <Filter size={14} /> Filter
        </button>
      </div>

      {/* Calendar */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-gray-800">September 2026</h3>
          <div className="flex gap-1">
            <button className="w-7 h-7 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-500 text-sm">←</button>
            <button className="w-7 h-7 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-500 text-sm">→</button>
          </div>
        </div>
        <div className="grid grid-cols-7 gap-1 text-center">
          {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((d, i) => (
            <div key={i} className="text-[10px] font-semibold text-gray-400 py-1">{d}</div>
          ))}
          {Array.from({ length: 30 }, (_, i) => i + 1).map(day => {
            const hasAppt = bookedDays.has(day);
            const isToday = day === todayDay;
            return (
              <button key={day} aria-label={hasAppt ? `Day ${day}, has appointments` : `Day ${day}`} className={`h-8 rounded-lg text-xs font-medium transition-all ${isToday ? 'bg-sahaay-deep text-white' : hasAppt ? 'bg-sahaay-deep/10 text-sahaay-deep font-bold' : 'text-gray-600 hover:bg-gray-100'}`}>
                {day}
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Appointment list */}
      <div className="space-y-3">
        {filtered.map((apt, i) => (
          <motion.div
            key={apt.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * i }}
            className="glass-card p-5 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
            onClick={() => setSelected(apt)}
          >
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-400 flex items-center justify-center text-white text-sm font-bold shrink-0">
                  {apt.patientName.split(' ').map((n: string) => n[0]).join('')}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-bold text-gray-900">{apt.patientName}</p>
                  <p className="text-xs text-gray-500">{apt.speciality} · {apt.facility}</p>
                </div>
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-600">
                <span className="flex items-center gap-1"><Calendar size={12} className="text-sahaay-deep" />{apt.date}</span>
                <span className="flex items-center gap-1"><Clock size={12} className="text-sahaay-deep" />{apt.time}</span>
                <span className="flex items-center gap-1">{apt.type === 'Video Consultation' ? <Video size={12} className="text-sahaay-deep" /> : <MapPin size={12} className="text-sahaay-deep" />}{apt.type}</span>
              </div>
              <div className="flex gap-2 shrink-0">
                <StatusBadge status={apt.priority} />
                {apt.status === 'upcoming' && (
                  <Button
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (apt.type === 'Video Consultation') {
                        onNavigate('/doctor/consultation');
                      } else {
                        showToast(`${apt.patientName} checked in — waiting room updated`);
                      }
                    }}
                  >
                    {apt.type === 'Video Consultation' ? <><Video size={14} /> Join</> : 'Check In'}
                  </Button>
                )}
              </div>
            </div>
          </motion.div>
        ))}
        {filtered.length === 0 && (
          <div className="text-center py-16">
            <Calendar size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 font-medium">No {activeTab} appointments</p>
          </div>
        )}
      </div>

      <div className="h-4 lg:hidden" />

      <Modal isOpen={!!selected} onClose={() => setSelected(null)} title="Appointment Details" size="lg">
        {selected && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-400 flex items-center justify-center text-white font-bold">
                {selected.patientName.split(' ').map((n: string) => n[0]).join('')}
              </div>
              <div>
                <p className="font-bold text-gray-900">{selected.patientName}</p>
                <p className="text-sm text-gray-500">{selected.speciality}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-sahaay-surface">
              <div><p className="text-xs text-gray-500">Date</p><p className="text-sm font-semibold">{selected.date}</p></div>
              <div><p className="text-xs text-gray-500">Time</p><p className="text-sm font-semibold">{selected.time}</p></div>
              <div><p className="text-xs text-gray-500">Facility</p><p className="text-sm font-semibold">{selected.facility}</p></div>
              <div><p className="text-xs text-gray-500">Type</p><p className="text-sm font-semibold">{selected.type}</p></div>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button onClick={() => { setSelected(null); onNavigate('/doctor/patients'); }}>
                View Patient History
              </Button>
              <Button variant="secondary" onClick={() => setSelected(null)}>Close</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
