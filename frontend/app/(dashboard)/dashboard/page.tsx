'use client';

import { useReportStats } from '@/features/reports/useReports';
import { FileText, Activity, Calendar, Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const { data, isLoading } = useReportStats();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="animate-spin text-indigo-600" size={48} />
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-3xl font-extrabold text-slate-900">Health Overview</h1>
        <p className="text-slate-500 font-medium">Real-time summary of your medical records.</p>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Total Reports */}
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4">
            <FileText size={24} />
          </div>
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">Total Reports</p>
          <h3 className="text-4xl font-black text-slate-900 mt-1">{data?.total_reports || 0}</h3>
        </div>

        {/* Card 2: Latest Upload */}
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-green-50 text-green-600 flex items-center justify-center mb-4">
            <Calendar size={24} />
          </div>
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">Last Activity</p>
          <h3 className="text-lg font-bold text-slate-900 mt-1 truncate">
            {data?.latest_filename || "N/A"}
          </h3>
        </div>

        {/* Card 3: System Status */}
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
            <Activity size={24} />
          </div>
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wider">AI Analysis</p>
          <h3 className="text-lg font-bold text-green-500 mt-1">Ready & Active</h3>
        </div>
      </div>
    </div>
  );
}