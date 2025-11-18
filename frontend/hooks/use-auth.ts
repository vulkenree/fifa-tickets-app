import useSWR from 'swr';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { User, LoginCredentials, RegisterCredentials } from '@/lib/types';

export function useAuth() {
  const router = useRouter();
  
  const { data: user, error, mutate } = useSWR<User>(
    typeof window !== 'undefined' && localStorage.getItem('token') ? '/api/auth/me' : null,
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

  return {
    user,
    isLoading: !error && !user,
    isError: error,
    login,
    register,
    logout,
  };
}
