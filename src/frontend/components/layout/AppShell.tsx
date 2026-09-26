import { useEffect, useState, type CSSProperties, type ReactNode } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { MobileNav } from './MobileNav';
import { PageTransition } from '../fx/PageTransition';

interface AppShellProps {
  children: ReactNode;
  activeRoute: string;
  onNavigate: (route: string) => void;
  role: 'patient' | 'doctor' | 'worker' | 'facility';
  title?: string;
  subtitle?: string;
}

export function AppShell({ children, activeRoute, onNavigate, role, title, subtitle }: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const reduce = useReducedMotion();

  // Escape closes the drawer, and the page behind it must not scroll while it
  // is open — otherwise a swipe on the dim backdrop moves the content.
  useEffect(() => {
    if (!mobileOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileOpen(false);
    };
    window.addEventListener('keydown', onKey);
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      window.removeEventListener('keydown', onKey);
      document.body.style.overflow = previous;
    };
  }, [mobileOpen]);

  return (
    /* No transform or filter on this element, ever: it is the ancestor of the
       fixed sidebar, bottom nav and emergency button, and a transformed
       ancestor would become their containing block. */
    <div className="sahaay-page-bg min-h-screen">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed(!collapsed)}
        activeRoute={activeRoute}
        onNavigate={onNavigate}
        role={role}
      />

      {/* ── Mobile drawer ──────────────────────────────────────────────── */}
      <AnimatePresence>
        {mobileOpen && (
          <div className="fixed inset-0 z-[60] lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setMobileOpen(false)}
              className="absolute inset-0 bg-ink-900/50 backdrop-blur-sm"
            />
            <motion.div
              initial={reduce ? { opacity: 0 } : { x: -300 }}
              animate={reduce ? { opacity: 1 } : { x: 0 }}
              exit={reduce ? { opacity: 0 } : { x: -300 }}
              transition={reduce ? { duration: 0.15 } : { type: 'spring', stiffness: 340, damping: 34 }}
              className="absolute bottom-0 left-0 top-0 w-[286px] max-w-[84vw] shadow-2xl"
            >
              <Sidebar
                collapsed={false}
                onToggle={() => setMobileOpen(false)}
                activeRoute={activeRoute}
                onNavigate={(route) => { onNavigate(route); setMobileOpen(false); }}
                role={role}
                variant="drawer"
              />
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ── Content column ─────────────────────────────────────────────── */}
      {/* One render of `children`, not two. The previous shell mounted the page
          separately for the desktop and mobile branches, so every page effect
          ran twice and every element id was duplicated. The rail offset is a
          CSS custom property so the reflow is one transition, not a per-frame
          JS style write. */}
      <div
        className="min-h-screen transition-[padding-left] duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] lg:pl-[var(--shell-rail)]"
        style={{ '--shell-rail': collapsed ? '72px' : '260px' } as CSSProperties}
      >
        <Topbar
          sidebarCollapsed={collapsed}
          onMenuToggle={() => setMobileOpen(true)}
          title={title}
          subtitle={subtitle}
          role={role}
        />
        {/* The route transition lives INSIDE the shell, around the page content
            only. Keying the whole app on the route (the old App.tsx approach)
            unmounted the shell on every navigation: the background flashed
            white and the sidebar scroll jumped back to the top. */}
        <main className="relative z-[1] p-4 pb-24 lg:p-6 lg:pb-10">
          <PageTransition routeKey={activeRoute}>{children}</PageTransition>
        </main>
      </div>

      <MobileNav activeRoute={activeRoute} onNavigate={onNavigate} role={role} />
    </div>
  );
}
