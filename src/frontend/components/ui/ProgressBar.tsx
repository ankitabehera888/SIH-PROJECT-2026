import { motion } from 'framer-motion';

interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  height?: number;
  showLabel?: boolean;
  label?: string;
}

export function ProgressBar({ value, max = 100, color = 'from-sahaay-deep to-sahaay-500', height = 8, showLabel = false, label }: ProgressBarProps) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="w-full">
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-xs font-medium text-gray-600">{label || ''}</span>
          {showLabel && <span className="text-xs font-bold text-sahaay-deep">{Math.round(pct)}%</span>}
        </div>
      )}
      <div className="w-full rounded-full bg-gray-100 overflow-hidden" style={{ height }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full rounded-full bg-gradient-to-r ${color}`}
        />
      </div>
    </div>
  );
}
