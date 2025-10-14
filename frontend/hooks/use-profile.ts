'use client';

import { useState, useCallback } from 'react';
import useSWR, { mutate } from 'swr';
import { profileApi } from '@/lib/api';
import { User, ProfileUpdateData } from '@/lib/types';
import { toast } from 'sonner';

export function useProfile() {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: profile, isLoading, mutate: mutateProfile } = useSWR(
    '/api/profile',
    profileApi.getProfile,
    {
      revalidateOnFocus: false,
    }
  );

  const updateProfile = useCallback(
    async (data: ProfileUpdateData) => {
      setIsUpdating(true);
      setError(null);

      try {
        const response = await profileApi.updateProfile(data);
        mutateProfile(response.data, false); // Update local cache
        toast.success('Profile updated successfully!');
        return response.data;
      } catch (err: any) {
        console.error('Failed to update profile:', err);
        const errorMessage = err.response?.data?.error || err.message || 'Failed to update profile.';
        setError(errorMessage);
        toast.error(errorMessage);
        throw err;
      } finally {
        setIsUpdating(false);
      }
    },
    [mutateProfile]
  );

  return {
    profile,
    isLoading,
    isUpdating,
    error,
    updateProfile,
    refetch: mutateProfile,
  };
}
