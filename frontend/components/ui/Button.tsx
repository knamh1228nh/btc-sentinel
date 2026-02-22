import { ButtonHTMLAttributes } from 'react';

export function Button({ children, className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button className={`px-4 py-2 rounded bg-blue-600 text-white ${className}`} {...props}>
      {children}
    </button>
  );
}
