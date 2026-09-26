import { useState } from 'react';

interface Tab { id: string; label: string; count?: number; }
interface TabsProps { tabs: Tab[]; activeTab?: string; onChange: (id: string) => void; }

export function Tabs({ tabs, activeTab, onChange }: TabsProps) {
  const [active, setActive] = useState(activeTab || tabs[0]?.id);
  const current = activeTab ?? active;
  const handleChange = (id: string) => { setActive(id); onChange(id); };

  return (
    <div className="flex gap-1 p-1 bg-white/60 backdrop-blur-sm rounded-xl border border-sahaay-deep/8">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => handleChange(tab.id)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
            current === tab.id
              ? 'bg-sahaay-deep text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-white/60'
          }`}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className={`text-[11px] px-1.5 py-0.5 rounded-full font-bold ${current === tab.id ? 'bg-white/20' : 'bg-gray-200 text-gray-600'}`}>
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
