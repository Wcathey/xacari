import { create } from 'zustand';
import { supabase } from '../config/supabase';
import { User, Profile } from '../types';

/**
 * Authentication Store
 *
 * Manages user authentication state using Supabase
 */

interface AuthState {
  user: User | null;
  profile: Profile | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, fullName?: string) => Promise<void>;
  signOut: () => Promise<void>;
  loadUser: () => Promise<void>;
  loadProfile: () => Promise<void>;
  updateProfile: (updates: Partial<Profile>) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  profile: null,
  isLoading: false,
  error: null,

  signIn: async (email: string, password: string) => {
    set({ isLoading: true, error: null });

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      set({ user: data.user as unknown as User });
      await get().loadProfile();
    } catch (error: any) {
      console.error('Sign in error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  signUp: async (email: string, password: string, fullName?: string) => {
    set({ isLoading: true, error: null });

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (error) throw error;

      set({ user: data.user as unknown as User });
      // Profile will be created automatically by the trigger
      await get().loadProfile();
    } catch (error: any) {
      console.error('Sign up error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  signOut: async () => {
    set({ isLoading: true, error: null });

    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;

      set({ user: null, profile: null });
    } catch (error: any) {
      console.error('Sign out error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  loadUser: async () => {
    set({ isLoading: true, error: null });

    try {
      const {
        data: { user },
        error,
      } = await supabase.auth.getUser();

      if (error) throw error;

      set({ user: user as unknown as User });

      if (user) {
        await get().loadProfile();
      }
    } catch (error: any) {
      console.error('Load user error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  loadProfile: async () => {
    const { user } = get();
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();

      if (error) throw error;

      set({ profile: data as Profile });
    } catch (error: any) {
      console.error('Load profile error:', error);
      set({ error: error.message });
    }
  },

  updateProfile: async (updates: Partial<Profile>) => {
    const { user } = get();
    if (!user) return;

    set({ isLoading: true, error: null });

    try {
      const { data, error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', user.id)
        .select()
        .single();

      if (error) throw error;

      set({ profile: data as Profile });
    } catch (error: any) {
      console.error('Update profile error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
