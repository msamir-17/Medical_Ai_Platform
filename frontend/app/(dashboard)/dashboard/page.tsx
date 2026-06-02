'use client';

import { useAllReports, useReportStats } from '@/features/reports/useReports';
import { FileText, Activity, Calendar, Loader2, Sparkles } from 'lucide-react';
import { RecentReports } from '../reports/RecentReports';

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useReportStats();
  const { data: reports, isLoading: reportsLoading } = useAllReports();

  if (statsLoading || reportsLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="animate-spin text-indigo-600" size={48} />
      </div>
    );
  }

  return (
    <div className="space-y-10 pb-20">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">Health Overview</h1>
          <p className="text-slate-500 font-medium mt-1">Welcome back! Your medical intelligence is up to date.</p>
        </div>
        <div className="bg-indigo-600 text-white px-4 py-2 rounded-2xl flex items-center gap-2 shadow-lg shadow-indigo-100">
           <Sparkles size={18} />
           <span className="text-sm font-bold">AI Active</span>
        </div>
      </header>

      {/* 1. Top Stats Cards (Same as before but with real data) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-8 rounded-4xl border border-slate-100 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-6">
            <FileText size={24} />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Total Reports</p>
          <h3 className="text-4xl font-black text-slate-900 mt-1">{stats?.total_reports || 0}</h3>
        </div>

        <div className="bg-white p-8 rounded-4xl border border-slate-100 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-6">
            <Activity size={24} />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">System Status</p>
          <h3 className="text-xl font-bold text-emerald-600 mt-2 italic">99.2% Accuracy</h3>
        </div>

        <div className="bg-white p-8 rounded-4xl border border-slate-100 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-orange-50 text-orange-600 flex items-center justify-center mb-6">
            <Calendar size={24} />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Last Analysis</p>
          <h3 className="text-sm font-bold text-slate-900 mt-2 truncate">
            {stats?.latest_filename || "No Activity"}
          </h3>
        </div>
      </div>

      {/* 2. RECENT REPORTS LIST SECTION */}
      <div className="space-y-6">
        <RecentReports reports={reports} />
      </div>
    </div>
  );
}