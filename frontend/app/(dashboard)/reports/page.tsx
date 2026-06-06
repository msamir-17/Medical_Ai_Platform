'use client';

import { useAllReports } from '@/features/reports/useReports';
import { ReportCard } from '@/components/report/ReportCard';
import { Loader2, FolderOpen } from 'lucide-react';

export default function ReportsPage() {
  const { data: reports, isLoading } = useAllReports();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="animate-spin text-[--color-primary-500]" size={40} />
      </div>
    );
  }

  return (
    <div className="space-y-6 md:space-y-8 pb-10 md:pb-0">
      {/* Header — responsive stacking */}
      <header className="flex flex-col sm:flex-row sm:justify-between sm:items-end gap-2">
        <div>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-[--color-text-primary]">Medical Vault</h1>
          <p className="text-[--color-text-secondary] font-medium text-sm md:text-base">Access and manage all your uploaded documents.</p>
        </div>
      </header>

      {reports?.length === 0 ? (
        /* Empty State */
        <div className="text-center py-12 md:py-20 bg-[--color-bg-secondary] rounded-2xl md:rounded-3xl border-2 border-dashed border-[--color-border]">
          <FolderOpen className="mx-auto text-[--color-text-muted] mb-4 opacity-50" size={40} />
          <p className="text-[--color-text-secondary] text-sm md:text-base">No reports found in your vault.</p>
        </div>
      ) : (
        /* Report Cards Grid — progressive columns with ultra-wide support */
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4 md:gap-6">
          {reports?.map((report: any) => (
            <ReportCard 
              key={report.id}
              id={report.id}
              filename={report.filename}
              date={report.created_at}
            />
          ))}
        </div>
      )}
    </div>
  );
}