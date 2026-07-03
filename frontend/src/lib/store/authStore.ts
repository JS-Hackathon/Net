import { create } from "zustand";
import {
  User,
  authService,
  LoginPayload,
  RegisterPayload,
  GoogleLoginPayload,
  ProfileUpdatePayload
} from "../services/auth";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isInitialized: boolean;

  setUser: (user: User | null) => void;
  setTokens: (accessToken: string | null, refreshToken: string | null) => void;

  register: (payload: RegisterPayload) => Promise<void>;
  login: (payload: LoginPayload) => Promise<void>;
  googleLogin: (payload: GoogleLoginPayload) => Promise<void>;
  refreshAccessToken: () => Promise<string | null>;
  logout: () => Promise<void>;
  updateProfile: (payload: ProfileUpdatePayload) => Promise<void>;
  checkAuth: (force?: boolean) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isLoading: false,
  isInitialized: false,

  setUser: (user) => set({ user }),

  setTokens: (accessToken, refreshToken) => {
    if (typeof window !== "undefined") {
      if (accessToken) {
        localStorage.setItem("access_token", accessToken);
      } else {
        localStorage.removeItem("access_token");
      }

      if (refreshToken) {
        localStorage.setItem("refresh_token", refreshToken);
      } else {
        localStorage.removeItem("refresh_token");
      }
    }
    set({ accessToken, refreshToken });
  },

  register: async (payload) => {
    set({ isLoading: true });
    try {
      await authService.register(payload);
    } finally {
      set({ isLoading: false });
    }
  },

  login: async (payload) => {
    set({ isLoading: true });
    try {
      const data = await authService.login(payload);
      get().setTokens(data.accessToken, data.refreshToken);
      set({ user: data.user });
    } finally {
      set({ isLoading: false });
    }
  },

  googleLogin: async (payload) => {
    set({ isLoading: true });
    try {
      const data = await authService.googleLogin(payload);
      get().setTokens(data.accessToken, data.refreshToken);
      set({ user: data.user });
    } finally {
      set({ isLoading: false });
    }
  },

  refreshAccessToken: async () => {
    const token = get().refreshToken || (typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null);
    if (!token) {
      await get().logout();
      return null;
    }
    try {
      const data = await authService.refreshToken({ refreshToken: token });
      get().setTokens(data.accessToken, data.refreshToken);
      return data.accessToken;
    } catch (error) {
      console.error("Token refresh failed:", error);
      await get().logout();
      return null;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      const token = get().refreshToken || (typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null);
      if (token) {
        await authService.logout({ refreshToken: token });
      }
    } catch (error) {
      console.error("Logout request failed:", error);
    } finally {
      get().setTokens(null, null);
      set({ user: null, isLoading: false });
    }
  },

  updateProfile: async (payload) => {
    set({ isLoading: true });
    try {
      const updatedUser = await authService.updateProfile(payload);
      set({ user: updatedUser });
    } finally {
      set({ isLoading: false });
    }
  },

  checkAuth: async (force: boolean = false) => {
    if (get().isInitialized && !force) return;

    if (typeof window === "undefined") {
      set({ isInitialized: true });
      return;
    }

    set({ isLoading: true });
    const accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");

    if (accessToken && refreshToken) {
      set({ accessToken, refreshToken });
      try {
        const user = await authService.getMe();
        set({ user });
      } catch (error) {
        console.warn("Access token invalid, trying to refresh...", error);
        // Thử refresh token
        try {
          const data = await authService.refreshToken({ refreshToken });
          get().setTokens(data.accessToken, data.refreshToken);
          const user = await authService.getMe();
          set({ user });
        } catch (refreshErr) {
          console.error("Auto refresh failed, logging out:", refreshErr);
          get().setTokens(null, null);
        }
      }
    }
    set({ isLoading: false, isInitialized: true });
  },
}));
