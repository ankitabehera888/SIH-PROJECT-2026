import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/providers';

/**
 * Global light/dark switch. Rendered in the Topbar (logged-in shell) and on
 * the landing + login pages, so the theme is changeable at any point in the
 * journey. Mirrors the toggle in Settings → Display Preferences.
 */
export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const label = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';

  return (
    <button
      onClick={toggleTheme}
      aria-label={label}
      title={label}
      className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-ink-500 transition-colors hover:bg-white/70 hover:text-ink-800"
    >
      <motion.span
        key={theme}
        initial={{ rotate: -60, opacity: 0 }}
        animate={{ rotate: 0, opacity: 1 }}
        transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
        className="flex"
      >
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </motion.span>
    </button>
  );
}
