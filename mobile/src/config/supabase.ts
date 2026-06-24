import { createClient } from '@supabase/supabase-js';
import CONFIG from './index';

/**
 * Supabase client for authentication and data storage
 *
 * IMPORTANT: Update CONFIG with your Supabase credentials before using
 */

if (!CONFIG.SUPABASE.URL || CONFIG.SUPABASE.URL === 'YOUR_SUPABASE_URL') {
  console.warn(
    '⚠️  Supabase URL not configured. Update src/config/index.ts with your Supabase credentials.'
  );
}

export const supabase = createClient(
  CONFIG.SUPABASE.URL,
  CONFIG.SUPABASE.ANON_KEY,
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
    },
  }
);

export default supabase;
