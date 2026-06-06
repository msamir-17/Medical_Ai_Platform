'use client';

import { useReportStats, useAllReports } from '@/features/reports/useReports';
import { RecentReports } from '../reports/RecentReports';
import { Skeleton } from '@/components/ui/Skeleton';
import { FileText, Activity, Calendar, Sparkles, TrendingUp, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useReportStats();
  const { data: reports, isLoading: reportsLoading } = useAllReports();

  const isLoading = statsLoading || reportsLoading;

  return (
    <div className="space-y-8 pb-10 md:pb-20">

      {/* ── HERO HEADER ──────────────────────────────────────── */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 via-indigo-500 to-violet-600 p-6 md:p-8 text-white shadow-xl shadow-indigo-200">
        {/* Decorative orbs */}
        <div className="absolute -top-8 -right-8 w-40 h-40 rounded-full bg-white/10 blur-2xl" />
        <div className="absolute bottom-0 left-1/2 w-32 h-32 rounded-full bg-violet-400/20 blur-3xl" />

        <div className="relative flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-indigo-200 text-xs font-bold uppercase tracking-widest">AI System Active</span>
            </div>
            <h1 className="text-2xl md:text-3xl lg:text-4xl font-black tracking-tight">
              Health Overview
            </h1>
            <p className="text-indigo-200 font-medium mt-1 text-sm md:text-base">
              Welcome back! Your medical intelligence is up to date.
            </p>
          </div>

          <div className="flex gap-3 shrink-0">
            <Link
              href="/upload"
              className="bg-white text-indigo-600 px-4 py-2.5 rounded-xl text-xs font-black hover:bg-indigo-50 transition-colors duration-150 flex items-center gap-2 shadow-lg"
            >
              <TrendingUp size={14} /> Upload Report
            </Link>
            <Link
              href="/chat"
              className="bg-white/20 text-white border border-white/30 px-4 py-2.5 rounded-xl text-xs font-black hover:bg-white/30 transition-colors duration-150 flex items-center gap-2 backdrop-blur-sm"
            >
              <Sparkles size={14} /> Ask AI
            </Link>
          </div>
        </div>
      </div>

      {/* ── STAT CARDS ───────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
        {isLoading ? (
          [1, 2, 3].map((i) => <Skeleton key={i} className="h-40 rounded-3xl" />)
        ) : (
          <>
            {/* Card 1 — Total Reports  |  primary-500 gradient */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-500 to-indigo-700 p-6 text-white shadow-lg shadow-indigo-200 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200">
              <div className="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-white/10" />
              <div className="w-10 h-10 rounded-2xl bg-white/20 flex items-center justify-center mb-5">
                <FileText size={20} />
              </div>
              <p className="text-indigo-200 text-[10px] font-black uppercase tracking-widest">Total Reports</p>
              <div className="flex items-end justify-between mt-1">
                <h3 className="text-4xl font-black">{stats?.total_reports || 0}</h3>
                <ArrowUpRight size={20} className="text-indigo-300 mb-1" />
              </div>
            </div>

            {/* Card 2 — System Status  |  info/blue gradient */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-500 to-blue-700 p-6 text-white shadow-lg shadow-blue-200 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200">
              <div className="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-white/10" />
              <div className="w-10 h-10 rounded-2xl bg-white/20 flex items-center justify-center mb-5">
                <Activity size={20} />
              </div>
              <p className="text-blue-100 text-[10px] font-black uppercase tracking-widest">System Status</p>
              <div className="flex items-end justify-between mt-1">
                <h3 className="text-2xl md:text-3xl font-black">99.2%</h3>
                <span className="text-blue-200 text-xs font-bold mb-1">Accuracy</span>
              </div>
            </div>

            {/* Card 3 — Last Analysis  |  violet/purple gradient */}
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-violet-500 to-purple-700 p-6 text-white shadow-lg shadow-violet-200 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200 sm:col-span-2 lg:col-span-1">
              <div className="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-white/10" />
              <div className="w-10 h-10 rounded-2xl bg-white/20 flex items-center justify-center mb-5">
                <Calendar size={20} />
              </div>
              <p className="text-violet-100 text-[10px] font-black uppercase tracking-widest">Last Analysis</p>
              <div className="mt-1">
                <h3 className="text-sm font-black truncate leading-tight" title={stats?.latest_filename}>
                  {stats?.latest_filename || 'No Activity Yet'}
                </h3>
                <p className="text-violet-200 text-[10px] mt-1">Most recent upload</p>
              </div>
            </div>
          </>
        )}
      </div>

      {/* ── RECENT REPORTS ───────────────────────────────────── */}
      <div>
        {isLoading ? (
          <Skeleton className="h-64 w-full rounded-3xl" />
        ) : (
          <RecentReports reports={reports} />
        )}
      </div>

    </div>
  );
}