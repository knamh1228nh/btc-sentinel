import { HTMLAttributes } from 'react';

export function Table({ children, className = '', ...props }: HTMLAttributes<HTMLTableElement>) {
  return <table className={`w-full ${className}`} {...props}>{children}</table>;
}
