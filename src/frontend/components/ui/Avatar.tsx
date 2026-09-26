interface AvatarProps {
  initials: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
}

const sizes = { sm: 'w-8 h-8 text-xs', md: 'w-10 h-10 text-sm', lg: 'w-12 h-12 text-base', xl: 'w-16 h-16 text-lg' };

export function Avatar({ initials, size = 'md', color = 'from-sahaay-deep to-sahaay-500' }: AvatarProps) {
  return (
    <div className={`${sizes[size]} rounded-full bg-gradient-to-br ${color} flex items-center justify-center text-white font-bold shrink-0`}>
      {initials}
    </div>
  );
}
