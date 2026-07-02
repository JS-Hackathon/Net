"use client";

import React, { createContext, useContext, useEffect } from "react";
import { useAuthStore } from "@/lib/store/authStore";
import { User } from "@/lib/services/auth";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (accessToken: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading, checkAuth, logout } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (accessToken: string) => {
    useAuthStore.getState().setTokens(accessToken, localStorage.getItem("refresh_token") || "");
    await useAuthStore.getState().checkAuth();
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
