import { useState, useCallback, useEffect, lazy, Suspense, type ReactNode } from 'react';
import { ToastProvider } from './components/ui/Toast';
import { AppShell } from './components/layout/AppShell';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { SignUpPage } from './pages/SignUpPage';
import { PatientDashboard } from './pages/patient/PatientDashboard';
import { PatientAppointments } from './pages/patient/PatientAppointments';
import { PatientRecords } from './pages/patient/PatientRecords';
import { PatientReferrals } from './pages/patient/PatientReferrals';
import { PatientFacilities } from './pages/patient/PatientFacilities';
import { PatientDiagnostics } from './pages/patient/PatientDiagnostics';
import { PatientMedicines } from './pages/patient/PatientMedicines';
import { PatientFollowups } from './pages/patient/PatientFollowups';
import { PatientMessages } from './pages/patient/PatientMessages';
import { PatientNotifications } from './pages/patient/PatientNotifications';
import { VideoConsultation } from './pages/patient/VideoConsultation';
import { SymptomChecker } from './pages/patient/SymptomChecker';
import { MyVitals } from './pages/patient/MyVitals';
import { LabReportUpload } from './pages/patient/LabReportUpload';
import { AIAssistant } from './pages/patient/AIAssistant';
import { DoctorDashboard } from './pages/doctor/DoctorDashboard';
import { DoctorPatients } from './pages/doctor/DoctorPatients';
import { DoctorAppointments } from './pages/doctor/DoctorAppointments';
import { DoctorReferrals } from './pages/doctor/DoctorReferrals';
import { DoctorFollowups } from './pages/doctor/DoctorFollowups';
import { DoctorMessages } from './pages/doctor/DoctorMessages';
import { DoctorNotifications } from './pages/doctor/DoctorNotifications';
import { WorkerDashboard } from './pages/worker/WorkerDashboard';
import { WorkerPatients } from './pages/worker/WorkerPatients';
import { WorkerFacilities } from './pages/worker/WorkerFacilities';
import { WorkerReferrals } from './pages/worker/WorkerReferrals';
import { WorkerFollowups } from './pages/worker/WorkerFollowups';
import { SettingsPage } from './pages/SettingsPage';
import { GenericPage } from './pages/GenericPage';
import { FacilityReferrals } from './pages/facility/FacilityReferrals';
import { FacilityInventory } from './pages/facility/FacilityInventory';
import { FacilityPatients } from './pages/facility/FacilityPatients';
import { FacilityMessages } from './pages/facility/FacilityMessages';
import { LanguageProvider, useLanguage } from './context/providers';
import { UserProfileProvider } from './context/providers';
import { NotificationProvider } from './context/providers';
import { ReferralProvider } from './context/providers';
import { ThemeProvider } from './context/providers';

/* Code-split the heavy analytics screens: they drag in recharts (~370 KB),
   which first paint and every route change would otherwise pay for. */
const PatientAnalytics = lazy(() => import('./pages/patient/PatientAnalytics').then((m) => ({ default: m.PatientAnalytics })));
const FacilityDashboard = lazy(() => import('./pages/facility/FacilityDashboard').then((m) => ({ default: m.FacilityDashboard })));
const FacilityAnalytics = lazy(() => import('./pages/facility/FacilityAnalytics').then((m) => ({ default: m.FacilityAnalytics })));

const pathFromLocation = (): string => {
  let p = window.location.pathname || '/';
  if (p.length > 1 && p.endsWith('/')) p = p.slice(0, -1);
  if (!p.startsWith('/')) p = `/${p}`;
  return p || '/';
};

const roleFromPath = (p: string): 'patient' | 'doctor' | 'worker' | 'facility' => {
  if (p.startsWith('/doctor')) return 'doctor';
  if (p.startsWith('/worker')) return 'worker';
  if (p.startsWith('/facility')) return 'facility';
  return 'patient';
};

function AppInner() {
  const { t } = useLanguage();
  const [route, setRoute] = useState(pathFromLocation);
  /* Role is session state, NOT derived from the URL: '/settings' (and any
     other role-neutral route) must keep the role the user logged in with.
     Deriving it from the path made '/settings' fall through to 'patient',
     swapping a doctor's whole shell for the patient one. */
  const [role, setRole] = useState<'patient' | 'doctor' | 'worker' | 'facility'>(() => roleFromPath(pathFromLocation()));

  const navigate = useCallback((newRoute: string) => {
    if (newRoute.startsWith('/doctor')) setRole('doctor');
    else if (newRoute.startsWith('/worker')) setRole('worker');
    else if (newRoute.startsWith('/facility')) setRole('facility');
    else if (newRoute.startsWith('/patient')) setRole('patient');
    const normalized = newRoute.length > 1 && newRoute.endsWith('/') ? newRoute.slice(0, -1) : newRoute;
    if (window.location.pathname !== normalized) {
      window.history.pushState({}, '', normalized);
    }
    setRoute(normalized || '/');
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    const onPopState = () => {
      const p = pathFromLocation();
      setRoute(p);
      if (p.startsWith('/doctor') || p.startsWith('/worker') || p.startsWith('/facility') || p.startsWith('/patient')) {
        setRole(roleFromPath(p));
      }
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const pageTitles: Record<string, { title: string; subtitle: string }> = {
    '/patient/dashboard': { title: 'Overview', subtitle: 'Your healthcare dashboard' },
    '/patient/appointments': { title: 'Appointments', subtitle: 'Manage consultations' },
    '/patient/records': { title: 'Health Records', subtitle: 'Your medical records' },
    '/patient/referrals': { title: 'Referrals', subtitle: 'Referral tracking' },
    '/patient/facilities': { title: 'Facilities', subtitle: 'Find healthcare facilities' },
    '/patient/diagnostics': { title: 'Diagnostics', subtitle: 'Diagnostic services' },
    '/patient/medicines': { title: 'Medicines', subtitle: 'Medicine availability' },
    '/patient/followups': { title: 'Follow-ups', subtitle: 'Follow-up care' },
    '/patient/messages': { title: 'Messages', subtitle: 'Healthcare communication' },
    '/patient/notifications': { title: 'Notifications', subtitle: 'Updates & alerts' },
    '/patient/analytics': { title: 'Analytics', subtitle: 'Healthcare insights' },
    '/patient/consultation': { title: 'Video Consultation', subtitle: 'Teleconsultation' },
    '/patient/symptom-checker': { title: t('sc.shell.title'), subtitle: t('sc.shell.subtitle') },
    '/patient/vitals': { title: 'My Vitals', subtitle: 'Track your health measurements' },
    '/patient/lab-reports': { title: 'Lab Report Upload', subtitle: 'Upload & manage lab reports' },
    '/patient/ai-assistant': { title: 'AI Assistant', subtitle: 'Voice & text health guidance' },
    '/doctor/dashboard': { title: 'Overview', subtitle: 'Clinical dashboard' },
    '/doctor/patients': { title: 'My Patients', subtitle: 'Patient management' },
    '/doctor/consultation': { title: 'Consultations', subtitle: 'Video consultations' },
    '/doctor/appointments': { title: 'Appointments', subtitle: 'Schedule management' },
    '/doctor/referrals': { title: 'Referrals', subtitle: 'Referral management' },
    '/doctor/followups': { title: 'Follow-ups', subtitle: 'Patient follow-ups' },
    '/doctor/messages': { title: 'Messages', subtitle: 'Communication' },
    '/doctor/notifications': { title: 'Notifications', subtitle: 'Updates' },
    '/worker/dashboard': { title: 'Overview', subtitle: 'Field worker dashboard' },
    '/worker/patients': { title: 'My Patients', subtitle: 'Patient registration' },
    '/worker/referrals': { title: 'Referrals', subtitle: 'Create & track referrals' },
    '/worker/followups': { title: 'Follow-ups', subtitle: 'Community follow-ups' },
    '/worker/facilities': { title: 'Facilities', subtitle: 'Find facilities' },
    '/worker/messages': { title: 'Messages', subtitle: 'Communication' },
    '/facility/dashboard': { title: 'Overview', subtitle: 'Facility operations' },
    '/facility/analytics': { title: 'Analytics', subtitle: 'Facility analytics' },
    '/facility/referrals': { title: 'Referrals', subtitle: 'Inbound referrals' },
    '/facility/inventory': { title: 'Inventory', subtitle: 'Medicine & supply inventory' },
    '/facility/patients': { title: 'Patients', subtitle: 'Patient management' },
    '/facility/messages': { title: 'Messages', subtitle: 'Communication' },
    '/settings': { title: 'Settings', subtitle: 'Account preferences' },
  };

  /* Route resolution is unchanged — it is wrapped in a function only so the
     single return below can hand the result to PageTransition. */
  const resolve = (): ReactNode => {

  // Public routes
  if (route === '/') return (
    <ToastProvider>
      <LandingPage onNavigate={navigate} />
    </ToastProvider>
  );

  if (route === '/login') return (
    <ToastProvider>
      <LoginPage onNavigate={navigate} />
    </ToastProvider>
  );

  // Registration
  if (route === '/signup') return (
    <ToastProvider>
      <SignUpPage onNavigate={navigate} />
    </ToastProvider>
  );

  // Settings
  if (route === '/settings') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role={role} title="Settings" subtitle="Account preferences">
        <SettingsPage />
      </AppShell>
    </ToastProvider>
  );

  // Video consultation
  if (route === '/patient/consultation') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="patient" title="Video Consultation" subtitle="Teleconsultation">
        <VideoConsultation />
      </AppShell>
    </ToastProvider>
  );

  // Symptom Checker
  if (route === '/patient/symptom-checker') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="patient" title={t('sc.shell.title')} subtitle={t('sc.shell.subtitle')}>
        <SymptomChecker onNavigate={navigate} />
      </AppShell>
    </ToastProvider>
  );

  // My Vitals
  if (route === '/patient/vitals') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="patient" title="My Vitals" subtitle="Track your health measurements">
        <MyVitals />
      </AppShell>
    </ToastProvider>
  );

  // Lab Report Upload
  if (route === '/patient/lab-reports') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="patient" title="Lab Report Upload" subtitle="Upload & manage lab reports">
        <LabReportUpload />
      </AppShell>
    </ToastProvider>
  );

  // AI Assistant
  if (route === '/patient/ai-assistant') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="patient" title="AI Assistant" subtitle="Voice & text health guidance">
        <AIAssistant />
      </AppShell>
    </ToastProvider>
  );

  // Patient routes
  const patientPages: Record<string, () => ReactNode> = {
    '/patient/dashboard': () => <PatientDashboard onNavigate={navigate} />,
    '/patient/appointments': () => <PatientAppointments onNavigate={navigate} />,
    '/patient/records': () => <PatientRecords />,
    '/patient/referrals': () => <PatientReferrals />,
    '/patient/facilities': () => <PatientFacilities />,
    '/patient/diagnostics': () => <PatientDiagnostics />,
    '/patient/medicines': () => <PatientMedicines />,
    '/patient/followups': () => <PatientFollowups />,
    '/patient/messages': () => <PatientMessages />,
    '/patient/notifications': () => <PatientNotifications />,
    '/patient/analytics': () => <Suspense fallback={null}><PatientAnalytics /></Suspense>,
  };

  if (patientPages[route]) {
    const info = pageTitles[route] || { title: '', subtitle: '' };
    return (
      <ToastProvider>
        <AppShell activeRoute={route} onNavigate={navigate} role="patient" title={info.title} subtitle={info.subtitle}>
          {patientPages[route]()}
        </AppShell>
      </ToastProvider>
    );
  }

  // Doctor routes
  if (route === '/doctor/dashboard') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="doctor" title="Overview" subtitle="Clinical dashboard">
        <DoctorDashboard onNavigate={navigate} />
      </AppShell>
    </ToastProvider>
  );

  if (route === '/doctor/consultation') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="doctor" title="Consultations" subtitle="Video consultations">
        <VideoConsultation />
      </AppShell>
    </ToastProvider>
  );

  const doctorPages: Record<string, { component: ReactNode; title: string; subtitle: string }> = {
    '/doctor/patients': { component: <DoctorPatients onNavigate={navigate} />, title: 'My Patients', subtitle: 'Patient management' },
    '/doctor/appointments': { component: <DoctorAppointments onNavigate={navigate} />, title: 'Appointments', subtitle: 'Schedule management' },
    '/doctor/referrals': { component: <DoctorReferrals />, title: 'Referrals', subtitle: 'Referral management' },
    '/doctor/followups': { component: <DoctorFollowups />, title: 'Follow-ups', subtitle: 'Patient follow-ups' },
    '/doctor/messages': { component: <DoctorMessages />, title: 'Messages', subtitle: 'Communication' },
    '/doctor/notifications': { component: <DoctorNotifications />, title: 'Notifications', subtitle: 'Updates' },
  };

  if (doctorPages[route]) {
    const info = doctorPages[route];
    return (
      <ToastProvider>
        <AppShell activeRoute={route} onNavigate={navigate} role="doctor" title={info.title} subtitle={info.subtitle}>
          {info.component}
        </AppShell>
      </ToastProvider>
    );
  }

  // Worker routes
  if (route === '/worker/dashboard') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="worker" title="Overview" subtitle="Field worker dashboard">
        <WorkerDashboard onNavigate={navigate} />
      </AppShell>
    </ToastProvider>
  );

  const workerPages: Record<string, { component: ReactNode; title: string; subtitle: string }> = {
    '/worker/patients': { component: <WorkerPatients />, title: 'My Patients', subtitle: 'Patient registration' },
    '/worker/referrals': { component: <WorkerReferrals />, title: 'Referrals', subtitle: 'Create & track referrals' },
    '/worker/followups': { component: <WorkerFollowups />, title: 'Follow-ups', subtitle: 'Community follow-ups' },
    '/worker/facilities': { component: <WorkerFacilities />, title: 'Facilities', subtitle: 'Find facilities' },
    '/worker/messages': { component: <GenericPage title="Messages" description="Communicate with supervisors and doctors." onBack={() => navigate('/worker/dashboard')} role="worker" />, title: 'Messages', subtitle: 'Communication' },
  };

  if (workerPages[route]) {
    const info = workerPages[route];
    return (
      <ToastProvider>
        <AppShell activeRoute={route} onNavigate={navigate} role="worker" title={info.title} subtitle={info.subtitle}>
          {info.component}
        </AppShell>
      </ToastProvider>
    );
  }

  // Facility routes
  if (route === '/facility/dashboard') return (
    <ToastProvider>
      <AppShell activeRoute={route} onNavigate={navigate} role="facility" title="Overview" subtitle="Facility operations">
        <Suspense fallback={null}>
          <FacilityDashboard onNavigate={navigate} />
        </Suspense>
      </AppShell>
    </ToastProvider>
  );

  const facilityPages: Record<string, { component: ReactNode; title: string; desc: string }> = {
    '/facility/analytics': { component: <Suspense fallback={null}><FacilityAnalytics /></Suspense>, title: 'Analytics', desc: 'Facility performance and operational metrics.' },
    '/facility/referrals': { component: <FacilityReferrals />, title: 'Referrals', desc: 'Manage inbound and outbound referrals.' },
    '/facility/inventory': { component: <FacilityInventory />, title: 'Inventory', desc: 'Medicine and supply inventory management.' },
    '/facility/patients': { component: <FacilityPatients />, title: 'Patients', desc: 'Patient management and records.' },
    '/facility/messages': { component: <FacilityMessages />, title: 'Messages', desc: 'Communication hub.' },
  };

  if (facilityPages[route]) {
    const info = facilityPages[route];
    return (
      <ToastProvider>
        <AppShell activeRoute={route} onNavigate={navigate} role="facility" title={info.title} subtitle={info.desc}>
          {info.component}
        </AppShell>
      </ToastProvider>
    );
  }

  // Fallback
  return (
    <ToastProvider>
      <LandingPage onNavigate={navigate} />
    </ToastProvider>
  );

  };

  /* No transition wrapper here: every dashboard branch above returns
     ToastProvider > AppShell at the same tree position, so React updates the
     shell in place instead of remounting it. That keeps the sidebar's scroll
     position and collapse state, and the page background never unmounts — so
     there is no white flash between screens. The content crossfade itself is
     handled by PageTransition inside AppShell. The profile provider sits here
     (not in App) because it needs the active role to pick which identity to
     expose. */
  return (
    <UserProfileProvider role={role}>
      <NotificationProvider role={role}>
        <ReferralProvider>{resolve()}</ReferralProvider>
      </NotificationProvider>
    </UserProfileProvider>
  );
}

function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AppInner />
      </LanguageProvider>
    </ThemeProvider>
  );
}

export default App;
