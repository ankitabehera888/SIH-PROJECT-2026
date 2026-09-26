import { useState } from 'react';
import { motion } from 'framer-motion';
import { Pill, Search, MapPin, Clock, Building2 } from 'lucide-react';
import { medicines } from '../../../mock-data/mockData';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { PageBanner } from '../../components/ui/PageBanner';
import { Button } from '../../components/ui/Button';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

export function PatientMedicines() {
  const [search, setSearch] = useState('');
  const { t } = useLanguage();
  const [category, setCategory] = useState('all');
  const { showToast } = useToast();

  const categories = ['all', 'Essential Medicines', 'Chronic Care', 'Maternal Care', 'Child Care', 'Emergency'];
  const filtered = medicines.filter(m =>
    (category === 'all' || m.category === category) &&
    (search === '' || m.name.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.medicines')}
        subtitle="Check medicine stock across nearby facilities."
        image="https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=1200&q=80"
      />

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input type="text" placeholder={t('med.searchMeds')} value={search} onChange={e => setSearch(e.target.value)} className="sahaay-input pl-10" />
        </div>
        <div className="flex gap-1.5 overflow-x-auto pb-1">
          {categories.map(cat => (
            <button key={cat} onClick={() => setCategory(cat)} className={`px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${category === cat ? 'bg-sahaay-deep text-white' : 'bg-white/60 text-gray-600 hover:bg-white border border-gray-200'}`}>
              {cat === 'all' ? 'All Categories' : cat}
            </button>
          ))}
        </div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((med, i) => (
          <motion.div key={med.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.04 * i }} className="glass-card p-4 hover:-translate-y-0.5 transition-all">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-xl bg-sahaay-deep/8 flex items-center justify-center text-sahaay-deep shrink-0">
                  <Pill size={16} />
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-900">{med.name}</p>
                  <p className="text-[10px] text-gray-500">{med.manufacturer}</p>
                </div>
              </div>
              <StatusBadge status={med.stock} />
            </div>
            <div className="space-y-1.5 text-xs text-gray-600 mb-4">
              <div className="flex items-center gap-1.5"><Building2 size={12} className="text-sahaay-deep" />{med.facility}</div>
              <div className="flex items-center gap-1.5"><MapPin size={12} className="text-sahaay-deep" />{med.distance} km away</div>
              <div className="flex items-center gap-1.5"><Clock size={12} className="text-sahaay-deep" />Updated: {med.lastUpdated}</div>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" className="flex-1" onClick={() => showToast(`Directions to ${med.facility}`)}>View Facility</Button>
              <Button size="sm" className="flex-1" onClick={() => showToast(`Reservation requested for ${med.name}`)}>Reserve</Button>
            </div>
          </motion.div>
        ))}
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
