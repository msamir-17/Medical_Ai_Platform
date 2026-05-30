'use client';

import { useAllReports } from '@/features/reports/useReports';
import { ReportCard } from '@/components/report/ReportCard';
import { Loader2, FolderOpen } from 'lucide-react';

export default function ReportsPage() {
  const { data: reports, isLoading } = useAllReports();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="animate-spin text-indigo-600" size={48} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900">Medical Vault</h1>
          <p className="text-slate-500 font-medium">Access and manage all your uploaded documents.</p>
        </div>
      </header>

      {reports?.length === 0 ? (
        <div className="text-center py-20 bg-slate-50 rounded-3xl border-2 border-dashed">
          <FolderOpen className="mx-auto text-slate-300 mb-4" size={48} />
          <p className="text-slate-500">No reports found in your vault.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
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