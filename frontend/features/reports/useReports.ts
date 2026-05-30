
'use client';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

export function useReportStats() {
  return useQuery({
    queryKey: ['report-stats'],
    queryFn: async () => {
      const response = await api.get('/reports/stats');
      return response.data;
    },
  });
}