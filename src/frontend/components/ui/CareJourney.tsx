import { motion } from 'framer-motion';
import { Check, Circle, Dot } from 'lucide-react';

interface JourneyStep {
  label: string;
  status: 'completed' | 'current' | 'upcoming';
  date?: string;
}

interface CareJourneyProps {
  steps: JourneyStep[];
  orientation?: 'vertical' | 'horizontal';
}

export function CareJourney({ steps, orientation = 'vertical' }: CareJourneyProps) {
  if (orientation === 'horizontal') {
    return (
      <div className="flex items-center gap-0 overflow-x-auto pb-4">
        {steps.map((step, i) => (
          <div key={i} className="flex items-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="flex flex-col items-center min-w-[90px]"
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all ${
                step.status === 'completed'
                  ? 'bg-sahaay-deep border-sahaay-deep text-white'
                  : step.status === 'current'
                  ? 'bg-white border-sahaay-500 text-sahaay-deep shadow-[0_0_0_4px_rgba(31,104,73,0.1)]'
                  : 'bg-white border-gray-200 text-gray-400'
              }`}>
                {step.status === 'completed' ? <Check size={18} /> : step.status === 'current' ? <Dot size={20} /> : <Circle size={16} />}
              </div>
              <span className={`text-[11px] font-semibold mt-2 text-center ${
                step.status === 'completed' ? 'text-sahaay-deep' : step.status === 'current' ? 'text-gray-800' : 'text-gray-400'
              }`}>{step.label}</span>
              {step.date && <span className="text-[10px] text-gray-400">{step.date}</span>}
            </motion.div>
            {i < steps.length - 1 && (
              <div className={`h-[2px] w-10 mt-[-16px] ${
                step.status === 'completed' ? 'bg-sahaay-deep' : 'bg-gray-200'
              }`} />
            )}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="relative pl-2">
      {steps.map((step, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.08 }}
          className="relative flex items-start gap-4 pb-6 last:pb-0"
        >
          {/* Line */}
          {i < steps.length - 1 && (
            <div className={`absolute left-[15px] top-[32px] w-[2px] h-[calc(100%-20px)] ${
              step.status === 'completed' ? 'bg-sahaay-deep' : 'bg-gray-200'
            }`} />
          )}
          {/* Node */}
          <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 z-10 ${
            step.status === 'completed'
              ? 'bg-sahaay-deep border-sahaay-deep text-white'
              : step.status === 'current'
              ? 'bg-white border-sahaay-500 text-sahaay-deep shadow-[0_0_0_4px_rgba(31,104,73,0.1)]'
              : 'bg-white border-gray-200 text-gray-400'
          }`}>
            {step.status === 'completed' ? <Check size={14} /> : step.status === 'current' ? <div className="w-2 h-2 rounded-full bg-sahaay-deep animate-pulse-soft" /> : <Circle size={12} />}
          </div>
          {/* Content */}
          <div className="pt-0.5">
            <p className={`text-sm font-semibold ${
              step.status === 'completed' ? 'text-sahaay-deep' : step.status === 'current' ? 'text-gray-900' : 'text-gray-400'
            }`}>{step.label}</p>
            {step.date && <p className="text-xs text-gray-400 mt-0.5">{step.date}</p>}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
