import { useState, type ComponentType } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import {
  LayoutDashboard, Users, Calendar, MessageSquare, FileText, Stethoscope,
  Pill, Activity, Building2, Bell, BarChart3, Settings, Heart,
  ChevronLeft, ChevronRight, LogOut, HelpCircle, ClipboardList,
  Video, Mic, Upload, X
} from 'lucide-react';
import { useLanguage } from '../../context/providers';
import { useUserProfile } from '../../context/providers';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  activeRoute: string;
  onNavigate: (route: string) => void;
  role: 'patient' | 'doctor' | 'worker' | 'facility';
  /**
   * 'rail' is the fixed desktop column (hidden below lg).
   * 'drawer' is the mobile slide-over, which must render at every width —
   * the previous single variant was `hidden lg:flex`, so the mobile menu
   * button opened an empty overlay.
   */
  variant?: 'rail' | 'drawer';
}

type MenuItem = {
  label: string;
  icon: ComponentType<{ size?: number | string; className?: string }>;
  route: string;
  /** i18n key for the group header this item sits under. */
  group?: string;
};

/* Routes and labels are unchanged. `group` only adds headers: a flat list of
   sixteen patient links is an overloaded nav, and grouping is the cheapest fix
   that costs no destinations. */
const roleMenus: Record<string, MenuItem[]> = {
  patient: [
    { label: 'Overview', icon: LayoutDashboard, route: '/patient/dashboard' },
    { label: 'Symptom Checker', icon: Stethoscope, route: '/patient/symptom-checker', group: 'nav.group.assess' },
    { label: 'AI Assistant', icon: Mic, route: '/patient/ai-assistant', group: 'nav.group.assess' },
    { label: 'My Vitals', icon: Activity, route: '/patient/vitals', group: 'nav.group.assess' },
    { label: 'Lab Reports', icon: Upload, route: '/patient/lab-reports', group: 'nav.group.assess' },
    { label: 'Appointments', icon: Calendar, route: '/patient/appointments', group: 'nav.group.carePlan' },
    { label: 'Referrals', icon: ClipboardList, route: '/patient/referrals', group: 'nav.group.carePlan' },
    { label: 'Follow-ups', icon: ClipboardList, route: '/patient/followups', group: 'nav.group.carePlan' },
    { label: 'Facilities', icon: Building2, route: '/patient/facilities', group: 'nav.group.locate' },
    { label: 'Diagnostics', icon: Activity, route: '/patient/diagnostics', group: 'nav.group.locate' },
    { label: 'Medicines', icon: Pill, route: '/patient/medicines', group: 'nav.group.locate' },
    { label: 'Health Records', icon: FileText, route: '/patient/records', group: 'nav.group.records' },
    { label: 'Analytics', icon: BarChart3, route: '/patient/analytics', group: 'nav.group.records' },
    { label: 'Messages', icon: MessageSquare, route: '/patient/messages', group: 'nav.group.account' },
    { label: 'Notifications', icon: Bell, route: '/patient/notifications', group: 'nav.group.account' },
    { label: 'Settings', icon: Settings, route: '/settings', group: 'nav.group.account' },
  ],
  doctor: [
    { label: 'Overview', icon: LayoutDashboard, route: '/doctor/dashboard' },
    { label: 'My Patients', icon: Users, route: '/doctor/patients', group: 'nav.group.clinical' },
    { label: 'Consultations', icon: Video, route: '/doctor/consultation', group: 'nav.group.clinical' },
    { label: 'Appointments', icon: Calendar, route: '/doctor/appointments', group: 'nav.group.clinical' },
    { label: 'Referrals', icon: ClipboardList, route: '/doctor/referrals', group: 'nav.group.coordination' },
    { label: 'Follow-ups', icon: Stethoscope, route: '/doctor/followups', group: 'nav.group.coordination' },
    { label: 'Messages', icon: MessageSquare, route: '/doctor/messages', group: 'nav.group.account' },
    { label: 'Notifications', icon: Bell, route: '/doctor/notifications', group: 'nav.group.account' },
    { label: 'Settings', icon: Settings, route: '/settings', group: 'nav.group.account' },
  ],
  worker: [
    { label: 'Overview', icon: LayoutDashboard, route: '/worker/dashboard' },
    { label: 'My Patients', icon: Users, route: '/worker/patients', group: 'nav.group.field' },
    { label: 'Referrals', icon: ClipboardList, route: '/worker/referrals', group: 'nav.group.field' },
    { label: 'Follow-ups', icon: Stethoscope, route: '/worker/followups', group: 'nav.group.field' },
    { label: 'Facilities', icon: Building2, route: '/worker/facilities', group: 'nav.group.field' },
    { label: 'Messages', icon: MessageSquare, route: '/worker/messages', group: 'nav.group.account' },
    { label: 'Settings', icon: Settings, route: '/settings', group: 'nav.group.account' },
  ],
  facility: [
    { label: 'Overview', icon: LayoutDashboard, route: '/facility/dashboard' },
    { label: 'Analytics', icon: BarChart3, route: '/facility/analytics', group: 'nav.group.operations' },
    { label: 'Referrals', icon: ClipboardList, route: '/facility/referrals', group: 'nav.group.operations' },
    { label: 'Inventory', icon: Pill, route: '/facility/inventory', group: 'nav.group.operations' },
    { label: 'Patients', icon: Users, route: '/facility/patients', group: 'nav.group.operations' },
    { label: 'Messages', icon: MessageSquare, route: '/facility/messages', group: 'nav.group.account' },
    { label: 'Settings', icon: Settings, route: '/settings', group: 'nav.group.account' },
  ],
};

const roleNames: Record<string, string> = { patient: 'Patient', doctor: 'Doctor', worker: 'Healthcare Worker', facility: 'Facility Admin' };

const menuLabels: Record<string, string> = {
  'Overview': 'dash.overview',
  'Appointments': 'dash.appointments',
  'Health Records': 'dash.records',
  'Referrals': 'dash.referrals',
  'Facilities': 'dash.facilities',
  'Diagnostics': 'dash.diagnostics',
  'Medicines': 'dash.medicines',
  'Follow-ups': 'dash.followups',
  'Messages': 'dash.messages',
  'Notifications': 'dash.notifications',
  'Analytics': 'dash.analytics',
  'Settings': 'dash.settings',
  'My Patients': 'dash.patients',
  'Consultations': 'dash.consultations',
  'Patients': 'dash.patients',
  'Inventory': 'dash.inventory',
  'Symptom Checker': 'dash.symptomChecker',
  'AI Assistant': 'dash.aiAssistant',
  'My Vitals': 'dash.myVitals',
  'Lab Reports': 'dash.labReports',
};

export function Sidebar({ collapsed, onToggle, activeRoute, onNavigate, role, variant = 'rail' }: SidebarProps) {
  const { t } = useLanguage();
  const { profile, initials: profileInitials } = useUserProfile();
  /* The identity block mirrors the profile saved in Settings for every role
     (the Topbar already does); roleNames stays for the aria label. */
  const identityName = profile.fullName;
  const identityInitials = profileInitials;
  const menuItems = roleMenus[role] || roleMenus.patient;
  const [hovered, setHovered] = useState<string | null>(null);
  const reduce = useReducedMotion();
  const isDrawer = variant === 'drawer';

  // The drawer is always expanded; only the desktop rail collapses.
  const shrunk = collapsed && !isDrawer;

  const label = (item: MenuItem) =>
    menuLabels[item.label] ? t(menuLabels[item.label]) : item.label;

  return (
    <>
    <motion.aside
      initial={false}
      animate={isDrawer ? undefined : { width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.28, ease: [0.4, 0, 0.2, 1] }}
      aria-label={`${roleNames[role]} navigation`}
      className={
        isDrawer
          ? 'sahaay-gradient-deep grain relative flex h-full w-full flex-col overflow-hidden'
          : 'sahaay-gradient-deep grain fixed bottom-0 left-0 top-0 z-40 hidden flex-col overflow-hidden lg:flex'
      }
    >
      {/* Ambient depth: two aurora blobs keep the deep panel from reading
          as a flat block of colour. Purely decorative — deliberately STATIC:
          the sidebar is fixed and always on screen, so animating these meant
          re-rasterizing two large blurred layers every single frame. */}
      <div
        aria-hidden="true"
        className="aurora-blob -left-24 -top-24 h-64 w-64"
        style={{ background: 'radial-gradient(circle, rgba(23,179,102,0.42), transparent 68%)' }}
      />
      <div
        aria-hidden="true"
        className="aurora-blob -bottom-28 -right-20 h-72 w-72"
        style={{ background: 'radial-gradient(circle, rgba(124,92,255,0.30), transparent 70%)' }}
      />

      {/* Iridescent inner edge — the vertical twin of .holo-line */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-y-0 right-0 w-px"
        style={{
          background:
            'linear-gradient(180deg, transparent, rgba(23,179,102,0.55) 18%, rgba(14,165,201,0.65) 48%, rgba(124,92,255,0.5) 76%, transparent)',
        }}
      />

      {/* ── Logo ───────────────────────────────────────────────────────── */}
      <div className="relative z-[2] flex h-16 shrink-0 items-center gap-3 px-4">
        <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white/15">
          {!reduce && (
            <span
              aria-hidden="true"
              className="animate-halo absolute inset-0 rounded-xl"
              style={{ boxShadow: '0 0 0 1px rgba(116,226,165,0.6)' }}
            />
          )}
          <Heart size={18} className="relative text-sahaay-300" fill="currentColor" />
        </div>
        <AnimatePresence initial={false}>
          {!shrunk && (
            <motion.div
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -6 }}
              className="overflow-hidden"
            >
              {/* A wordmark, not a document heading — the page owns the h1. */}
              <span className="block font-display text-lg font-bold tracking-tight text-white">SAHAAY</span>
            </motion.div>
          )}
        </AnimatePresence>

        {isDrawer && (
          <button
            onClick={onToggle}
            aria-label="Close navigation"
            className="ml-auto flex h-11 w-11 items-center justify-center rounded-xl text-white/60 transition-colors hover:bg-white/10 hover:text-white"
          >
            <X size={20} />
          </button>
        )}
      </div>

      {/* ── Role badge ─────────────────────────────────────────────────── */}
      <AnimatePresence initial={false}>
        {!shrunk && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="relative z-[2] mb-3 px-4"
          >
            <span className="font-mono text-[10px] font-bold uppercase tracking-[0.18em] text-sahaay-300/70">
              {roleNames[role]}
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Nav ────────────────────────────────────────────────────────── */}
      <nav className="no-scrollbar relative z-[2] flex-1 space-y-0.5 overflow-y-auto px-3">
        {menuItems.map((item, i) => {
          const isActive = activeRoute === item.route;
          const Icon = item.icon;
          // A header is drawn the first time a group appears in the list.
          const startsGroup = !!item.group && item.group !== menuItems[i - 1]?.group;

          return (
            <div key={item.route}>
              {startsGroup && (
                shrunk ? (
                  <div aria-hidden="true" className="mx-2 my-2 h-px bg-white/10" />
                ) : (
                  <p className="px-3 pb-1 pt-4 font-mono text-[9.5px] font-bold uppercase tracking-[0.2em] text-white/28">
                    {t(item.group!)}
                  </p>
                )
              )}

              <button
                onClick={() => onNavigate(item.route)}
                onMouseEnter={() => setHovered(item.route)}
                onMouseLeave={() => setHovered(null)}
                aria-current={isActive ? 'page' : undefined}
                className={`group relative flex min-h-[44px] w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-200 ${
                  isActive ? 'text-white' : 'text-white/60 hover:bg-white/[0.07] hover:text-white'
                }`}
                title={shrunk ? label(item) : undefined}
              >
                {/* Shared-layout pill: it glides between items instead of
                    popping, which is what makes the rail feel physical. */}
                {isActive && (
                  <motion.span
                    aria-hidden="true"
                    layoutId={`sidebar-active-${variant}`}
                    transition={{ type: 'spring', stiffness: 380, damping: 32 }}
                    className="absolute inset-0 rounded-xl bg-white/[0.14]"
                    style={{ boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.16)' }}
                  />
                )}
                {isActive && (
                  <motion.span
                    aria-hidden="true"
                    layoutId={`sidebar-bar-${variant}`}
                    transition={{ type: 'spring', stiffness: 380, damping: 32 }}
                    className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-sahaay-300"
                    style={{ boxShadow: '0 0 12px rgba(116,226,165,0.8)' }}
                  />
                )}

                <Icon
                  size={20}
                  className={`relative shrink-0 transition-transform duration-300 ${
                    isActive ? 'text-sahaay-300' : 'group-hover:scale-110'
                  }`}
                />

                <AnimatePresence initial={false}>
                  {!shrunk && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="relative whitespace-nowrap"
                    >
                      {label(item)}
                    </motion.span>
                  )}
                </AnimatePresence>

                {/* Collapsed-rail tooltip. `title` above covers keyboard and
                    screen-reader users; this is the visual affordance. */}
                {shrunk && hovered === item.route && (
                  <motion.span
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="pointer-events-none absolute left-full z-50 ml-3 whitespace-nowrap rounded-lg bg-ink-900/95 px-2.5 py-1.5 text-xs font-semibold text-white shadow-lg backdrop-blur"
                  >
                    {label(item)}
                  </motion.span>
                )}
              </button>
            </div>
          );
        })}
      </nav>

      {/* ── Identity + actions ─────────────────────────────────────────── */}
      <div className="relative z-[2] mt-2 space-y-1 border-t border-white/10 px-3 pb-4 pt-3">
        {!shrunk && (
          <div className="mb-2 flex items-center gap-2.5 rounded-xl bg-white/[0.06] px-2.5 py-2">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-sahaay-400 to-sahaay-600 text-[11px] font-bold text-white">
              {identityInitials}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-xs font-semibold text-white/90">{identityName}</span>
              <span className="flex items-center gap-1.5 text-[10px] text-white/45">
                <span className={`h-1.5 w-1.5 rounded-full bg-sahaay-400 ${reduce ? '' : 'animate-pulse-soft'}`} />
                Online
              </span>
            </span>
          </div>
        )}

        <button className="flex min-h-[44px] w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/60 transition-all hover:bg-white/[0.07] hover:text-white">
          <HelpCircle size={20} className="shrink-0" />
          {!shrunk && <span>{t('footer.support')}</span>}
        </button>
        <button
          onClick={() => onNavigate('/login')}
          className="flex min-h-[44px] w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/60 transition-all hover:bg-vital-pulse/15 hover:text-white"
        >
          <LogOut size={20} className="shrink-0" />
          {!shrunk && <span>{t('dash.logout')}</span>}
        </button>
      </div>

      {/* ── Collapse toggle ────────────────────────────────────────────── */}
      {/* Rendered outside the `overflow-hidden` aside as a sibling: nested on
          the panel it was clipped away, so the rail could never be collapsed. */}
    </motion.aside>

    {!isDrawer && (
      <button
        onClick={onToggle}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        aria-expanded={!collapsed}
        style={{ left: collapsed ? 60 : 248 }}
        className="fixed top-[76px] z-50 hidden h-7 w-7 items-center justify-center rounded-full border border-white/25 bg-sahaay-deep text-white/70 shadow-lg transition-[left,background-color,transform] duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] hover:scale-110 hover:bg-sahaay-700 hover:text-white lg:flex"
      >
        {collapsed ? <ChevronRight size={13} /> : <ChevronLeft size={13} />}
      </button>
    )}
    </>
  );
}
