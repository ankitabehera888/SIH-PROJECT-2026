import { useState } from 'react';
import { motion } from 'framer-motion';
import { Pill, PackageCheck, AlertTriangle, PackageX, Search } from 'lucide-react';
import { medicines } from '../../../mock-data/mockData';
import { StatCard } from '../../components/ui/StatCard';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { PageBanner } from '../../components/ui/PageBanner';

const FACILITY = 'PHC Chandrapur';

export function FacilityInventory() {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');

  // This console manages one facility's stock; network items show for reorder reference.
  const ownStock = medicines.filter((m) => m.facility === FACILITY);
  const lowStock = ownStock.filter((m) => m.stock === 'Low Stock');
  const unavailable = ownStock.filter((m) => m.stock === 'Unavailable');
  const availablePct = Math.round((ownStock.filter((m) => m.stock === 'Available').length / Math.max(ownStock.length, 1)) * 100);

  const categories = ['All', ...Array.from(new Set(medicines.map((m) => m.category)))];
  const visible = medicines.filter(
    (m) =>
      (category === 'All' || m.category === category) &&
      m.name.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      <PageBanner
        title="Inventory"
        subtitle={`Medicine and supply stock at ${FACILITY}, with network availability for reorders.`}
        image="https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=1200&q=80"
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Items Tracked" value={ownStock.length} icon={<Pill size={22} />} delay={0} />
        <StatCard title="Stock Availability" value={`${availablePct}%`} icon={<PackageCheck size={22} />} delay={0.05} />
        <StatCard title="Low Stock" value={lowStock.length} icon={<AlertTriangle size={22} />} accent="sun" delay={0.1} />
        <StatCard title="Out of Stock" value={unavailable.length} icon={<PackageX size={22} />} accent="pulse" delay={0.15} />
      </div>

      {(lowStock.length > 0 || unavailable.length > 0) && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card-elevated p-4 border-l-4 border-amber-400">
          <p className="text-xs font-bold text-amber-600 uppercase tracking-wider mb-1.5">Reorder alerts</p>
          <p className="text-sm text-gray-700">
            {[...unavailable, ...lowStock].map((m) => m.name).join(', ') || 'None'} — restock recommended.
          </p>
        </motion.div>
      )}

      {/* Search + category filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search medicines..."
            className="sahaay-input pl-9 py-2 text-sm w-full"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`px-3 py-2 rounded-xl text-xs font-bold transition-colors ${
                category === c ? 'bg-sahaay-deep text-white' : 'glass-card text-gray-600 hover:text-sahaay-deep'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Stock grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {visible.map((m, i) => (
          <motion.div
            key={m.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.03 }}
            className="glass-card-elevated p-4"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="w-9 h-9 rounded-xl bg-sahaay-deep/8 flex items-center justify-center text-sahaay-deep shrink-0">
                <Pill size={16} />
              </div>
              <StatusBadge status={m.stock} />
            </div>
            <p className="text-sm font-bold text-gray-900">{m.name}</p>
            <p className="text-[11px] text-gray-500 mt-0.5">{m.category} · {m.manufacturer}</p>
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
              <span className="text-[11px] text-gray-500">{m.facility}</span>
              <span className="text-[11px] text-gray-400">Updated {m.lastUpdated}</span>
            </div>
          </motion.div>
        ))}
        {visible.length === 0 && (
          <p className="text-sm text-gray-500 col-span-full text-center py-8">No medicines match this filter.</p>
        )}
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
