import { HTMLAttributes } from 'react';

export function Card({ children, className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`border rounded-lg p-4 ${className}`} {...props}>
      {children}
    </div>
  );
}
