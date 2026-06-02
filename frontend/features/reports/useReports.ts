
'use client';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { reportService } from './reportService';
import { useMutation, useQueryClient } from '@tanstack/react-query';


export function useReportStats() {
  return useQuery({
    queryKey: ['report-stats'],
    queryFn: async () => {
      const response = await api.get('/reports/stats');
      return response.data;
    },
  });
}

export function useAllReports() {
  return useQuery({
    queryKey: ['all-reports'],
    queryFn: reportService.getAll,
  });
}

// Add this at the bottom
export function useReport(id: string) {
  return useQuery({
    queryKey: ['report', id],
    queryFn: () => reportService.getById(id),
    enabled: !!id && id !== 'undefined', 
  });
}


export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/reports/${id}`);
    },
    onSuccess: () => {
      // Refresh both 'all-reports' and 'report-stats' keys automatically!
      queryClient.invalidateQueries({ queryKey: ['all-reports'] });
      queryClient.invalidateQueries({ queryKey: ['report-stats'] });
    },
  });
}