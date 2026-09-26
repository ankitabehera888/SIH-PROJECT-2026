import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, Video, MapPin, Filter, Stethoscope, CheckCircle2 } from 'lucide-react';
import { Tabs } from '../../components/ui/Tabs';
import { PageBanner } from '../../components/ui/PageBanner';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { appointments as seedAppointments, doctors } from '../../../mock-data/mockData';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';
import { useUserProfile } from '../../context/providers';

interface PatientAppointmentsProps {
  onNavigate: (route: string) => void;
}

/* The logged-in patient in the demo dataset. */
const SELF_PATIENT_ID = 'P001';
const TIME_SLOTS = ['09:00 AM', '10:30 AM', '11:30 AM', '02:00 PM', '03:30 PM', '05:00 PM'];
const APPOINTMENT_TYPES = ['Video Consultation', 'In-Person'];

type Appointment = (typeof seedAppointments)[number] & { reason?: string };

export function PatientAppointments({ onNavigate }: PatientAppointmentsProps) {
  const { t } = useLanguage();
  const { showToast } = useToast();
  const { profile } = useUserProfile();

  const [activeTab, setActiveTab] = useState('upcoming');
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  /* Real state, seeded from the mock list but scoped to this patient — a
     booking made here shows up in the list, its tab count, and the calendar. */
  const [list, setList] = useState<Appointment[]>(() =>
    seedAppointments.filter((a) => a.patientId === SELF_PATIENT_ID),
  );
  const [bookingOpen, setBookingOpen] = useState(false);

  // Booking draft
  const [doctorId, setDoctorId] = useState(doctors[0].id);
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [type, setType] = useState(APPOINTMENT_TYPES[0]);
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');

  const countBy = (status: string) => list.filter((a) => a.status === status).length;

  const tabs = [
    { id: 'upcoming', label: t('common.upcoming'), count: countBy('upcoming') },
    { id: 'completed', label: t('common.completed'), count: countBy('completed') },
    { id: 'cancelled', label: t('common.cancelled'), count: countBy('cancelled') },
  ];

  const filtered = list.filter((a) => a.status === activeTab);

  /* Days in the shown month that already carry an appointment. */
  const bookedDays = useMemo(() => new Set(list.map((a) => Number(a.date.split('-')[2]))), [list]);
  const todayDay = new Date().getDate();

  const openBooking = () => {
    setDoctorId(doctors[0].id);
    setDate('');
    setTime('');
    setType(APPOINTMENT_TYPES[0]);
    setReason('');
    setError('');
    setBookingOpen(true);
  };

  const confirmBooking = () => {
    const doctor = doctors.find((d) => d.id === doctorId);
    if (!doctor) return;
    if (!date) return setError('Pick a date for the appointment.');
    if (!time) return setError('Pick a time slot.');

    const newAppointment: Appointment = {
      id: `A${String(list.length + 100).padStart(3, '0')}`,
      patientId: SELF_PATIENT_ID,
      patientName: profile.fullName,
      doctorId: doctor.id,
      doctorName: doctor.name,
      speciality: doctor.speciality,
      facility: doctor.facility,
      date,
      time,
      type,
      status: 'upcoming',
      priority: 'normal',
      reason: reason.trim() || undefined,
    };

    setList((prev) => [newAppointment, ...prev]);
    setActiveTab('upcoming');
    setBookingOpen(false);
    showToast(`Appointment booked with ${doctor.name} on ${date} at ${time}`);
  };

  const cancelAppointment = (id: string) => {
    setList((prev) => prev.map((a) => (a.id === id ? { ...a, status: 'cancelled' } : a)));
    setSelectedAppointment(null);
    showToast('Appointment cancelled');
  };

  const selectedDoctor = doctors.find((d) => d.id === doctorId) ?? doctors[0];


  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.appointments')}
        subtitle={t('ap.manageConsultations')}
        image="https://images.unsplash.com/photo-1506784983877-45594efa4cbe?auto=format&fit=crop&w=1200&q=80"
      />
      <div className="flex justify-end">
        <Button onClick={openBooking}>{t('dash.bookAppointment')}</Button>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <Tabs tabs={tabs} onChange={setActiveTab} />
        <button className="flex items-center gap-2 px-3 py-2 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-white/60 transition-colors">
          <Filter size={14} /> {t('common.filter')}
        </button>
      </div>

      {/* Month grid — days with appointments are highlighted from live state */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-gray-800">
            {new Date().toLocaleString('en-GB', { month: 'long', year: 'numeric' })}
          </h3>
          <div className="flex gap-1">
            <button aria-label="Previous month" className="w-7 h-7 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-500 text-sm">←</button>
            <button aria-label="Next month" className="w-7 h-7 rounded-lg hover:bg-gray-100 flex items-center justify-center text-gray-500 text-sm">→</button>
          </div>
        </div>
        <div className="grid grid-cols-7 gap-1 text-center">
          {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((d, i) => (
            <div key={i} className="text-[10px] font-semibold text-gray-400 py-1">{d}</div>
          ))}
          {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => {
            const hasAppointment = bookedDays.has(day);
            const isToday = day === todayDay;
            return (
              <button
                key={day}
                aria-label={hasAppointment ? `Day ${day}, has appointments` : `Day ${day}`}
                className={`h-8 rounded-lg text-xs font-medium transition-all ${
                  isToday ? 'bg-sahaay-deep text-white' : hasAppointment ? 'bg-sahaay-deep/10 text-sahaay-deep font-bold' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
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
            transition={{ delay: Math.min(0.05 * i, 0.25) }}
            className="glass-card p-5 hover:-translate-y-0.5 transition-all duration-200"
          >
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex items-center gap-3 flex-1">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-sahaay-deep to-sahaay-500 flex items-center justify-center text-white text-sm font-bold shrink-0">
                  {apt.doctorName.split(' ').slice(1).map((n: string) => n[0]).join('')}
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-bold text-gray-900">{apt.doctorName}</p>
                    <StatusBadge status={apt.priority} />
                  </div>
                  <p className="text-xs text-gray-500">{apt.speciality} · {apt.facility}</p>
                </div>
              </div>

              <div className="flex items-center gap-4 text-xs text-gray-600">
                <span className="flex items-center gap-1"><Calendar size={12} className="text-sahaay-deep" />{apt.date}</span>
                <span className="flex items-center gap-1"><Clock size={12} className="text-sahaay-deep" />{apt.time}</span>
                <span className="flex items-center gap-1">{apt.type === 'Video Consultation' ? <Video size={12} className="text-sahaay-deep" /> : <MapPin size={12} className="text-sahaay-deep" />}{apt.type}</span>
              </div>

              <div className="flex gap-2 shrink-0">
                {apt.status === 'upcoming' && apt.type === 'Video Consultation' && (
                  <Button size="sm" onClick={() => onNavigate('/patient/consultation')}>
                    <Video size={14} /> {t('apt.join')}
                  </Button>
                )}
                <Button size="sm" variant="secondary" onClick={() => setSelectedAppointment(apt)}>
                  {t('apt.details')}
                </Button>
                {apt.status === 'upcoming' && (
                  <Button size="sm" variant="ghost" onClick={() => cancelAppointment(apt.id)}>
                    {t('apt.cancel')}
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
            {activeTab === 'upcoming' && (
              <Button className="mt-4" onClick={openBooking}>{t('dash.bookAppointment')}</Button>
            )}
          </div>
        )}
      </div>

      <div className="h-4 lg:hidden" />


      {/* Detail modal */}
      <Modal isOpen={!!selectedAppointment} onClose={() => setSelectedAppointment(null)} title={t('apt.details')} size="lg">
        {selectedAppointment && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-sahaay-deep to-sahaay-500 flex items-center justify-center text-white font-bold">
                {selectedAppointment.doctorName.split(' ').slice(1).map((n: string) => n[0]).join('')}
              </div>
              <div>
                <p className="font-bold text-gray-900">{selectedAppointment.doctorName}</p>
                <p className="text-sm text-gray-500">{selectedAppointment.speciality}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-sahaay-surface">
              <div><p className="text-xs text-gray-500">{t('apt.date')}</p><p className="text-sm font-semibold">{selectedAppointment.date}</p></div>
              <div><p className="text-xs text-gray-500">{t('apt.time')}</p><p className="text-sm font-semibold">{selectedAppointment.time}</p></div>
              <div><p className="text-xs text-gray-500">{t('dash.facilities')}</p><p className="text-sm font-semibold">{selectedAppointment.facility}</p></div>
              <div><p className="text-xs text-gray-500">{t('apt.type')}</p><p className="text-sm font-semibold">{selectedAppointment.type}</p></div>
            </div>
            {selectedAppointment.reason && (
              <div className="rounded-xl bg-sahaay-surface p-4">
                <p className="text-xs text-gray-500">Reason for visit</p>
                <p className="text-sm font-semibold">{selectedAppointment.reason}</p>
              </div>
            )}
            <div className="flex flex-wrap gap-3">
              <Button onClick={() => { showToast('Reschedule request sent'); setSelectedAppointment(null); }}>{t('apt.reschedule')}</Button>
              {selectedAppointment.status === 'upcoming' && (
                <Button variant="ghost" onClick={() => cancelAppointment(selectedAppointment.id)}>
                  {t('apt.cancel')}
                </Button>
              )}
              <Button variant="secondary" onClick={() => setSelectedAppointment(null)}>{t('common.close')}</Button>
            </div>
          </div>
        )}
      </Modal>


      {/* Booking modal */}
      <Modal isOpen={bookingOpen} onClose={() => setBookingOpen(false)} title={t('dash.bookAppointment')} size="lg">
        <div className="space-y-5">
          {/* Doctor picker */}
          <div>
            <label className="mb-1.5 block text-xs font-semibold text-gray-600">Doctor</label>
            <div className="grid gap-2 sm:grid-cols-2">
              {doctors.filter((d) => d.available).map((d) => (
                <button
                  key={d.id}
                  onClick={() => setDoctorId(d.id)}
                  className={`flex items-center gap-3 rounded-xl border p-3 text-left transition-all ${
                    doctorId === d.id ? 'border-sahaay-deep bg-sahaay-deep/6' : 'border-gray-200 hover:bg-white/60'
                  }`}
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-sahaay-deep to-sahaay-500 text-[11px] font-bold text-white">
                    {d.avatar}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold text-gray-900">{d.name}</span>
                    <span className="block truncate text-xs text-gray-500">{d.speciality} · {d.facility}</span>
                  </span>
                  {doctorId === d.id && <CheckCircle2 size={16} className="ml-auto shrink-0 text-sahaay-deep" />}
                </button>
              ))}
            </div>
            <p className="mt-1.5 flex items-center gap-1 text-xs text-gray-500">
              <Stethoscope size={12} /> {selectedDoctor.experience} experience · rating {selectedDoctor.rating}
            </p>
          </div>

          {/* Date + type */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="appt-date" className="mb-1.5 block text-xs font-semibold text-gray-600">Date</label>
              <input
                id="appt-date"
                type="date"
                value={date}
                min={new Date().toISOString().slice(0, 10)}
                onChange={(e) => { setDate(e.target.value); setError(''); }}
                className="sahaay-input"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-semibold text-gray-600">Consultation type</label>
              <div className="flex gap-2">
                {APPOINTMENT_TYPES.map((option) => (
                  <button
                    key={option}
                    onClick={() => setType(option)}
                    className={`flex flex-1 items-center justify-center gap-2 rounded-xl border px-3 py-2.5 text-sm font-medium transition-all ${
                      type === option ? 'border-sahaay-deep bg-sahaay-deep/6 text-sahaay-deep' : 'border-gray-200 text-gray-600 hover:bg-white/60'
                    }`}
                  >
                    {option === 'Video Consultation' ? <Video size={14} /> : <MapPin size={14} />}
                    {option === 'Video Consultation' ? 'Video' : 'In-Person'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Time slots */}
          <div>
            <label className="mb-1.5 block text-xs font-semibold text-gray-600">Time slot</label>
            <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
              {TIME_SLOTS.map((slot) => (
                <button
                  key={slot}
                  onClick={() => { setTime(slot); setError(''); }}
                  className={`rounded-xl border px-2 py-2 text-xs font-semibold transition-all ${
                    time === slot ? 'border-sahaay-deep bg-sahaay-deep text-white' : 'border-gray-200 text-gray-600 hover:bg-white/60'
                  }`}
                >
                  {slot}
                </button>
              ))}
            </div>
          </div>

          {/* Reason */}
          <div>
            <label htmlFor="appt-reason" className="mb-1.5 block text-xs font-semibold text-gray-600">Reason for visit (optional)</label>
            <textarea
              id="appt-reason"
              rows={2}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Blood pressure review, recurring headache"
              className="sahaay-input resize-none"
            />
          </div>

          {error && (
            <p role="alert" className="rounded-xl border border-amber-200/60 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-800">
              {error}
            </p>
          )}

          <div className="flex gap-3">
            <Button onClick={confirmBooking}>Confirm booking</Button>
            <Button variant="secondary" onClick={() => setBookingOpen(false)}>{t('common.cancel')}</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
