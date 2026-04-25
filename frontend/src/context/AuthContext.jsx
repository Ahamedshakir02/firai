import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export function AuthProvider({ children }) {
  const [officer, setOfficer] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('firai_token'));
  const [loading, setLoading] = useState(true);

  // On mount, verify stored token
  useEffect(() => {
    if (token) {
      fetchProfile(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchProfile = async (t) => {
    try {
      const { data } = await axios.get(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${t}` },
      });
      setOfficer(data);
      setToken(t);
    } catch {
      // Token invalid/expired
      localStorage.removeItem('firai_token');
      setToken(null);
      setOfficer(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (badge_number, password) => {
    const { data } = await axios.post(`${API_BASE}/auth/login`, {
      badge_number,
      password,
    });
    const t = data.access_token;
    localStorage.setItem('firai_token', t);
    setToken(t);
    setOfficer(data.officer);
    return data.officer;
  };

  const logout = () => {
    localStorage.removeItem('firai_token');
    setToken(null);
    setOfficer(null);
  };

  return (
    <AuthContext.Provider value={{ officer, token, loading, login, logout, isAuthenticated: !!officer }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;
