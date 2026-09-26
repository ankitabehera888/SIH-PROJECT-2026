import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ClipboardList, Clock, CheckCircle2, Truck } from 'lucide-react';
import { referrals } from '../../../mock-data/mockData';
import { StatCard } from '../../components/ui/StatCard';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Avatar } from '../../components/ui/Avatar';
import { PageBanner } from '../../components/ui/PageBanner';

const FACILITY = 'PHC Chandrapur';

type Filter = 'all' | 'inbound' | 'outbound';

export function FacilityReferrals() {
  const [filter, setFilter] = useState<Filter>('all');

  const inbound = referrals.filter((r) => r.destinationFacility === FACILITY);
  const outbound = referrals.filter((r) => r.sourceFacility === FACILITY);
  const visible = filter === 'inbound' ? inbound : filter === 'outbound' ? outbound : referrals;

  const pendingCount = referrals.filter((r) => r.status === 'pending').length;
  const transitCount = referrals.filter((r) => r.status === 'in_transit').length;
  const completedCount = referrals.filter((r) => r.status === 'completed').length;

  return (
    <div className="space-y-6">
      <PageBanner
        title="Referrals"
        subtitle={`Inbound and outbound referrals for ${FACILITY}.`}
        image="https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=1200&q=80"
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Referrals" value={referrals.length} icon={<ClipboardList size={22} />} delay={0} />
        <StatCard title="Pending" value={pendingCount} icon={<Clock size={22} />} accent="sun" delay={0.05} />
        <StatCard title="In Transit" value={transitCount} icon={<Truck size={22} />} accent="oxy" delay={0.1} />
        <StatCard title="Completed" value={completedCount} icon={<CheckCircle2 size={22} />} delay={0.15} />
      </div>

      {/* Direction filter */}
      <div className="flex gap-2">
        {([
          { key: 'all', label: `All (${referrals.length})` },
          { key: 'inbound', label: `Inbound (${inbound.length})` },
          { key: 'outbound', label: `Outbound (${outbound.length})` },
        ] as { key: Filter; label: string }[]).map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-colors ${
              filter === f.key ? 'bg-sahaay-deep text-white' : 'glass-card text-gray-600 hover:text-sahaay-deep'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Referral list */}
      <div className="space-y-3">
        {visible.map((r, i) => {
          const isInbound = r.destinationFacility === FACILITY;
          return (
            <motion.div
              key={r.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.05 }}
              className="glass-card-elevated p-4 flex flex-col sm:flex-row sm:items-center gap-4"
            >
              <div className="flex items-center gap-3 min-w-0 sm:w-56 shrink-0">
                <Avatar initials={r.patientName.split(' ').map((n) => n[0]).join('').slice(0, 2)} size="md" />
                <div className="min-w-0">
                  <p className="text-sm font-bold text-gray-900 truncate">{r.patientName}</p>
                  <p className="text-[11px] text-gray-500">{r.id} · {r.assignedDoctor}</p>
                </div>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 text-xs font-semibold text-gray-700 flex-wrap">
                  <span>{r.sourceFacility}</span>
                  <ArrowRight size={12} className="text-sahaay-deep shrink-0" />
                  <span>{r.destinationFacility}</span>
                  <span className={`ml-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${isInbound ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                    {isInbound ? 'Inbound' : 'Outbound'}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{r.reason}</p>
                <p className="text-[11px] text-gray-400 mt-0.5">Created {r.createdDate} · Expected {r.expectedDate}</p>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <StatusBadge status={r.priority} />
                <StatusBadge status={r.status} />
              </div>
            </motion.div>
          );
        })}
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
