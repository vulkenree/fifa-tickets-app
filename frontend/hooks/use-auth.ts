import useSWR from 'swr';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { User, LoginCredentials, RegisterCredentials } from '@/lib/types';

export function useAuth() {
  const router = useRouter();
  
  // Check if token exists
  const hasToken = typeof window !== 'undefined' && localStorage.getItem('token');
  
  const { data: user, error, isLoading: swrLoading, mutate } = useSWR<User>(
    hasToken ? '/api/auth/me' : null,
    () => authApi.me().then(res => res.data),
    {
      shouldRetryOnError: false,
      revalidateOnFocus: false,
    }
  );

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials);
      // Store token in localStorage
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
      }
      await mutate(response.data.user);
      router.push('/dashboard');
    } catch (error) {
      throw error;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    try {
      const response = await authApi.register(credentials);
      // Store token in localStorage
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
      }
      await mutate(response.data.user);
      router.push('/dashboard');
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Ignore errors on logout
    } finally {
      // Clear token from localStorage
      localStorage.removeItem('token');
      await mutate(undefined, false);
      router.push('/login');
    }
  };

  // Only show loading if we have a token and SWR is loading
  // If no token, we're not loading (user is not authenticated)
  const isLoading = hasToken ? swrLoading : false;

  return {
    user,
    isLoading,
    isError: error,
    login,
    register,
    logout,
  };
}
