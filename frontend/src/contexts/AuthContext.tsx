import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface AuthContextType {
  isAuthenticated: boolean;
  isAdmin: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  adminLogin: (email: string, password: string) => Promise<void>;
  logout: () => void;
  token: string | null;
}

interface User {
  id: string;
  email: string;
  display_name: string;
  is_admin?: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      const parsedUser = JSON.parse(storedUser);
      setUser(parsedUser);
      setIsAuthenticated(true);
      setIsAdmin(parsedUser.is_admin || false);
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await axios.post(`${apiUrl}/api/auth/login`, formData);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      const userObj = {
        id: 'user-id', // This would come from a /me endpoint
        email: email,
        display_name: email.split('@')[0]
      };
      
      localStorage.setItem('user', JSON.stringify(userObj));
      setUser(userObj);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setIsAdmin(false);
    delete axios.defaults.headers.common['Authorization'];
  };

  const adminLogin = async (email: string, password: string) => {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await axios.post(`${apiUrl}/api/auth/admin/login`, formData);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      const userObj = {
        id: 'admin',
        email: email,
        display_name: 'Administrator',
        is_admin: true
      };
      
      localStorage.setItem('user', JSON.stringify(userObj));
      setUser(userObj);
      setIsAuthenticated(true);
      setIsAdmin(true);
    } catch (error) {
      console.error('Admin login failed:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isAdmin, user, login, adminLogin, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
};
