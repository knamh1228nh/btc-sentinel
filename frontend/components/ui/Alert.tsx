import { HTMLAttributes } from 'react';

export function Alert({ children, className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div role="alert" className={`p-4 rounded border ${className}`} {...props}>
      {children}
    </div>
  );
}
