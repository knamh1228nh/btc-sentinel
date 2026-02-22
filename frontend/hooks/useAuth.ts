import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase/client';

export function useAuth() {
  const [user, setUser] = useState<unknown>(null);
  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user: u } }) => setUser(u));
  }, []);
  return { user };
}
