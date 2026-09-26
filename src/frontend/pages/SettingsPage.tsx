import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { User, Bell, Globe, Eye, Shield, Phone, Palette } from 'lucide-react';
import { useToast } from '../components/ui/Toast';
import { useLanguage } from '../context/providers';
import { useUserProfile } from '../context/providers';
import { useTheme } from '../context/providers';

function readJSON<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return { ...fallback, ...JSON.parse(raw) } as T;
  } catch {
    return fallback;
  }
}

function writeJSON(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable — settings still work for this session */
  }
}

export function SettingsPage() {
  const [activeSection, setActiveSection] = useState('profile');
  const { t, language, setLanguage } = useLanguage();
  const { showToast } = useToast();
  const { theme, toggleTheme } = useTheme();

  /* --- Persisted settings state: every toggle actually flips + persists --- */
  const [notifPrefs, setNotifPrefs] = useState(() =>
    readJSON('sahaay-settings-notifications', {
      appointmentReminders: true,
      followupAlerts: true,
      referralUpdates: true,
      medicineAvailability: false,
      doctorMessages: true,
    })
  );
  useEffect(() => writeJSON('sahaay-settings-notifications', notifPrefs), [notifPrefs]);

  const [largeText, setLargeText] = useState(() => localStorage.getItem('sahaay-a11y-large-text') === '1');
  const [highContrast, setHighContrast] = useState(() => localStorage.getItem('sahaay-a11y-high-contrast') === '1');
  const [reduceMotion, setReduceMotion] = useState(() => localStorage.getItem('sahaay-a11y-reduce-motion') === '1');
  const [voiceAssist, setVoiceAssist] = useState(() => localStorage.getItem('sahaay-a11y-voice') === '1');

  /* Apply accessibility prefs to the whole app so the toggles have real effect. */
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle('a11y-large-text', largeText);
    root.style.fontSize = largeText ? '18px' : '';
    try { localStorage.setItem('sahaay-a11y-large-text', largeText ? '1' : '0'); } catch { /* ignore */ }
  }, [largeText]);
  useEffect(() => {
    document.documentElement.classList.toggle('a11y-high-contrast', highContrast);
    try { localStorage.setItem('sahaay-a11y-high-contrast', highContrast ? '1' : '0'); } catch { /* ignore */ }
  }, [highContrast]);
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle('a11y-reduce-motion', reduceMotion);
    root.style.setProperty('--motion-off', reduceMotion ? '1' : '0');
    try { localStorage.setItem('sahaay-a11y-reduce-motion', reduceMotion ? '1' : '0'); } catch { /* ignore */ }
  }, [reduceMotion]);
  useEffect(() => {
    try { localStorage.setItem('sahaay-a11y-voice', voiceAssist ? '1' : '0'); } catch { /* ignore */ }
  }, [voiceAssist]);

  const [privacyPrefs, setPrivacyPrefs] = useState(() =>
    readJSON('sahaay-settings-privacy', {
      shareRecords: true,
      facilityHistory: true,
      coordinatorProfile: true,
      anonymousAnalytics: false,
    })
  );
  useEffect(() => writeJSON('sahaay-settings-privacy', privacyPrefs), [privacyPrefs]);

  const [emergency, setEmergency] = useState(() =>
    readJSON('sahaay-settings-emergency', {
      name: 'Priya Sharma',
      relationship: 'Spouse',
      phone: '+91 98765 43211',
    })
  );

  const [compactView, setCompactView] = useState(() => localStorage.getItem('sahaay-display-compact') === '1');
  const [healthTips, setHealthTips] = useState(() => localStorage.getItem('sahaay-display-tips') !== '0');
  useEffect(() => {
    document.documentElement.classList.toggle('display-compact', compactView);
    try { localStorage.setItem('sahaay-display-compact', compactView ? '1' : '0'); } catch { /* ignore */ }
  }, [compactView]);
  useEffect(() => {
    try { localStorage.setItem('sahaay-display-tips', healthTips ? '1' : '0'); } catch { /* ignore */ }
  }, [healthTips]);
  const { profile, updateProfile } = useUserProfile();
  /* Local draft so typing doesn't repaint the topbar/sidebar on every
     keystroke — the rest of the app updates when Save is pressed. */
  const [form, setForm] = useState(profile);

  /* Each role has its own profile — if the login role changes while this
     page is open, reload the draft for the newly active identity. (State
     adjusted during render, per React docs — no effect needed.) */
  const [loadedProfile, setLoadedProfile] = useState(profile);
  if (loadedProfile !== profile) {
    setLoadedProfile(profile);
    setForm(profile);
  }

  const saveProfile = () => {
    updateProfile({
      fullName: form.fullName.trim() || profile.fullName,
      email: form.email.trim(),
      phone: form.phone.trim(),
      dob: form.dob,
    });
    showToast('Profile updated');
  };

  const sections = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'language', label: 'Language', icon: Globe },
    { id: 'accessibility', label: 'Accessibility', icon: Eye },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'emergency', label: 'Emergency Contact', icon: Phone },
    { id: 'display', label: 'Display Preferences', icon: Palette },
  ];

  const Toggle = ({ checked, onChange }: { checked: boolean; onChange: () => void }) => (
    <button type="button" role="switch" aria-checked={checked} onClick={onChange} className={`w-11 h-6 rounded-full transition-colors shrink-0 ${checked ? 'bg-sahaay-deep' : 'bg-gray-300'} relative`}>
      <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${checked ? 'translate-x-[22px]' : 'translate-x-[2px]'} mt-[2px]`} />
    </button>
  );

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-gray-900">{t('dash.settings')}</h1>
        <p className="text-sm text-gray-500 mt-1">Manage your account preferences and accessibility settings.</p>
      </motion.div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-64 shrink-0">
          <div className="glass-card p-2 flex lg:flex-col gap-1 overflow-x-auto">
            {sections.map(s => {
              const Icon = s.icon;
              return (
                <button
                  key={s.id}
                  onClick={() => setActiveSection(s.id)}
                  className={`flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                    activeSection === s.id ? 'bg-sahaay-deep text-white' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={16} />
                  {s.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 glass-card-elevated p-6">
          {activeSection === 'profile' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-gray-900">Profile Settings</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <div><label className="block text-xs font-semibold text-gray-600 mb-1">Full Name</label><input type="text" value={form.fullName} onChange={(e) => setForm({ ...form, fullName: e.target.value })} className="sahaay-input" /></div>
                <div><label className="block text-xs font-semibold text-gray-600 mb-1">Email</label><input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="sahaay-input" /></div>
                <div><label className="block text-xs font-semibold text-gray-600 mb-1">Phone</label><input type="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="sahaay-input" /></div>
                <div><label className="block text-xs font-semibold text-gray-600 mb-1">Date of Birth</label><input type="date" value={form.dob} onChange={(e) => setForm({ ...form, dob: e.target.value })} className="sahaay-input" /></div>
              </div>
              <button className="sahaay-btn-primary" onClick={saveProfile}>Save Changes</button>
            </div>
          )}

          {activeSection === 'notifications' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-gray-900">Notification Preferences</h2>
              {[
                { key: 'appointmentReminders' as const, label: 'Appointment reminders', desc: 'Get notified before appointments' },
                { key: 'followupAlerts' as const, label: 'Follow-up alerts', desc: 'Notifications for upcoming follow-ups' },
                { key: 'referralUpdates' as const, label: 'Referral updates', desc: 'Updates on referral status changes' },
                { key: 'medicineAvailability' as const, label: 'Medicine availability', desc: 'When medicines become available' },
                { key: 'doctorMessages' as const, label: 'Messages from doctors', desc: 'New messages from healthcare providers' },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-3 rounded-xl bg-sahaay-surface">
                  <div><p className="text-sm font-semibold">{item.label}</p><p className="text-xs text-gray-500">{item.desc}</p></div>
                  <Toggle checked={notifPrefs[item.key]} onChange={() => { setNotifPrefs(p => ({ ...p, [item.key]: !p[item.key] })); showToast('Notification setting updated'); }} />
                </div>
              ))}
            </div>
          )}

          {activeSection === 'language' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-gray-900">Language Settings</h2>
              <div className="space-y-2">
                {[
                  { code: 'en' as const, label: 'English', native: 'English' },
                  { code: 'hi' as const, label: 'Hindi', native: 'हिन्दी' },
                  { code: 'mr' as const, label: 'Marathi', native: 'मराठी' },
                ].map(opt => (
                  <button
                    key={opt.code}
                    onClick={() => { setLanguage(opt.code); showToast('Language updated'); }}
                    className={`w-full flex items-center justify-between p-3 rounded-xl transition-all ${
                      language === opt.code ? 'bg-sahaay-deep text-white' : 'bg-sahaay-surface hover:bg-sahaay-deep/5'
                    }`}
                  >
                    <span className="text-sm font-medium">{opt.native} ({opt.label})</span>
                    {language === opt.code && <span className="text-xs font-bold">✓ Selected</span>}
                  </button>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'accessibility' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-gray-900">Accessibility</h2>
              <div className="space-y-3">
                {[
                  { label: 'Large Text', desc: 'Increase text size across the application', checked: largeText, onChange: () => { setLargeText(v => !v); showToast('Accessibility setting updated'); } },
                  { label: 'High Contrast', desc: 'Increase contrast for better visibility', checked: highContrast, onChange: () => { setHighContrast(v => !v); showToast('Accessibility setting updated'); } },
                  { label: 'Reduce Motion', desc: 'Minimize animations and transitions', checked: reduceMotion, onChange: () => { setReduceMotion(v => !v); showToast('Accessibility setting updated'); } },
                  { label: 'Voice Assistance', desc: 'Screen reader optimized navigation', checked: voiceAssist, onChange: () => { setVoiceAssist(v => !v); showToast('Voice assistance updated'); } },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-sahaay-surface">
                    <div><p className="text-sm font-semibold">{item.label}</p><p className="text-xs text-gray-500">{item.desc}</p></div>
                    <Toggle checked={item.checked} onChange={item.onChange} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'privacy' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-gray-900">Privacy Settings</h2>
              <div className="space-y-3">
                {[
                  { key: 'shareRecords' as const, label: 'Share health records with doctors' },
                  { key: 'facilityHistory' as const, label: 'Allow facility to access appointment history' },
                  { key: 'coordinatorProfile' as const, label: 'Show profile to care coordinator' },
                  { key: 'anonymousAnalytics' as const, label: 'Anonymous analytics' },
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between p-3 rounded-xl bg-sahaay-surface">
                    <span className="text-sm font-medium">{item.label}</span>
                    <Toggle checked={privacyPrefs[item.key]} onChange={() => { setPrivacyPrefs(p => ({ ...p, [item.key]: !p[item.key] })); showToast('Privacy setting updated'); }} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'emergency' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-gray-900">Emergency Contact</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <div><label className="block text-xs font-semibold text-gray-600 mb-1">Contact Name</label><input type="text" value={emergency.name} onChange={(e) => setEmergency({ ...emergency, name: e.target.value })} className="sahaay-input" /></div>
                <div><label className="block text-xs font-semibold text-gray-600 mb-1">Relationship</label><input type="text" value={emergency.relationship} onChange={(e) => setEmergency({ ...emergency, relationship: e.target.value })} className="sahaay-input" /></div>
                <div><label className="block text-xs font-semibold text-gray-600 mb-1">Phone Number</label><input type="tel" value={emergency.phone} onChange={(e) => setEmergency({ ...emergency, phone: e.target.value })} className="sahaay-input" /></div>
              </div>
              <button className="sahaay-btn-primary" onClick={() => { writeJSON('sahaay-settings-emergency', emergency); showToast('Emergency contact updated'); }}>Save Contact</button>
            </div>
          )}

          {activeSection === 'display' && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold text-gray-900">Display Preferences</h2>
              <div className="space-y-3">
                {[
                  { label: 'Compact view', desc: 'Show more information with less spacing', checked: compactView, onChange: () => { setCompactView(v => !v); showToast('Display preference updated'); } },
                  { label: 'Show health tips', desc: 'Display daily health tips on dashboard', checked: healthTips, onChange: () => { setHealthTips(v => !v); showToast('Display preference updated'); } },
                  { label: 'Dark mode', desc: 'Switch between light and dark theme', checked: theme === 'dark', onChange: () => { toggleTheme(); showToast('Theme updated'); } },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-sahaay-surface">
                    <div><p className="text-sm font-semibold">{item.label}</p><p className="text-xs text-gray-500">{item.desc}</p></div>
                    <Toggle checked={item.checked} onChange={item.onChange} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
