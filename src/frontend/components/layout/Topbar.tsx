import { useState, useRef, useEffect, useMemo } from 'react';
import { motion, AnimatePresence, useScroll, useSpring } from 'framer-motion';
import { Search, Bell, Menu, X, Phone, Command } from 'lucide-react';
import { Avatar } from '../ui/Avatar';
import { LanguageSelector } from '../ui/LanguageSelector';
import { ThemeToggle } from '../ui/ThemeToggle';
import { useUserProfile } from '../../context/providers';
import { useNotifications } from '../../context/providers';

interface TopbarProps {
  sidebarCollapsed: boolean;
  onMenuToggle: () => void;
  title?: string;
  subtitle?: string;
  role?: 'patient' | 'doctor' | 'worker' | 'facility';
}

const roleChips: Record<string, { label: string; ink: string; bg: string; ring: string }> = {
  patient:  { label: 'Patient',  ink: '#0A5F38', bg: 'rgba(23,179,102,0.12)',  ring: 'rgba(23,179,102,0.26)' },
  doctor:   { label: 'Doctor',   ink: '#076A82', bg: 'rgba(14,165,201,0.12)',  ring: 'rgba(14,165,201,0.26)' },
  worker:   { label: 'Worker',   ink: '#5533DB', bg: 'rgba(124,92,255,0.12)',  ring: 'rgba(124,92,255,0.26)' },
  facility: { label: 'Facility', ink: '#92610A', bg: 'rgba(245,158,11,0.13)',  ring: 'rgba(245,158,11,0.28)' },
};

const searchIndex = [
  { category: 'Patients', results: ['Rahul Sharma', 'Ananya Das', 'Priya Devi'] },
  { category: 'Doctors', results: ['Dr. Ananya Sharma', 'Dr. Arjun Das', 'Dr. Priya Singh'] },
  { category: 'Facilities', results: ['PHC Chandrapur', 'CHC Sonapur', 'District Hospital Guwahati'] },
];

export function Topbar({ onMenuToggle, title, subtitle, role = 'patient' }: TopbarProps) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [notifOpen, setNotifOpen] = useState(false);
  const [now, setNow] = useState(() => new Date());
  const notifRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const { items: notifItems, unreadCount, markRead, markAllRead } = useNotifications();
  const { shortName, initials } = useUserProfile();
  const chip = roleChips[role] ?? roleChips.patient;

  // Reading-progress hairline on the header's lower edge. Spring-smoothed so it
  // glides instead of stepping with each scroll event.
  const { scrollYProgress } = useScroll();
  const progress = useSpring(scrollYProgress, { stiffness: 140, damping: 30, mass: 0.3 });

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // ⌘K / Ctrl+K jumps to search; Escape dismisses whichever panel is open.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        searchRef.current?.focus();
        setSearchOpen(true);
      }
      if (e.key === 'Escape') {
        setNotifOpen(false);
        setSearchOpen(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  // A clinical shell should say what time it is — shifts and slots depend on it.
  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 30_000);
    return () => window.clearInterval(id);
  }, []);

  /* The old dropdown listed every seeded name regardless of what was typed.
     Filter for real, and say so when nothing matches. */
  const matches = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return [];
    return searchIndex
      .map(cat => ({ ...cat, results: cat.results.filter(r => r.toLowerCase().includes(q)) }))
      .filter(cat => cat.results.length > 0);
  }, [searchQuery]);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-2 border-b border-sahaay-deep/[0.07] bg-sahaay-surface/80 px-3 backdrop-blur-xl sm:gap-3 lg:gap-4 lg:px-6">
      {/* Mobile menu */}
      <button
        onClick={onMenuToggle}
        aria-label="Open navigation"
        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-ink-500 transition-colors hover:bg-white/70 hover:text-ink-800 lg:hidden"
      >
        <Menu size={20} />
      </button>

      {/* Title + role chip */}
      {/* Deliberately not an <h1>: this is shell chrome that repeats the page
          title, and each page already owns the document's real heading. */}
      <div className="hidden min-w-0 sm:block">
        <div className="flex items-center gap-2">
          <p className="truncate font-display text-base font-bold text-ink-900">
            {title || 'SAHAAY'}
          </p>
          <span
            className="hidden shrink-0 rounded-full px-2 py-0.5 font-mono text-[9.5px] font-bold uppercase tracking-[0.14em] lg:inline"
            style={{ color: chip.ink, background: chip.bg, boxShadow: `inset 0 0 0 1px ${chip.ring}` }}
          >
            {chip.label}
          </span>
        </div>
        <p className="truncate text-[11px] text-ink-400">
          {subtitle || 'Connecting Care. Continuing Hope.'}
        </p>
      </div>

      <div className="flex-1" />

      {/* Live clock */}
      <div className="hidden shrink-0 text-right xl:block">
        <p className="font-mono text-sm font-semibold leading-none text-ink-700 tabular-nums">
          {now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
        <p className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.12em] text-ink-300">
          {now.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' })}
        </p>
      </div>

      {/* Search */}
      <div
        className="relative hidden shrink-0 transition-[width] duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] md:block"
        style={{ width: searchOpen ? 340 : 210 }}
      >
        <div
          className={`flex items-center gap-2 rounded-xl border bg-white/65 px-3 py-2 transition-all duration-200 ${
            searchOpen ? 'border-sahaay-500/40 shadow-sm' : 'border-transparent'
          }`}
          style={searchOpen ? { boxShadow: '0 0 0 4px rgba(23,179,102,0.10)' } : undefined}
        >
          <Search size={16} className="shrink-0 text-ink-300" />
          <input
            ref={searchRef}
            type="text"
            aria-label="Search patients, doctors and facilities"
            placeholder="Search patients, doctors..."
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setSearchOpen(true); }}
            onFocus={() => setSearchOpen(true)}
            className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-ink-300"
          />
          {searchQuery ? (
            <button
              onClick={() => { setSearchQuery(''); setSearchOpen(false); }}
              aria-label="Clear search"
              className="shrink-0 text-ink-300 transition-colors hover:text-ink-600"
            >
              <X size={14} />
            </button>
          ) : (
            <span
              aria-hidden="true"
              className="hidden shrink-0 items-center gap-0.5 rounded-md bg-ink-200/50 px-1.5 py-0.5 font-mono text-[10px] font-bold text-ink-400 lg:flex"
            >
              <Command size={9} /> K
            </span>
          )}
        </div>

        <AnimatePresence>
          {searchOpen && searchQuery && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
              className="glass-card-elevated absolute left-0 right-0 top-full mt-2 max-h-80 overflow-y-auto p-3"
            >
              {matches.length === 0 ? (
                <p className="px-2 py-3 text-sm text-ink-400">
                  No matches for “{searchQuery.trim()}”
                </p>
              ) : (
                matches.map(cat => (
                  <div key={cat.category} className="mb-3 last:mb-0">
                    <p className="mb-1 px-2 font-mono text-[9.5px] font-bold uppercase tracking-[0.16em] text-ink-300">
                      {cat.category}
                    </p>
                    {cat.results.map(r => (
                      <button
                        key={r}
                        className="w-full rounded-lg px-3 py-2 text-left text-sm text-ink-700 transition-colors hover:bg-sahaay-500/10"
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                ))
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Mobile search */}
      <button
        aria-label="Search"
        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-ink-500 transition-colors hover:bg-white/70 md:hidden"
      >
        <Search size={18} />
      </button>

      <div className="shrink-0">
        <LanguageSelector />
      </div>

      {/* Theme switch — always one click away, mirrors Settings → Display */}
      <ThemeToggle />

      {/* Emergency */}
      <button
        aria-label="Emergency helpline"
        className="relative hidden shrink-0 items-center gap-1.5 overflow-hidden rounded-xl px-3 py-2.5 text-xs font-bold text-vital-pulse-ink transition-transform hover:-translate-y-0.5 active:translate-y-0 sm:flex"
        style={{ background: 'rgba(255,77,109,0.10)', boxShadow: 'inset 0 0 0 1px rgba(255,77,109,0.26)' }}
      >
        <span
          aria-hidden="true"
          className="animate-pulse-soft absolute inset-0"
          style={{ background: 'radial-gradient(60% 100% at 0% 50%, rgba(255,77,109,0.20), transparent)' }}
        />
        <Phone size={14} className="relative" />
        <span className="relative hidden lg:inline">Emergency</span>
      </button>

      {/* Notifications */}
      <div ref={notifRef} className="relative shrink-0">
        <button
          onClick={() => setNotifOpen(!notifOpen)}
          aria-label={unreadCount > 0 ? `Notifications, ${unreadCount} unread` : 'Notifications'}
          aria-expanded={notifOpen}
          className="relative flex h-11 w-11 items-center justify-center rounded-xl text-ink-500 transition-colors hover:bg-white/70 hover:text-ink-800"
        >
          <Bell size={18} />
          {unreadCount > 0 && (
            <span
              className="animate-pulse-soft absolute right-2 top-2 flex h-4 w-4 items-center justify-center rounded-full bg-vital-pulse text-[9px] font-bold text-white"
              style={{ boxShadow: '0 0 0 2px rgba(242,251,245,0.9), 0 0 10px rgba(255,77,109,0.6)' }}
            >
              {unreadCount}
            </span>
          )}
        </button>

        <AnimatePresence>
          {notifOpen && (
            <motion.div
              initial={{ opacity: 0, y: -8, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.98 }}
              transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="glass-card-elevated absolute right-0 top-full mt-2 w-[min(20rem,calc(100vw-1.5rem))] overflow-hidden"
            >
              <div className="flex items-center justify-between border-b border-ink-200/60 px-4 py-3">
                <h3 className="font-display text-sm font-bold text-ink-900">Notifications</h3>
                {unreadCount > 0 ? (
                  <button
                    onClick={markAllRead}
                    className="rounded-lg px-2 py-1 text-xs font-semibold text-sahaay-deep transition-colors hover:bg-sahaay-500/10"
                  >
                    Mark all read
                  </button>
                ) : (
                  <span className="font-mono text-[10px] uppercase tracking-wider text-ink-400">All read</span>
                )}
              </div>
              <div className="max-h-72 overflow-y-auto">
                {notifItems.map((n, i) => (
                  <motion.div
                    key={n.id}
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.03 * i, duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
                    onClick={() => markRead(n.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); markRead(n.id); } }}
                    className={`cursor-pointer border-b border-ink-200/40 px-4 py-3 transition-colors last:border-0 hover:bg-sahaay-500/[0.07] ${
                      !n.read ? 'bg-sahaay-50/60' : ''
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {!n.read && (
                        <span aria-hidden="true" className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-sahaay-500" />
                      )}
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-ink-800">{n.title}</p>
                        <p className="mt-0.5 line-clamp-2 text-xs text-ink-500">{n.message}</p>
                        <p className="mt-1 font-mono text-[10px] text-ink-300">{n.time}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Profile */}
      <button
        aria-label={`Account: ${shortName}`}
        className="flex shrink-0 items-center gap-2 rounded-xl py-1.5 pl-2 pr-2 transition-colors hover:bg-white/70 lg:pr-3"
      >
        <Avatar initials={initials} size="sm" />
        <span className="hidden text-sm font-medium text-ink-700 lg:inline">{shortName}</span>
      </button>

      {/* Reading progress */}
      <motion.div
        aria-hidden="true"
        className="holo-line absolute inset-x-0 bottom-0 h-[2px] origin-left"
        style={{ scaleX: progress }}
      />
    </header>
  );
}
