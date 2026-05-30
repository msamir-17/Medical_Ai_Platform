import api from '@/lib/api';
import { UserLogin, UserRegister, AuthResponse } from '@/types/index'; // We will define these next

export const authService = {
  // 1. Logic for Login
  login: async (data: UserLogin): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', data);
    return response.data;
  },

  // 2. Logic for Registration
  register: async (data: UserRegister) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  // 3. Logic for Verification
  // Return type change karke AuthResponse kar diya
  verifyEmail: async (token: string): Promise<AuthResponse> => {
    const response = await api.get(`/auth/verify-email/${token}`);
    return response.data;
  }
};