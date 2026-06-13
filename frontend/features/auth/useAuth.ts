import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const response = await api.get('/auth/me');
      return response.data; // Returns { email: "...", id: "..." }
    },
  });
}