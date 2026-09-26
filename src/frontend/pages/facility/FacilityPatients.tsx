import { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, UserCheck, Stethoscope, Search, Phone, MapPin } from 'lucide-react';
import { patients } from '../../../mock-data/mockData';
import { StatCard } from '../../components/ui/StatCard';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Avatar } from '../../components/ui/Avatar';
import { PageBanner } from '../../components/ui/PageBanner';

export function FacilityPatients() {
  const [query, setQuery] = useState('');

  const active = patients.filter((p) => p.status === 'active').length;
  const followup = patients.filter((p) => p.status === 'followup').length;
  const visible = patients.filter(
    (p) =>
      p.name.toLowerCase().includes(query.toLowerCase()) ||
      p.id.toLowerCase().includes(query.toLowerCase()) ||
      p.location.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      <PageBanner
        title="Patients"
        subtitle="Registered patients served by this facility."
        image="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80"
      />

      <div className="grid grid-cols-3 gap-4">
        <StatCard title="Registered" value={patients.length} icon={<Users size={22} />} delay={0} />
        <StatCard title="Active" value={active} icon={<UserCheck size={22} />} delay={0.05} />
        <StatCard title="Follow-up Due" value={followup} icon={<Stethoscope size={22} />} accent="sun" delay={0.1} />
      </div>

      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name, ID, or location..."
          className="sahaay-input pl-9 py-2 text-sm w-full"
        />
      </div>

      <div className="space-y-3">
        {visible.map((p, i) => (
          <motion.div
            key={p.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.04 }}
            className="glass-card-elevated p-4 flex flex-col sm:flex-row sm:items-center gap-4"
          >
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <Avatar initials={p.avatar} size="md" />
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-bold text-gray-900">{p.name}</p>
                  <StatusBadge status={p.status} />
                </div>
                <p className="text-[11px] text-gray-500 mt-0.5">
                  {p.id} · {p.age} yrs · {p.gender} · {p.bloodGroup}
                </p>
              </div>
            </div>
            <div className="flex flex-col gap-1 text-[11px] text-gray-500 sm:text-right shrink-0">
              <span className="flex items-center gap-1.5 sm:justify-end"><MapPin size={11} className="text-sahaay-deep" />{p.location}</span>
              <span className="flex items-center gap-1.5 sm:justify-end"><Phone size={11} className="text-sahaay-deep" />{p.phone}</span>
              <span className="text-gray-400">Registered {p.registeredDate}</span>
            </div>
          </motion.div>
        ))}
        {visible.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-8">No patients match this search.</p>
        )}
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
