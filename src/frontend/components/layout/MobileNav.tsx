import type { ComponentType } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Home, Calendar, FileText, ClipboardList, User, Settings, Phone } from 'lucide-react';

interface MobileNavProps {
  activeRoute: string;
  onNavigate: (route: string) => void;
  role: 'patient' | 'doctor' | 'worker' | 'facility';
}

type NavItem = {
  label: string;
  icon: ComponentType<{ size?: number | string; className?: string }>;
  route: string;
};

/* The fifth slot used to point at `/<role>/profile`, which no route resolves —
   tapping it silently dropped the user back on the landing page. It now goes to
   the real settings screen. Five items, the bottom-nav ceiling. */
const navItems: Record<string, NavItem[]> = {
  patient: [
    { label: 'Home', icon: Home, route: '/patient/dashboard' },
    { label: 'Records', icon: FileText, route: '/patient/records' },
    { label: 'Referrals', icon: ClipboardList, route: '/patient/referrals' },
    { label: 'Calendar', icon: Calendar, route: '/patient/appointments' },
    { label: 'Settings', icon: Settings, route: '/settings' },
  ],
  doctor: [
    { label: 'Home', icon: Home, route: '/doctor/dashboard' },
    { label: 'Patients', icon: User, route: '/doctor/patients' },
    { label: 'Consult', icon: Calendar, route: '/doctor/consultation' },
    { label: 'Referrals', icon: ClipboardList, route: '/doctor/referrals' },
    { label: 'Settings', icon: Settings, route: '/settings' },
  ],
  worker: [
    { label: 'Home', icon: Home, route: '/worker/dashboard' },
    { label: 'Patients', icon: User, route: '/worker/patients' },
    { label: 'Referrals', icon: ClipboardList, route: '/worker/referrals' },
    { label: 'Follow-ups', icon: Calendar, route: '/worker/followups' },
    { label: 'Settings', icon: Settings, route: '/settings' },
  ],
  facility: [
    { label: 'Home', icon: Home, route: '/facility/dashboard' },
    { label: 'Analytics', icon: FileText, route: '/facility/analytics' },
    { label: 'Referrals', icon: ClipboardList, route: '/facility/referrals' },
    { label: 'Inventory', icon: Calendar, route: '/facility/inventory' },
    { label: 'Settings', icon: Settings, route: '/settings' },
  ],
};

export function MobileNav({ activeRoute, onNavigate, role }: MobileNavProps) {
  const items = navItems[role] || navItems.patient;
  const reduce = useReducedMotion();

  return (
    <>
      {/* Emergency FAB */}
      <button
        aria-label="Emergency helpline"
        className="fixed bottom-[calc(5.5rem+env(safe-area-inset-bottom))] right-4 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-vital-pulse text-white transition-transform active:scale-95 lg:hidden"
        style={{ boxShadow: '0 8px 24px rgba(255,77,109,0.42), inset 0 1px 0 rgba(255,255,255,0.28)' }}
      >
        {!reduce && (
          <span
            aria-hidden="true"
            className="animate-halo absolute inset-0 rounded-full"
            style={{ background: 'rgba(255,77,109,0.4)' }}
          />
        )}
        <Phone size={20} className="relative" />
      </button>

      {/* Bottom nav */}
      <nav
        aria-label="Primary"
        className="fixed inset-x-0 bottom-0 z-50 border-t border-sahaay-deep/[0.08] bg-white/90 px-1 pb-[env(safe-area-inset-bottom)] backdrop-blur-xl lg:hidden"
      >
        {/* Iridescent hairline along the top edge */}
        <span aria-hidden="true" className="holo-line absolute inset-x-0 top-0 h-[1.5px]" />

        <div className="flex h-16 items-stretch justify-around">
          {items.map(item => {
            const Icon = item.icon;
            const isActive = activeRoute === item.route;
            return (
              <button
                key={item.route}
                onClick={() => onNavigate(item.route)}
                aria-current={isActive ? 'page' : undefined}
                className={`relative flex min-w-[56px] flex-1 flex-col items-center justify-center gap-0.5 rounded-xl transition-colors ${
                  isActive ? 'text-sahaay-deep' : 'text-ink-300'
                }`}
              >
                <span className="relative flex h-8 w-11 items-center justify-center">
                  {isActive && (
                    <motion.span
                      aria-hidden="true"
                      layoutId="mobilenav-active"
                      transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                      className="absolute inset-0 rounded-lg bg-sahaay-500/15"
                      style={{ boxShadow: 'inset 0 0 0 1px rgba(23,179,102,0.24)' }}
                    />
                  )}
                  <Icon size={20} className="relative" />
                </span>
                <span className="max-w-full truncate px-0.5 text-[10px] font-semibold">
                  {item.label}
                </span>
              </button>
            );
          })}
        </div>
      </nav>
    </>
  );
}
