import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, CheckCircle2, Stethoscope, AlertCircle, Clock, Pill, Calendar, CheckCheck } from 'lucide-react';
import { PageBanner } from '../../components/ui/PageBanner';
import { useNotifications } from '../../context/providers';
import { useLanguage } from '../../context/providers';

const typeIcons: Record<string, any> = {
  referral: CheckCircle2, consultation: Stethoscope, followup: Clock, diagnostic: AlertCircle, medicine: Pill, appointment: Calendar,
};

export function PatientNotifications() {
  const { t } = useLanguage();
  const { items, unreadCount, markRead, markAllRead } = useNotifications();
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const visible = filter === 'unread' ? items.filter((n) => !n.read) : items;

  return (
    <div className="space-y-6">
      <PageBanner image="https://images.unsplash.com/photo-1512428559087-560fa5ceab42?auto=format&fit=crop&w=1200&q=80" />
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{t('dash.notifications')}</h1>
            <p className="text-sm text-gray-500 mt-1">
              {t('noti.desc')}
              {unreadCount > 0 && <span className="ml-2 font-semibold text-sahaay-deep">{unreadCount} unread</span>}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Filter: all / unread */}
            <div className="flex rounded-xl border border-gray-200 p-0.5">
              {([['all', 'All'], ['unread', 'Unread']] as const).map(([id, label]) => (
                <button
                  key={id}
                  onClick={() => setFilter(id)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                    filter === id ? 'bg-sahaay-deep text-white' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            <button
              onClick={markAllRead}
              disabled={unreadCount === 0}
              className="flex items-center gap-1.5 rounded-xl border border-gray-200 px-3 py-2 text-xs font-semibold text-gray-600 transition-colors hover:bg-white/60 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <CheckCheck size={14} /> Mark all read
            </button>
          </div>
        </div>
      </motion.div>

      <div className="space-y-2">
        <AnimatePresence initial={false}>
          {visible.map((n, i) => {
            const Icon = typeIcons[n.type] || Bell;
            return (
              <motion.div
                key={n.id}
                layout
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ delay: Math.min(0.04 * i, 0.24) }}
                onClick={() => markRead(n.id)}
                role="button"
                tabIndex={0}
                aria-label={n.read ? n.title : `${n.title} (unread)`}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); markRead(n.id); } }}
                className={`glass-card p-4 flex items-start gap-3 hover:-translate-y-0.5 transition-all cursor-pointer ${!n.read ? 'border-l-4 border-l-sahaay-deep bg-sahaay-surface/50' : ''}`}
              >
                <div className="w-10 h-10 rounded-xl bg-sahaay-deep/8 flex items-center justify-center text-sahaay-deep shrink-0">
                  <Icon size={18} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-bold text-gray-900">{n.title}</p>
                    {!n.read && <span className="w-2 h-2 rounded-full bg-sahaay-deep" />}
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                  <p className="text-[10px] text-gray-400 mt-1">{n.time}</p>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {visible.length === 0 && (
          <div className="py-16 text-center">
            <Bell size={40} className="mx-auto mb-3 text-gray-300" />
            <p className="font-medium text-gray-500">Nothing unread — you're all caught up</p>
          </div>
        )}
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
