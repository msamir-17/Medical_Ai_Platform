import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  _hasHydrated: boolean; // NEW: To track if data is loaded from disk
  setToken: (token: string | null) => void;
  setHasHydrated: (state: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      _hasHydrated: false, // Start as false
      setToken: (token) => set({ token }),
      setHasHydrated: (state) => set({ _hasHydrated: state }),
      logout: () => set({ token: null }),
    }),
    { 
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        // Yeh function tab chalta hai jab LocalStorage se data load ho jata hai
        state?.setHasHydrated(true);
      }
    }
  )
);