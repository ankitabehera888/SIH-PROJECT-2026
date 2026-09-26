import { motion } from 'framer-motion';
import type { ReactNode } from 'react';
import { Users, Clock, ClipboardList, Stethoscope, Video, FileText, AlertTriangle, ChevronRight, MapPin } from 'lucide-react';
import { StatCard } from '../../components/ui/StatCard';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Button } from '../../components/ui/Button';
import { patients } from '../../../mock-data/mockData';
import { useToast } from '../../components/ui/Toast';
import { useTimeGreeting } from '../../hooks/useTimeGreeting';
import { useUserProfile } from '../../context/providers';

interface QueueItem {
  patient: (typeof patients)[number];
  time: string;
  reason: string;
  mode: 'Video' | 'In-Person';
  priority: string;
}

interface QueueCardProps {
  title: string;
  icon: ReactNode;
  items: QueueItem[];
  delay: number;
  action: { label: string; icon: ReactNode; route: string };
  viewAllRoute: string;
  emptyMessage: string;
  onNavigate: (route: string) => void;
}

/** One segment of today's schedule. The dashboard renders two of these — an
    in-person list and a video list — so each mode reads as its own queue
    instead of one mixed timeline. */
function QueueCard({ title, icon, items, delay, action, viewAllRoute, emptyMessage, onNavigate }: QueueCardProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }} className="glass-card-elevated p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sahaay-deep/10 text-sahaay-deep"
          >
            {icon}
          </span>
          <div>
            <h2 className="text-lg font-bold text-gray-900">{title}</h2>
            <p className="text-sm text-gray-500">{items.length} patients scheduled</p>
          </div>
        </div>
        <Button variant="secondary" size="sm" onClick={() => onNavigate(viewAllRoute)}>View All <ChevronRight size={14} /></Button>
      </div>

      <div className="space-y-3">
        {items.length === 0 && (
          <div className="py-10 text-center text-sm text-gray-500">{emptyMessage}</div>
        )}
        {items.map((item, i) => (
          <motion.div
            key={item.patient.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.05 * i }}
            className="flex flex-col sm:flex-row sm:items-center gap-3 p-4 rounded-xl bg-white/60 border border-gray-100 hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-3 flex-1">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sahaay-deep to-sahaay-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
                {item.patient.avatar}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-bold text-gray-900">{item.patient.name}</p>
                  <StatusBadge status={item.priority} />
                  <span className="text-[10px] text-gray-400">{item.patient.age} yrs</span>
                </div>
                <p className="text-xs text-gray-500">{item.reason}</p>
                <p className="text-[10px] text-gray-400 flex items-center gap-1 mt-0.5">
                  <MapPin size={10} />{item.patient.location}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 text-xs text-gray-500 shrink-0">
              <span className="flex items-center gap-1"><Clock size={12} className="text-sahaay-deep" />{item.time}</span>
            </div>

            <div className="flex gap-2 shrink-0">
              <Button size="sm" onClick={() => onNavigate(action.route)}>
                {action.icon} {action.label}
              </Button>
              <Button size="sm" variant="secondary" onClick={() => onNavigate('/doctor/patients')}>
                <FileText size={14} />
              </Button>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

interface DoctorDashboardProps {
  onNavigate: (route: string) => void;
}

export function DoctorDashboard({ onNavigate }: DoctorDashboardProps) {
  const { showToast } = useToast();
  // The greeting was the only translated string on this screen, and it now
  // comes from the hook (which localizes it itself), so `useLanguage` is gone.
  const { greeting, Icon: TimeIcon, tint } = useTimeGreeting();
  const { firstName } = useUserProfile();

  const todayQueue: QueueItem[] = [
    { patient: patients[0], time: '11:30 AM', reason: 'Hypertension follow-up', mode: 'Video', priority: 'high' },
    { patient: patients[1], time: '12:00 PM', reason: 'Prenatal checkup', mode: 'In-Person', priority: 'high' },
    { patient: patients[3], time: '02:30 PM', reason: 'Knee pain consultation', mode: 'Video', priority: 'normal' },
    { patient: patients[4], time: '03:00 PM', reason: 'Blood work review', mode: 'In-Person', priority: 'normal' },
    { patient: patients[5], time: '03:30 PM', reason: 'Thyroid monitoring', mode: 'Video', priority: 'low' },
  ];
  const inPersonQueue = todayQueue.filter((item) => item.mode === 'In-Person');
  const videoQueue = todayQueue.filter((item) => item.mode === 'Video');

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="relative overflow-hidden glass-card-elevated p-6 lg:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-blue-100/40 to-transparent rounded-full blur-3xl -translate-y-1/3 translate-x-1/3" />
        <img
          src="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=800&q=80"
          alt=""
          loading="lazy"
          className="pointer-events-none absolute inset-y-0 right-0 hidden w-2/5 object-cover opacity-20 lg:block [mask-image:linear-gradient(to_left,black_35%,transparent)]"
        />
        <div className="relative">
          {/* Live greeting: sunrise → sun → sunset → moon as the day turns.
              A lucide glyph replaces the 👋 emoji, which renders differently on
              every platform and is announced literally by screen readers. */}
          <h1 className="flex flex-wrap items-center gap-x-3 gap-y-2 font-display text-2xl font-bold text-ink-900 lg:text-3xl">
            <span
              aria-hidden="true"
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl"
              style={{ color: tint, background: `${tint}1A`, boxShadow: `inset 0 0 0 1px ${tint}33` }}
            >
              <TimeIcon size={19} />
            </span>
            <span>{greeting}, Dr. {firstName}</span>
          </h1>
          <p className="mt-1.5 text-ink-500">Here's your clinical workload for today.</p>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Today's Patients" value={12} icon={<Users size={22} />} delay={0.05} />
        <StatCard title="Pending Consultations" value={4} icon={<Stethoscope size={22} />} delay={0.1} />
        <StatCard title="Pending Referrals" value={6} icon={<ClipboardList size={22} />} delay={0.15} />
        <StatCard title="Follow-ups Due" value={8} icon={<Clock size={22} />} delay={0.2} />
      </div>

      {/* Today's Queue — split so clinic visits and tele-consults read as two lists */}
      <QueueCard
        title="In-Person Queue"
        icon={<Stethoscope size={18} />}
        items={inPersonQueue}
        delay={0.25}
        action={{ label: 'Consult', icon: <Stethoscope size={14} />, route: '/doctor/appointments' }}
        viewAllRoute="/doctor/appointments"
        emptyMessage="No in-person visits scheduled today."
        onNavigate={onNavigate}
      />
      <QueueCard
        title="Video Consultations"
        icon={<Video size={18} />}
        items={videoQueue}
        delay={0.3}
        action={{ label: 'Start', icon: <Video size={14} />, route: '/doctor/consultation' }}
        viewAllRoute="/doctor/consultation"
        emptyMessage="No video consultations scheduled today."
        onNavigate={onNavigate}
      />

      {/* Bottom row */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Pending referrals */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-5">
          <h3 className="text-sm font-bold text-gray-900 mb-3">Pending Referrals</h3>
          <div className="space-y-2">
            {[
              { patient: 'Priya Devi', from: 'RHC Dhekiajuli', reason: 'Diabetes management' },
              { patient: 'Amit Kumar', from: 'PHC Chandrapur', reason: 'Knee pain evaluation' },
              { patient: 'Rakesh Singh', from: 'CHC Sonapur', reason: 'Iron deficiency workup' },
            ].map((r, i) => (
              <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-sahaay-surface text-sm">
                <div>
                  <p className="font-semibold text-gray-900">{r.patient}</p>
                  <p className="text-xs text-gray-500">{r.from} · {r.reason}</p>
                </div>
                <Button size="sm" variant="ghost" onClick={() => showToast('Referral reviewed')}>Review</Button>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Follow-up alerts */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }} className="glass-card p-5">
          <h3 className="text-sm font-bold text-gray-900 mb-3">Follow-up Alerts</h3>
          <div className="space-y-2">
            {[
              { patient: 'Dipak Gogoi', condition: 'Post-surgery recovery', due: 'Sep 10' },
              { patient: 'Priya Devi', condition: 'HbA1c monitoring', due: 'Aug 28 (Overdue)' },
              { patient: 'Rakesh Singh', condition: 'Blood test review', due: 'Sep 5' },
            ].map((f, i) => (
              <div key={i} className={`flex items-center justify-between p-2.5 rounded-lg text-sm ${f.due.includes('Overdue') ? 'bg-red-50' : 'bg-sahaay-surface'}`}>
                <div>
                  <p className="font-semibold text-gray-900">{f.patient}</p>
                  <p className="text-xs text-gray-500">{f.condition} · Due: {f.due}</p>
                </div>
                {f.due.includes('Overdue') && <AlertTriangle size={16} className="text-red-500" />}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
