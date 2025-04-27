/**
 * Authentication service
 */
import { User, ApiResponse } from '../types';

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token';
const USER_DATA_KEY = 'user_data';

// API endpoint
const AUTH_URL = 'https://api.example.com/auth';

/**
 * Authentication service methods
 */
export const authService = {
  /**
   * Login with email and password
   * @param email - User email
   * @param password - User password
   * @returns Promise with authentication result
   */
  login: async (email: string, password: string): Promise<ApiResponse<{ user: User; token: string }>> => {
    try {
      const response = await fetch(`${AUTH_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      
      // Store token and user data
      localStorage.setItem(ACCESS_TOKEN_KEY, data.token);
      localStorage.setItem(USER_DATA_KEY, JSON.stringify(data.user));
      
      return {
        success: true,
        data: data,
      };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        data: null as unknown as { user: User; token: string },
        message: error instanceof Error ? error.message : 'Login failed',
      };
    }
  },

  /**
   * Register a new user
   * @param userData - User registration data
   * @returns Promise with registration result
   */
  register: async (userData: {
    username: string;
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
  }): Promise<ApiResponse<User>> => {
    try {
      const response = await fetch(`${AUTH_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      const data = await response.json();
      return {
        success: true,
        data: data.user,
      };
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        data: null as unknown as User,
        message: error instanceof Error ? error.message : 'Registration failed',
      };
    }
  },

  /**
   * Logout the current user
   */
  logout: (): void => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
    window.location.href = '/login';
  },

  /**
   * Get the current user token
   * @returns Current token or null
   */
  getToken: (): string | null => {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  /**
   * Get the current user data
   * @returns Current user or null
   */
  getCurrentUser: (): User | null => {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
  },

  /**
   * Check if a user is authenticated
   * @returns Boolean indicating authentication status
   */
  isAuthenticated: (): boolean => {
    return !!authService.getToken();
  },

  /**
   * Update the current user's profile
   * @param userData - Updated user data
   * @returns Promise with update result
   */
  updateProfile: async (userData: Partial<User>): Promise<ApiResponse<User>> => {
    try {
      const token = authService.getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const currentUser = authService.getCurrentUser();
      if (!currentUser) {
        throw new Error('User data not found');
      }

      const response = await fetch(`${AUTH_URL}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error('Profile update failed');
      }

      const data = await response.json();
      
      // Update stored user data
      localStorage.setItem(USER_DATA_KEY, JSON.stringify({
        ...currentUser,
        ...data.user,
      }));
      
      return {
        success: true,
        data: data.user,
      };
    } catch (error) {
      console.error('Profile update error:', error);
      return {
        success: false,
        data: null as unknown as User,
        message: error instanceof Error ? error.message : 'Profile update failed',
      };
    }
  },
}; 