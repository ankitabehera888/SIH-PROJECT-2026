import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  loading?: boolean;
}

export function Button({ variant = 'primary', size = 'md', icon, loading, children, className = '', ...props }: ButtonProps) {
  const base = 'inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-200 cursor-pointer select-none disabled:opacity-50 disabled:cursor-not-allowed';
  const variants: Record<string, string> = {
    primary: 'bg-gradient-to-br from-sahaay-deep to-sahaay-600 text-white shadow-[0_2px_8px_rgba(31,104,73,0.25)] hover:-translate-y-0.5 hover:shadow-[0_4px_16px_rgba(31,104,73,0.35)] active:translate-y-0 active:shadow-[0_1px_4px_rgba(31,104,73,0.2)]',
    secondary: 'bg-sahaay-deep/8 text-sahaay-deep border border-sahaay-deep/15 hover:bg-sahaay-deep/14 hover:-translate-y-0.5',
    ghost: 'bg-transparent text-sahaay-deep hover:bg-sahaay-deep/6',
    danger: 'bg-red-500 text-white hover:bg-red-600 shadow-[0_2px_8px_rgba(239,68,68,0.25)]',
    outline: 'bg-transparent text-sahaay-deep border-2 border-sahaay-deep/20 hover:border-sahaay-deep/40 hover:bg-sahaay-deep/4',
  };
  const sizes: Record<string, string> = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-5 py-2.5 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} disabled={loading || props.disabled} {...props}>
      {loading ? <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" /> : icon}
      {children}
    </button>
  );
}
