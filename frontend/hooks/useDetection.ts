import { useState } from 'react';
import { fetchBackend } from '@/lib/api/backend';

export function useDetection() {
  const [loading, setLoading] = useState(false);
  const runDetection = async (payload: object) => {
    setLoading(true);
    try {
      const res = await fetchBackend('/api/v1/detection/', {
        method: 'POST',
        body: JSON.stringify({ source: 'upbit', payload }),
      });
      return res;
    } finally {
      setLoading(false);
    }
  };
  return { runDetection, loading };
}
