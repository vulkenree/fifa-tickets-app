import useSWR from 'swr';
import { matchesApi } from '@/lib/api';
import { Match } from '@/lib/types';

export function useMatches() {
  const { data, error, mutate } = useSWR<Match[]>(
    '/api/matches',
    () => matchesApi.getAll().then(res => res.data)
  );

  const getMatchByNumber = async (matchNumber: string) => {
    try {
      const response = await matchesApi.getByNumber(matchNumber);
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  return {
    matches: data || [],
    isLoading: !error && !data,
    isError: error,
    getMatchByNumber,
    mutate,
  };
}
