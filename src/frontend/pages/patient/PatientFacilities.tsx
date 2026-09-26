import { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Clock, Users, Stethoscope, Filter } from 'lucide-react';
import { facilities } from '../../../mock-data/mockData';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { PageBanner } from '../../components/ui/PageBanner';
import { Button } from '../../components/ui/Button';
import { useToast } from '../../components/ui/Toast';
import { useLanguage } from '../../context/providers';

export function PatientFacilities() {
  const [filterType, setFilterType] = useState('all');
  const { t } = useLanguage();
  const { showToast } = useToast();

  const types = ['all', 'Primary Health Centre', 'Community Health Centre', 'District Hospital', 'Rural Health Centre', 'Specialist Centre'];
  const filtered = filterType === 'all' ? facilities : facilities.filter(f => f.type === filterType);

  return (
    <div className="space-y-6">
      <PageBanner
        title={t('fac.findRight')}
        subtitle="Recommended based on your healthcare need, available services and accessibility."
        image="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80"
      />

      {/* Filters */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="glass-card p-4">
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <Filter size={16} className="text-gray-400 shrink-0" />
          {types.map(type => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                filterType === type ? 'bg-sahaay-deep text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {type === 'all' ? 'All Types' : type.replace('Health ', 'H. ')}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Facility cards */}
      <div className="grid md:grid-cols-2 gap-4">
        {filtered.map((facility, i) => (
          <motion.div
            key={facility.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * i }}
            className="glass-card-elevated p-5 hover:-translate-y-0.5 transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-gray-900">{facility.name}</h3>
                <p className="text-xs text-gray-500">{facility.type}</p>
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge status={facility.emergency ? 'active' : 'pending'} />
                <StatusBadge status={facility.medicines} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <MapPin size={14} className="text-sahaay-deep shrink-0" />
                <span>{facility.distance} km away</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Clock size={14} className="text-sahaay-deep shrink-0" />
                <span>~{facility.waitingTime} min wait</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Users size={14} className="text-sahaay-deep shrink-0" />
                <span>{facility.doctorsAvailable} doctors</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Stethoscope size={14} className="text-sahaay-deep shrink-0" />
                <span>{facility.beds} beds ({facility.occupancy}% full)</span>
              </div>
            </div>

            <div className="mb-4">
              <p className="text-xs font-semibold text-gray-700 mb-1.5">Services</p>
              <div className="flex flex-wrap gap-1.5">
                {facility.services.map((s, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded-md bg-sahaay-deep/6 text-[10px] font-medium text-sahaay-deep">{s}</span>
                ))}
              </div>
            </div>

            <div className="mb-4">
              <p className="text-xs font-semibold text-gray-700 mb-1.5">Diagnostics Available</p>
              <div className="flex flex-wrap gap-1.5">
                {facility.diagnostics.slice(0, 4).map((d, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded-md bg-blue-50 text-[10px] font-medium text-blue-700">{d}</span>
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              <Button size="sm" variant="secondary" onClick={() => showToast(`${facility.name} details viewed`)}>{t('fac.viewFacility')}</Button>
              <Button size="sm" onClick={() => showToast(`Directions to ${facility.name}`)}>Get Directions</Button>
            </div>
          </motion.div>
        ))}
      </div>
      <div className="h-4 lg:hidden" />
    </div>
  );
}
