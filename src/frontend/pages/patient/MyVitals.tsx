import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Heart, Activity, Droplets, Thermometer, Weight,
  TrendingUp, TrendingDown, Minus, Plus, Calendar, X,
  AlertCircle, CheckCircle2, Target
} from 'lucide-react';
import { useLanguage } from '../../context/providers';
import { PageBanner } from '../../components/ui/PageBanner';

interface VitalReading {
  id: string;
  date: string;
  time: string;
  systolic?: number;
  diastolic?: number;
  heartRate?: number;
  bloodSugar?: number;
  temperature?: number;
  weight?: number;
  height?: number;
  spo2?: number;
  notes?: string;
}

interface VitalTarget {
  label: string;
  min: number;
  max: number;
  unit: string;
  color: string;
}

const vitalTargets: Record<string, VitalTarget> = {
  bloodPressure: { label: 'Blood Pressure', min: 90, max: 140, unit: 'mmHg', color: '#1F6849' },
  heartRate: { label: 'Heart Rate', min: 60, max: 100, unit: 'bpm', color: '#ef4444' },
  bloodSugar: { label: 'Blood Sugar (Fasting)', min: 70, max: 110, unit: 'mg/dL', color: '#f59e0b' },
  temperature: { label: 'Body Temperature', min: 97, max: 99, unit: '°F', color: '#8b5cf6' },
  weight: { label: 'Weight', min: 45, max: 90, unit: 'kg', color: '#1F6849' },
  spo2: { label: 'Blood Oxygen (SpO₂)', min: 95, max: 100, unit: '%', color: '#3b82f6' },
};

const mockVitals: VitalReading[] = [
  { id: 'V001', date: '2026-09-01', time: '08:30 AM', systolic: 132, diastolic: 85, heartRate: 78, bloodSugar: 98, temperature: 98.4, weight: 72.5, spo2: 98, notes: 'Morning reading' },
  { id: 'V002', date: '2026-08-30', time: '09:00 AM', systolic: 128, diastolic: 82, heartRate: 75, bloodSugar: 102, temperature: 98.2, weight: 72.3, spo2: 97, notes: 'After medication' },
  { id: 'V003', date: '2026-08-28', time: '08:15 AM', systolic: 138, diastolic: 88, heartRate: 82, bloodSugar: 110, temperature: 98.6, weight: 72.8, spo2: 98, notes: 'Before breakfast' },
  { id: 'V004', date: '2026-08-25', time: '08:45 AM', systolic: 135, diastolic: 86, heartRate: 80, bloodSugar: 105, temperature: 98.3, weight: 73.0, spo2: 97, notes: '' },
  { id: 'V005', date: '2026-08-22', time: '09:10 AM', systolic: 142, diastolic: 90, heartRate: 85, bloodSugar: 115, temperature: 98.8, weight: 73.2, spo2: 96, notes: 'Elevated reading' },
];

function getReadingStatus(value: number, target: VitalTarget): 'normal' | 'warning' | 'danger' {
  if (value < target.min * 0.9 || value > target.max * 1.15) return 'danger';
  if (value < target.min || value > target.max) return 'warning';
  return 'normal';
}

function getStatusIcon(status: 'normal' | 'warning' | 'danger') {
  if (status === 'normal') return <CheckCircle2 size={14} className="text-emerald-500" />;
  if (status === 'warning') return <AlertCircle size={14} className="text-amber-500" />;
  return <AlertCircle size={14} className="text-red-500" />;
}

function getTrend(current: number, previous: number): 'up' | 'down' | 'stable' {
  const diff = current - previous;
  if (Math.abs(diff) < 1) return 'stable';
  return diff > 0 ? 'up' : 'down';
}

export function MyVitals() {
  const { t } = useLanguage();
  const [vitals] = useState<VitalReading[]>(mockVitals);
  const [activeTab, setActiveTab] = useState<'overview' | 'history' | 'add'>('overview');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newReading, setNewReading] = useState({
    systolic: '', diastolic: '', heartRate: '', bloodSugar: '', temperature: '', weight: '', spo2: '', notes: ''
  });

  const latest = vitals[0];
  const previous = vitals[1];

  const summaryCards = [
    {
      label: t('vitals.bloodPressure'),
      value: `${latest.systolic}/${latest.diastolic}`,
      target: '90-140/60-90 mmHg',
      icon: Heart,
      color: 'from-red-500/10 to-red-400/5',
      textColor: 'text-red-500',
      status: getReadingStatus(latest.systolic || 0, vitalTargets.bloodPressure),
      trend: getTrend(latest.systolic || 0, previous.systolic || 0),
    },
    {
      label: t('vitals.heartRate'),
      value: `${latest.heartRate}`,
      target: '60-100 bpm',
      icon: Activity,
      color: 'from-pink-500/10 to-pink-400/5',
      textColor: 'text-pink-500',
      status: getReadingStatus(latest.heartRate || 0, vitalTargets.heartRate),
      trend: getTrend(latest.heartRate || 0, previous.heartRate || 0),
    },
    {
      label: t('vitals.bloodSugar'),
      value: `${latest.bloodSugar}`,
      target: '70-110 mg/dL',
      icon: Droplets,
      color: 'from-amber-500/10 to-amber-400/5',
      textColor: 'text-amber-500',
      status: getReadingStatus(latest.bloodSugar || 0, vitalTargets.bloodSugar),
      trend: getTrend(latest.bloodSugar || 0, previous.bloodSugar || 0),
    },
    {
      label: t('vitals.temperature'),
      value: `${latest.temperature}`,
      target: '97-99 °F',
      icon: Thermometer,
      color: 'from-purple-500/10 to-purple-400/5',
      textColor: 'text-purple-500',
      status: getReadingStatus(latest.temperature || 0, vitalTargets.temperature),
      trend: getTrend(latest.temperature || 0, previous.temperature || 0),
    },
    {
      label: t('vitals.weight'),
      value: `${latest.weight}`,
      target: '45-90 kg',
      icon: Weight,
      color: 'from-sahaay-deep/10 to-sahaay-500/5',
      textColor: 'text-sahaay-deep',
      status: getReadingStatus(latest.weight || 0, vitalTargets.weight),
      trend: getTrend(latest.weight || 0, previous.weight || 0),
    },
    {
      label: t('vitals.spo2'),
      value: `${latest.spo2}%`,
      target: '95-100%',
      icon: Target,
      color: 'from-blue-500/10 to-blue-400/5',
      textColor: 'text-blue-500',
      status: getReadingStatus(latest.spo2 || 0, vitalTargets.spo2),
      trend: getTrend(latest.spo2 || 0, previous.spo2 || 0),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageBanner
        title={t('vitals.title')}
        subtitle={t('vitals.desc')}
        image="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=1200&q=80"
      />
      <div className="flex justify-end">
        <button onClick={() => setShowAddModal(true)} className="sahaay-btn-primary flex items-center gap-2 text-sm">
          <Plus size={16} /> {t('vitals.logReading')}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-white/60 rounded-xl border border-sahaay-deep/8 w-fit">
        {(['overview', 'history'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
              activeTab === tab ? 'sahaay-gradient text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'overview' ? t('vitals.overview') : t('vitals.history')}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <>
          {/* Vital Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {summaryCards.map((card, i) => {
              const Icon = card.icon;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  whileHover={{ y: -2 }}
                  className="glass-card p-5 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center`}>
                      <Icon size={20} className={card.textColor} />
                    </div>
                    <div className="flex items-center gap-1.5">
                      {getStatusIcon(card.status)}
                      {card.trend === 'up' && <TrendingUp size={14} className="text-red-400" />}
                      {card.trend === 'down' && <TrendingDown size={14} className="text-emerald-400" />}
                      {card.trend === 'stable' && <Minus size={14} className="text-gray-300" />}
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 font-medium mb-1">{card.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{card.value} <span className="text-sm font-normal text-gray-400">{card.target.split(' ')[1]}</span></p>
                  <div className="mt-3 flex items-center justify-between">
                    <span className="text-[11px] text-gray-400">Target: {card.target}</span>
                    <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                      card.status === 'normal' ? 'bg-emerald-50 text-emerald-600' :
                      card.status === 'warning' ? 'bg-amber-50 text-amber-600' :
                      'bg-red-50 text-red-600'
                    }`}>
                      {card.status}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Trend mini-chart */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card-elevated p-6"
          >
            <h3 className="text-sm font-bold text-gray-900 mb-4">{t('vitals.recentTrend')}</h3>
            <div className="flex items-end gap-3 h-32">
              {[...vitals].reverse().map((v, i) => {
                const maxVal = 160;
                const height = ((v.systolic || 120) / maxVal) * 100;
                const isHigh = (v.systolic || 0) > 140;
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-1">
                    <span className="text-[10px] font-medium text-gray-500">{v.systolic}/{v.diastolic}</span>
                    <motion.div
                      initial={{ height: 0 }}
                      animate={{ height: `${height}%` }}
                      transition={{ duration: 0.6, delay: i * 0.1 }}
                      className={`w-full rounded-t-lg ${isHigh ? 'bg-amber-400' : 'bg-sahaay-deep/60'}`}
                    />
                    <span className="text-[10px] text-gray-400">{v.date.slice(5)}</span>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </>
      )}

      {activeTab === 'history' && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card-elevated overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-sahaay-deep/8">
                  <th className="text-left p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Date & Time</th>
                  <th className="text-left p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">BP (mmHg)</th>
                  <th className="text-left p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">{t('vitals.heartRate')}</th>
                  <th className="text-left p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">{t('vitals.bloodSugar')}</th>
                  <th className="text-left p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">{t('vitals.temperature')}</th>
                  <th className="text-left p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">{t('vitals.weight')}</th>
                  <th className="text-left p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">{t('vitals.spo2')}</th>
                  <th className="text-left p-4 text-xs font-bold text-gray-500 uppercase tracking-wider">{t('vitals.notes')}</th>
                </tr>
              </thead>
              <tbody>
                {vitals.map((v) => (
                  <tr key={v.id} className="border-b border-sahaay-deep/4 hover:bg-sahaay-surface/50 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Calendar size={14} className="text-sahaay-deep" />
                        <div>
                          <p className="font-medium text-gray-800">{v.date}</p>
                          <p className="text-[11px] text-gray-400">{v.time}</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4 font-medium text-gray-800">{v.systolic}/{v.diastolic}</td>
                    <td className="p-4 text-gray-600">{v.heartRate} bpm</td>
                    <td className="p-4 text-gray-600">{v.bloodSugar} mg/dL</td>
                    <td className="p-4 text-gray-600">{v.temperature}°F</td>
                    <td className="p-4 text-gray-600">{v.weight} kg</td>
                    <td className="p-4 text-gray-600">{v.spo2}%</td>
                    <td className="p-4 text-gray-400 text-xs">{v.notes || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card-elevated w-full max-w-lg p-6 mx-4"
          >
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-gray-900">{t('vitals.logVitals')}</h3>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={20} />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {[
                { label: t('vitals.systolicBP'), key: 'systolic', placeholder: '120' },
                { label: t('vitals.diastolicBP'), key: 'diastolic', placeholder: '80' },
                { label: t('vitals.heartRateBpm'), key: 'heartRate', placeholder: '75' },
                { label: t('vitals.bloodSugarMg'), key: 'bloodSugar', placeholder: '95' },
                { label: t('vitals.temperatureF'), key: 'temperature', placeholder: '98.4' },
                { label: t('vitals.weightKg'), key: 'weight', placeholder: '70' },
                { label: t('vitals.spo2Percent'), key: 'spo2', placeholder: '98' },
              ].map(field => (
                <div key={field.key}>
                  <label className="text-xs font-semibold text-gray-500 mb-1 block">{field.label}</label>
                  <input
                    type="number"
                    value={(newReading as any)[field.key]}
                    onChange={e => setNewReading(prev => ({ ...prev, [field.key]: e.target.value }))}
                    placeholder={field.placeholder}
                    className="sahaay-input text-sm"
                  />
                </div>
              ))}
            </div>
            <div className="mt-3">
              <label className="text-xs font-semibold text-gray-500 mb-1 block">{t('vitals.notes')}</label>
              <input
                type="text"
                value={newReading.notes}
                onChange={e => setNewReading(prev => ({ ...prev, notes: e.target.value }))}
                placeholder={t('vitals.notesPlaceholder')}
                className="sahaay-input text-sm"
              />
            </div>

            <div className="flex gap-2 mt-5">
              <button onClick={() => setShowAddModal(false)} className="sahaay-btn-secondary flex-1 py-2.5 text-sm">
                {t('vitals.cancel')}
              </button>
              <button className="sahaay-btn-primary flex-1 py-2.5 text-sm">
                {t('vitals.saveReading')}
              </button>
            </div>
          </motion.div>
        </div>
      )}

      <div className="h-4 lg:hidden" />
    </div>
  );
}
