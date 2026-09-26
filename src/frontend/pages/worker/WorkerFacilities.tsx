import { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Clock, Users, Phone, Navigation, Search, Stethoscope } from 'lucide-react';
import { facilities } from '../../../mock-data/mockData';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { PageBanner } from '../../components/ui/PageBanner';
import { Button } from '../../components/ui/Button';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

export function WorkerFacilities() {
  const [search, setSearch] = useState('');
  const { t } = useLanguage();
  const [sortBy, setSortBy] = useState('distance');
  const { showToast } = useToast();

  const sorted = [...facilities]
    .filter(f => f.name.toLowerCase().includes(search.toLowerCase()) || f.type.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => sortBy === 'distance' ? a.distance - b.distance : a.waitingTime - b.waitingTime);

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('dash.facilities')}
        subtitle="Find and recommend healthcare facilities for your patients."
        image="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80"
      />

      {/* Search and sort */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search facilities..." className="sahaay-input pl-9" />
        </div>
        <div className="flex gap-2">
          <button onClick={() => setSortBy('distance')} className={`px-3 py-2 rounded-xl text-xs font-semibold transition-colors ${sortBy === 'distance' ? 'bg-sahaay-deep text-white' : 'bg-white/60 text-gray-600 border border-gray-200'}`}>
            <Navigation size={12} className="inline mr-1" />Nearest
          </button>
          <button onClick={() => setSortBy('wait')} className={`px-3 py-2 rounded-xl text-xs font-semibold transition-colors ${sortBy === 'wait' ? 'bg-sahaay-deep text-white' : 'bg-white/60 text-gray-600 border border-gray-200'}`}>
            <Clock size={12} className="inline mr-1" />Fastest
          </button>
        </div>
      </div>

      {/* Facility cards */}
      <div className="space-y-4">
        {sorted.map((facility, i) => (
          <motion.div
            key={facility.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * i }}
            className="glass-card-elevated p-5 hover:-translate-y-0.5 transition-all duration-200"
          >
            <div className="flex flex-col gap-3">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-base font-bold text-gray-900">{facility.name}</p>
                  <p className="text-xs text-gray-500">{facility.type}</p>
                </div>
                <StatusBadge status={facility.medicines} />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <MapPin size={14} className="text-sahaay-deep shrink-0" />
                  <span>{facility.distance} km away</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <Users size={14} className="text-sahaay-deep shrink-0" />
                  <span>{facility.doctorsAvailable} doctors</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <Clock size={14} className="text-sahaay-deep shrink-0" />
                  <span>~{facility.waitingTime} min wait</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <Stethoscope size={14} className="text-sahaay-deep shrink-0" />
                  <span>{facility.beds} beds ({facility.occupancy}% occ.)</span>
                </div>
              </div>

              {/* Services */}
              <div className="flex flex-wrap gap-1.5">
                {facility.services.slice(0, 5).map((service, j) => (
                  <span key={j} className="px-2 py-0.5 rounded-full bg-sahaay-deep/6 text-sahaay-deep text-[10px] font-medium">
                    {service}
                  </span>
                ))}
                {facility.services.length > 5 && (
                  <span className="px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 text-[10px] font-medium">
                    +{facility.services.length - 5} more
                  </span>
                )}
              </div>

              {/* Diagnostics */}
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span className="font-medium">Diagnostics:</span>
                {facility.diagnostics.slice(0, 3).join(', ')}
                {facility.diagnostics.length > 3 && ` +${facility.diagnostics.length - 3} more`}
              </div>

              <div className="flex gap-2 pt-1">
                <Button size="sm" onClick={() => showToast(`Recommended ${facility.name} to patient`)}>
                  <Phone size={14} /> Contact
                </Button>
                <Button size="sm" variant="secondary" onClick={() => showToast(`Referral to ${facility.name} initiated`)}>
                  Refer Patient
                </Button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="h-4 lg:hidden" />
    </div>
  );
}
