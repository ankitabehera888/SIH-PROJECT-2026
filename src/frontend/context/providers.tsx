import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { translations, type Language } from '../i18n/translations';
import {
  notifications as seedPatientNotifications,
  doctorNotifications,
  workerNotifications,
  facilityNotifications,
  referrals as seedReferrals,
} from '../../mock-data/mockData';

/* --- SAHAAY global state ---
   Every provider and hook lives in this one file so the whole app's state
   model is readable top to bottom: language ? user profiles ? theme ?
   notifications ? referrals. Consumed via the use* hooks exported below. */

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => {
    return (localStorage.getItem('sahaay-lang') as Language) || 'en';
  });

  const handleSetLanguage = (lang: Language) => {
    setLanguage(lang);
    localStorage.setItem('sahaay-lang', lang);
  };

  const t = (key: string, params?: Record<string, string | number>): string => {
    let value = translations[language]?.[key] || translations['en']?.[key] || key;
    if (params) {
      for (const [name, raw] of Object.entries(params)) {
        value = value.split(`{${name}}`).join(String(raw));
      }
    }
    return value;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage: handleSetLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}

export type Role = 'patient' | 'doctor' | 'worker' | 'facility';

export interface UserProfile {
  fullName: string;
  email: string;
  phone: string;
  dob: string;
}

interface UserProfileContextType {
  /** The profile of the role currently logged in. */
  profile: UserProfile;
  /** Updates ONLY the active role's profile — other roles keep their own. */
  updateProfile: (patch: Partial<UserProfile>) => void;
  /** Writes a specific role's profile — used by sign-up, before that role is active. */
  updateProfileFor: (role: Role, patch: Partial<UserProfile>) => void;
  /** "Rahul" — used in greetings. Honorifics ("Dr.") are stripped. */
  firstName: string;
  /** "Rahul S." — used in the topbar. */
  shortName: string;
  /** "RS" — used in avatars. */
  initials: string;
}

/* One identity per role: editing your name as a doctor must NOT rename the
   patient, the worker, or the facility admin. */
const DEFAULT_PROFILES: Record<Role, UserProfile> = {
  patient: { fullName: 'Rahul Sharma', email: 'rahul.sharma@email.com', phone: '+91 98765 43210', dob: '1992-05-15' },
  doctor: { fullName: 'Ananya Sharma', email: 'dr.ananya@phc-chandrapur.in', phone: '+91 98760 10001', dob: '1988-03-22' },
  worker: { fullName: 'Meena Kumari', email: 'meena.k@asha-worker.in', phone: '+91 98765 11111', dob: '1990-07-08' },
  facility: { fullName: 'Facility Admin', email: 'admin@phc-chandrapur.in', phone: '+91 98765 22222', dob: '1985-01-01' },
};

const PROFILE_STORAGE_KEY = 'sahaay-profiles';
const LEGACY_KEY = 'sahaay-profile';

function loadProfiles(): Record<Role, UserProfile> {
  let stored: Partial<Record<Role, Partial<UserProfile>>> = {};
  try {
    const raw = localStorage.getItem(PROFILE_STORAGE_KEY);
    if (raw) stored = JSON.parse(raw) as typeof stored;
  } catch {
    /* corrupted storage — fall back to defaults */
  }
  const merged = { ...DEFAULT_PROFILES };
  (Object.keys(DEFAULT_PROFILES) as Role[]).forEach((role) => {
    merged[role] = { ...DEFAULT_PROFILES[role], ...stored[role] };
  });
  /* One-time migration: the original single-profile build stored the edited
     details under 'sahaay-profile'. They belong to the patient login. */
  try {
    const legacy = localStorage.getItem(LEGACY_KEY);
    if (legacy) {
      merged.patient = { ...merged.patient, ...(JSON.parse(legacy) as Partial<UserProfile>) };
      localStorage.removeItem(LEGACY_KEY);
    }
  } catch {
    /* ignore */
  }
  return merged;
}

/* "Dr. Ananya Sharma" → ["Ananya", "Sharma"] so greetings never read
   "Dr. Dr. …" and initials never come out as "DR". */
function nameParts(fullName: string): string[] {
  return fullName
    .trim()
    .split(/\s+/)
    .filter((part) => part && !/^(dr|mr|mrs|ms|shri|smt)\.?$/i.test(part));
}

const UserProfileContext = createContext<UserProfileContextType>({
  profile: DEFAULT_PROFILES.patient,
  updateProfile: () => {},
  updateProfileFor: () => {},
  firstName: 'Rahul',
  shortName: 'Rahul S.',
  initials: 'RS',
});

export function UserProfileProvider({ role, children }: { role: Role; children: ReactNode }) {
  const [profiles, setProfiles] = useState<Record<Role, UserProfile>>(loadProfiles);

  const profile = profiles[role] ?? DEFAULT_PROFILES.patient;

  const updateProfile = (patch: Partial<UserProfile>) => {
    setProfiles((prev) => {
      const next = { ...prev, [role]: { ...prev[role], ...patch } };
      localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  const updateProfileFor = (targetRole: Role, patch: Partial<UserProfile>) => {
    setProfiles((prev) => {
      const next = { ...prev, [targetRole]: { ...prev[targetRole], ...patch } };
      localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  const parts = nameParts(profile.fullName);
  const firstName = parts[0] || 'User';
  const lastName = parts.length > 1 ? parts[parts.length - 1] : '';
  const shortName = lastName ? `${firstName} ${lastName[0].toUpperCase()}.` : firstName;
  const initials = (
    parts.length > 1
      ? parts[0][0] + parts[parts.length - 1][0]
      : (parts[0] || 'U').slice(0, 2)
  ).toUpperCase();

  return (
    <UserProfileContext.Provider value={{ profile, updateProfile, updateProfileFor, firstName, shortName, initials }}>
      {children}
    </UserProfileContext.Provider>
  );
}

export function useUserProfile() {
  return useContext(UserProfileContext);
}

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const THEME_STORAGE_KEY = 'sahaay-theme';

const ThemeContext = createContext<ThemeContextType>({ theme: 'light', toggleTheme: () => {} });

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    return localStorage.getItem(THEME_STORAGE_KEY) === 'dark' ? 'dark' : 'light';
  });

  /* All dark styling keys off the data-theme attribute on <html> — the heavy
     lifting lives in index.css ([data-theme='dark'] token remaps), this just
     flips the switch and persists it. */
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'light' ? 'dark' : 'light'));

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  time: string;
  type: string;
  read: boolean;
}

interface NotificationContextType {
  /** Notifications for the role currently logged in. */
  items: AppNotification[];
  unreadCount: number;
  markRead: (id: string) => void;
  markAllRead: () => void;
}

/* Each role sees its own inbox — a doctor should not read the patient's
   reminders, and the badge in the topbar counts the right person's unread. */
const SEED: Record<Role, AppNotification[]> = {
  patient: seedPatientNotifications,
  doctor: doctorNotifications,
  worker: workerNotifications,
  facility: facilityNotifications,
};

const NotificationContext = createContext<NotificationContextType>({
  items: [],
  unreadCount: 0,
  markRead: () => {},
  markAllRead: () => {},
});

export function NotificationProvider({ role, children }: { role: Role; children: ReactNode }) {
  /* Cloned per role so marking something read never mutates the seed data —
     signing out and back in returns to the original inbox. */
  const [byRole, setByRole] = useState<Record<Role, AppNotification[]>>(() => ({
    patient: SEED.patient.map((n) => ({ ...n })),
    doctor: SEED.doctor.map((n) => ({ ...n })),
    worker: SEED.worker.map((n) => ({ ...n })),
    facility: SEED.facility.map((n) => ({ ...n })),
  }));

  const items = byRole[role] ?? [];

  const markRead = (id: string) => {
    setByRole((prev) => ({
      ...prev,
      [role]: prev[role].map((n) => (n.id === id ? { ...n, read: true } : n)),
    }));
  };

  const markAllRead = () => {
    setByRole((prev) => ({
      ...prev,
      [role]: prev[role].map((n) => (n.read ? n : { ...n, read: true })),
    }));
  };

  const unreadCount = items.filter((n) => !n.read).length;

  return (
    <NotificationContext.Provider value={{ items, unreadCount, markRead, markAllRead }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  return useContext(NotificationContext);
}

export type ReferralStatus =
  | 'pending'
  | 'accepted'
  | 'appointment_scheduled'
  | 'in_transit'
  | 'completed'
  | 'followup_required';

export interface Referral {
  id: string;
  patientId: string;
  patientName: string;
  sourceFacility: string;
  destinationFacility: string;
  reason: string;
  priority: string;
  status: ReferralStatus;
  createdDate: string;
  expectedDate: string;
  assignedDoctor: string;
  notes: string;
}

export interface NewReferralDraft {
  patientId: string;
  patientName: string;
  sourceFacility: string;
  destinationFacility: string;
  reason: string;
  priority: string;
  expectedDate: string;
  assignedDoctor: string;
  notes: string;
}

/* Forward path a referral walks. `followup_required` is a side exit that can
   still be closed out as completed. */
const FLOW: ReferralStatus[] = ['pending', 'accepted', 'appointment_scheduled', 'in_transit', 'completed'];

export function nextStatus(status: ReferralStatus): ReferralStatus | null {
  if (status === 'followup_required') return 'completed';
  const index = FLOW.indexOf(status);
  if (index === -1 || index === FLOW.length - 1) return null;
  return FLOW[index + 1];
}

export const STATUS_ACTION_LABEL: Partial<Record<ReferralStatus, string>> = {
  accepted: 'Accept referral',
  appointment_scheduled: 'Schedule appointment',
  in_transit: 'Mark in transit',
  completed: 'Mark completed',
};

/* The logged-in patient in the demo dataset. */
export const SELF_PATIENT_ID = 'P001';
/* Referrals owned by the demo doctor login. */
export const SELF_DOCTOR_NAME = 'Dr. Ananya Sharma';

interface ReferralContextType {
  referrals: Referral[];
  createReferral: (draft: NewReferralDraft) => Referral;
  advance: (id: string) => void;
  setStatus: (id: string, status: ReferralStatus) => void;
}

const ReferralContext = createContext<ReferralContextType>({
  referrals: [],
  createReferral: () => ({}) as Referral,
  advance: () => {},
  setStatus: () => {},
});

const today = () => new Date().toISOString().slice(0, 10);

export function ReferralProvider({ children }: { children: ReactNode }) {
  /* One shared register: a referral raised by the field worker is immediately
     visible to the doctor who must accept it and to the patient tracking it. */
  const [referrals, setReferrals] = useState<Referral[]>(() =>
    seedReferrals.map((r) => ({ ...r, status: r.status as ReferralStatus })),
  );

  const createReferral = (draft: NewReferralDraft): Referral => {
    const created: Referral = {
      id: `R${String(referrals.length + 100).padStart(3, '0')}`,
      ...draft,
      status: 'pending',
      createdDate: today(),
    };
    setReferrals((prev) => [created, ...prev]);
    return created;
  };

  const setStatus = (id: string, status: ReferralStatus) => {
    setReferrals((prev) => prev.map((r) => (r.id === id ? { ...r, status } : r)));
  };

  const advance = (id: string) => {
    setReferrals((prev) =>
      prev.map((r) => {
        if (r.id !== id) return r;
        const next = nextStatus(r.status);
        return next ? { ...r, status: next } : r;
      }),
    );
  };

  return (
    <ReferralContext.Provider value={{ referrals, createReferral, advance, setStatus }}>
      {children}
    </ReferralContext.Provider>
  );
}

export function useReferrals() {
  return useContext(ReferralContext);
}
