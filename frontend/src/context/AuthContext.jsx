import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { setAuthToken } from '../api/client';

const AuthContext = createContext(null);

const TOKEN_KEY = 'k8s_auth_token';
const USER_KEY = 'k8s_auth_user';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem(USER_KEY);
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  const login = (authData) => {
    setToken(authData.access_token);
    setUser(authData.user);
    localStorage.setItem(TOKEN_KEY, authData.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(authData.user));
    setAuthToken(authData.access_token);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setAuthToken(null);
  };

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      login,
      logout,
    }),
    [token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
