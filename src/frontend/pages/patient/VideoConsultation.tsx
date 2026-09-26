import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Mic, MicOff, Video, VideoOff, PhoneOff, Monitor, MessageSquare, MoreVertical, Clock
} from 'lucide-react';
import { Avatar } from '../../components/ui/Avatar';
import { Button } from '../../components/ui/Button';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';
import { useUserProfile } from '../../context/providers';

export function VideoConsultation() {
  const [muted, setMuted] = useState(false);
  const { t } = useLanguage();
  const [videoOff, setVideoOff] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [showEndConfirm, setShowEndConfirm] = useState(false);
  const { showToast } = useToast();
  const { profile, initials } = useUserProfile();

  const patientTabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'symptoms', label: 'Symptoms' },
    { id: 'history', label: 'History' },
    { id: 'prescriptions', label: 'Prescriptions' },
    { id: 'notes', label: 'Notes' },
  ];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('dash.videoConsultation')}</h1>
          <p className="text-sm text-gray-500 mt-1">Consultation with Dr. Ananya Sharma — PHC Chandrapur</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-700 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse-soft" /> In Progress
          </span>
          <span className="text-sm text-gray-500"><Clock size={14} className="inline mr-1" />12:34</span>
        </div>
      </motion.div>

      <div className="flex flex-col lg:flex-row gap-4" style={{ height: 'calc(100vh - 200px)', minHeight: 500 }}>
        {/* Main video area */}
        <div className="flex-1 relative rounded-2xl overflow-hidden bg-gradient-to-br from-gray-900 to-gray-800">
          {/* Mock doctor video */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Avatar initials="AS" size="xl" color="from-blue-600 to-blue-400" />
              <p className="text-white font-bold mt-4 text-lg">Dr. Ananya Sharma</p>
              <p className="text-white/60 text-sm">General Physician · PHC Chandrapur</p>
              <div className="mt-4 flex items-center justify-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-soft" />
                <span className="text-emerald-400 text-xs font-medium">Connected</span>
              </div>
            </div>
          </div>

          {/* Patient preview (small) */}
          <div className="absolute bottom-4 right-4 w-36 h-24 rounded-xl overflow-hidden border-2 border-white/20 bg-gray-800">
            <div className="w-full h-full flex items-center justify-center">
              {videoOff ? (
                <Avatar initials="RS" size="md" />
              ) : (
                <div className="text-center">
                  <Avatar initials="RS" size="sm" />
                  <p className="text-white/80 text-[10px] mt-1">You</p>
                </div>
              )}
            </div>
          </div>

          {/* Timer overlay */}
          <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-1.5 rounded-lg bg-black/40 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse-soft" />
            <span className="text-white text-xs font-medium">00:12:34</span>
          </div>
        </div>

        {/* Right panel - Patient info */}
        <div className="w-full lg:w-80 glass-card-elevated flex flex-col shrink-0">
          <div className="p-4 border-b border-gray-100">
            <h3 className="text-sm font-bold text-gray-900">Patient Information</h3>
            <div className="flex items-center gap-2 mt-2">
              <Avatar initials={initials} size="sm" />
              <div>
                <p className="text-sm font-semibold">{profile.fullName}</p>
                <p className="text-[11px] text-gray-500">34 yrs · Male · B+ · ID: P001</p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-100 overflow-x-auto">
            {patientTabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-2 text-xs font-medium whitespace-nowrap transition-all ${
                  activeTab === tab.id ? 'text-sahaay-deep border-b-2 border-sahaay-deep' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {activeTab === 'overview' && (
              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Blood Pressure</p><p className="text-sm font-bold">142/92 mmHg</p></div>
                <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Heart Rate</p><p className="text-sm font-bold">78 bpm</p></div>
                <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Temperature</p><p className="text-sm font-bold">98.6°F</p></div>
                <div className="p-3 rounded-xl bg-sahaay-surface"><p className="text-xs text-gray-500">Conditions</p><p className="text-sm font-bold">Hypertension, Mild Anemia</p></div>
              </div>
            )}
            {activeTab === 'symptoms' && (
              <div className="space-y-2">
                {['Headache (2 weeks)', 'Mild dizziness', 'Occasional chest discomfort'].map((s, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-sahaay-surface text-sm text-gray-700">
                    <span className="w-2 h-2 rounded-full bg-sahaay-deep shrink-0" />{s}
                  </div>
                ))}
              </div>
            )}
            {activeTab === 'history' && (
              <div className="space-y-2">
                {['Aug 12 — PHC Consultation', 'Aug 18 — Blood Test', 'Aug 28 — Specialist Consultation'].map((h, i) => (
                  <div key={i} className="flex items-start gap-2 p-2 text-sm text-gray-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-sahaay-deep mt-1.5 shrink-0" />{h}
                  </div>
                ))}
              </div>
            )}
            {activeTab === 'prescriptions' && (
              <div className="space-y-2">
                {['Amlodipine 5mg — Once daily', 'Aspirin 75mg — Once daily', 'Iron Supplement — Twice daily'].map((p, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-sahaay-surface text-sm text-gray-700">
                    <span className="text-sahaay-deep">💊</span>{p}
                  </div>
                ))}
              </div>
            )}
            {activeTab === 'notes' && (
              <div className="p-3 rounded-xl bg-sahaay-surface">
                <textarea placeholder="Add clinical notes..." className="w-full bg-transparent text-sm outline-none resize-none h-24" />
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="p-3 border-t border-gray-100 space-y-2">
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" className="flex-1" onClick={() => showToast('Prescription added')}>Add Rx</Button>
              <Button size="sm" variant="secondary" className="flex-1" onClick={() => showToast('Notes saved')}>Add Notes</Button>
            </div>
            <Button size="sm" variant="outline" className="w-full" onClick={() => showToast('Referral created')}>Refer Patient</Button>
          </div>
        </div>
      </div>

      {/* Bottom controls */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <div className="glass-card-elevated px-6 py-4 flex items-center justify-center gap-3">
          <button onClick={() => setMuted(!muted)} className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${muted ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
            {muted ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <button onClick={() => setVideoOff(!videoOff)} className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${videoOff ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>
            {videoOff ? <VideoOff size={20} /> : <Video size={20} />}
          </button>
          <button className="w-12 h-12 rounded-2xl bg-gray-100 text-gray-700 flex items-center justify-center hover:bg-gray-200 transition-all">
            <Monitor size={20} />
          </button>
          <button className="w-12 h-12 rounded-2xl bg-gray-100 text-gray-700 flex items-center justify-center hover:bg-gray-200 transition-all">
            <MessageSquare size={20} />
          </button>
          <button className="w-12 h-12 rounded-2xl bg-gray-100 text-gray-700 flex items-center justify-center hover:bg-gray-200 transition-all">
            <MoreVertical size={20} />
          </button>
          <div className="w-px h-8 bg-gray-200 mx-2" />
          <button onClick={() => setShowEndConfirm(true)} className="w-12 h-12 rounded-2xl bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-all shadow-lg shadow-red-500/25">
            <PhoneOff size={20} />
          </button>
        </div>
      </motion.div>

      {/* End call confirmation */}
      {showEndConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowEndConfirm(false)} />
          <div className="relative glass-card-elevated p-6 max-w-sm w-full text-center">
            <h3 className="text-lg font-bold text-gray-900 mb-2">End Consultation?</h3>
            <p className="text-sm text-gray-500 mb-6">Are you sure you want to end this video consultation?</p>
            <div className="flex gap-3">
              <Button variant="secondary" className="flex-1" onClick={() => setShowEndConfirm(false)}>Continue</Button>
              <Button variant="danger" className="flex-1" onClick={() => { setShowEndConfirm(false); showToast('Consultation ended'); }}>End Call</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
