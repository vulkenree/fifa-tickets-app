import useSWR from 'swr';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { User, LoginCredentials, RegisterCredentials } from '@/lib/types';

export function useAuth() {
  const router = useRouter();
  
  const { data: user, error, mutate } = useSWR<User>(
    '/api/auth/me',
    () => authApi.me().then(res => res.data),
    {
      shouldRetryOnError: false,
      revalidateOnFocus: false,
    }
  );

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials);
      await mutate(response.data);
      router.push('/dashboard');
    } catch (error) {
      throw error;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    try {
      const response = await authApi.register(credentials);
      await mutate(response.data);
      router.push('/dashboard');
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
      await mutate(undefined, false);
      router.push('/login');
    } catch (error) {
      // Even if logout fails on server, clear local state
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
