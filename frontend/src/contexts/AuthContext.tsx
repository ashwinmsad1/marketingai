import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name?: string;
  phone?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  initialized: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  company_name?: string;
  phone?: string;
}

type AuthAction = 
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'SET_INITIALIZED' };

const initialState: AuthState = {
  user: null,
  token: null,
  loading: false,
  initialized: false
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, loading: true };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        loading: false
      };
    case 'AUTH_FAILURE':
      return { ...state, user: null, token: null, loading: false };
    case 'LOGOUT':
      return { ...state, user: null, token: null, loading: false };
    case 'UPDATE_USER':
      return { ...state, user: action.payload };
    case 'SET_INITIALIZED':
      return { ...state, initialized: true };
    default:
      return state;
  }
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (token && refreshToken) {
          // Set token in API service
          authService.setAuthToken(token);
          
          try {
            // Get current user profile
            const userResponse = await authService.getCurrentUser();
            
            dispatch({
              type: 'AUTH_SUCCESS',
              payload: {
                user: userResponse.data,
                token: token
              }
            });
          } catch (error) {
            // Token might be expired, try refresh
            try {
              await refreshTokens();
            } catch (refreshError) {
              // Both tokens invalid, clear storage
              localStorage.removeItem('auth_token');
              localStorage.removeItem('refresh_token');
              authService.setAuthToken(null);
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
      } finally {
        dispatch({ type: 'SET_INITIALIZED' });
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const response = await authService.login(email, password);
      const { user, tokens } = response.data;
      
      // Store tokens securely
      setAuthTokens({
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token
      });
      
      // Set token in API service
      authService.setAuthToken(tokens.access_token);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: user,
          token: tokens.access_token
        }
      });
    } catch (error: any) {
      dispatch({ type: 'AUTH_FAILURE' });
      
      // Extract error message from response
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'Login failed';
      
      throw new Error(errorMessage);
    }
  };

  const register = async (userData: RegisterData): Promise<void> => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const response = await authService.register(userData);
      const { user, tokens } = response.data;
      
      // Store tokens securely
      setAuthTokens({
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token
      });
      
      // Set token in API service
      authService.setAuthToken(tokens.access_token);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: user,
          token: tokens.access_token
        }
      });
    } catch (error: any) {
      dispatch({ type: 'AUTH_FAILURE' });
      
      // Extract error message from response
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'Registration failed';
      
      throw new Error(errorMessage);
    }
  };

  const refreshTokens = async (): Promise<void> => {
    try {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await authService.refreshToken(refreshToken);
      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      // Update stored tokens securely
      setAuthTokens({
        access_token,
        refresh_token: newRefreshToken
      });
      
      // Set new token in API service
      authService.setAuthToken(access_token);
      
      // Update state with new token
      if (state.user) {
        dispatch({
          type: 'AUTH_SUCCESS',
          payload: {
            user: state.user,
            token: access_token
          }
        });
      }
    } catch (error) {
      // Refresh failed, logout user
      logout();
      throw error;
    }
  };

  const logout = (): void => {
    // Clear storage securely
    removeAuthTokens();
    
    // Clear API service token
    authService.setAuthToken(null);
    
    // Update state
    dispatch({ type: 'LOGOUT' });
    
    toast.success('Logged out successfully!');
  };

  const updateProfile = async (userData: Partial<User>): Promise<void> => {
    try {
      const response = await authService.updateProfile(userData);
      dispatch({ type: 'UPDATE_USER', payload: response.data });
      toast.success('Profile updated successfully!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Profile update failed';
      throw new Error(errorMessage);
    }
  };

  const refreshToken = async (): Promise<void> => {
    await refreshTokens();
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken,
    updateProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};