"use client";

import { api, User } from "@/shared/api";
import { createContext, ReactNode, useCallback, useContext, useEffect, useState } from "react";

type AuthState = {
  user: User | null;
  loading: boolean;
  login: (correo: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const refresh = useCallback(async () => {
    try {
      setUser(await api<User>("/auth/me"));
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    api<User>("/auth/me")
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(correo: string, password: string) {
    setUser(
      await api<User>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ correo, password }),
      }),
    );
  }
  async function logout() {
    await api<void>("/auth/logout", { method: "POST" });
    setUser(null);
  }
  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return value;
}
