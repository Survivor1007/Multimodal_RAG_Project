import { create } from "zustand";

type Theme = "dark" | "light";

interface ThemeStoreState {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

const getInitialTheme = (): Theme => {
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem("theme") as Theme;
    if (saved === "dark" || saved === "light") {
      return saved;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return "dark";
};

const applyThemeToDOM = (theme: Theme) => {
  if (typeof window !== "undefined") {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }
};

const initialTheme = getInitialTheme();
applyThemeToDOM(initialTheme);

export const useThemeStore = create<ThemeStoreState>((set) => ({
  theme: initialTheme,

  toggleTheme: () =>
    set((state) => {
      const nextTheme = state.theme === "dark" ? "light" : "dark";
      applyThemeToDOM(nextTheme);
      return { theme: nextTheme };
    }),

  setTheme: (theme: Theme) => {
    applyThemeToDOM(theme);
    set({ theme });
  },
}));

// Export legacy ThemeStore alias for backwards compatibility
export const ThemeStore = useThemeStore;