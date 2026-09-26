interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

const statusColors: Record<string, string> = {
  active: 'bg-emerald-100 text-emerald-700',
  completed: 'bg-emerald-100 text-emerald-700',
  upcoming: 'bg-blue-100 text-blue-700',
  pending: 'bg-amber-100 text-amber-700',
  accepted: 'bg-emerald-100 text-emerald-700',
  in_transit: 'bg-blue-100 text-blue-700',
  appointment_scheduled: 'bg-purple-100 text-purple-700',
  followup_required: 'bg-orange-100 text-orange-700',
  cancelled: 'bg-red-100 text-red-700',
  missed: 'bg-red-100 text-red-700',
  high: 'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low: 'bg-blue-100 text-blue-700',
  normal: 'bg-gray-100 text-gray-600',
  available: 'bg-emerald-100 text-emerald-700',
  'Low Stock': 'bg-amber-100 text-amber-700',
  Unavailable: 'bg-red-100 text-red-700',
};

export function StatusBadge({ status, size = 'sm' }: StatusBadgeProps) {
  const colorClass = statusColors[status] || 'bg-gray-100 text-gray-600';
  const sizeClass = size === 'sm' ? 'px-2.5 py-0.5 text-[11px]' : 'px-3 py-1 text-xs';
  return (
    <span className={`inline-flex items-center rounded-full font-semibold capitalize ${colorClass} ${sizeClass}`}>
      {status.replace(/_/g, ' ')}
    </span>
  );
}
