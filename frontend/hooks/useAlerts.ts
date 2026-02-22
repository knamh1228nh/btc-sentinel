import { useState, useEffect } from 'react';
import { fetchBackend } from '@/lib/api/backend';

export function useAlerts() {
  const [alerts, setAlerts] = useState<unknown[]>([]);
  useEffect(() => {
    fetchBackend<{ alerts: unknown[] }>('/api/v1/alerts/').then((r) => setAlerts(r.alerts || []));
  }, []);
  return { alerts };
}
