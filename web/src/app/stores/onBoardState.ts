import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface StoreState {
  isCompleted: boolean;
  setIsCompleted: (value: boolean) => void;
}

// Create the Zustand store with persist to store the onboarding state in localStorage
const useOnboardStore = create<StoreState>()(
  persist(
    (set) => ({
      isCompleted: false,
      setIsCompleted: (value: boolean) => set({ isCompleted: value }),
    }),
    {
      name: 'isCompleted-storage',
    },
  ),
);

export default useOnboardStore;
