'use client';
import React from 'react';
import { FileText, ArrowRight, Activity } from 'lucide-react';
import Link from 'next/link';

export function RecentReports({ reports }: { reports: any[] }) {
  if (!reports || reports.length === 0) return null;

  return (
    <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
      <div className="p-6 border-b border-slate-50 flex justify-between items-center">
        <h3 className="font-bold text-slate-900 text-lg">Recent Medical Records</h3>
        <Link href="/reports" className="text-xs font-bold text-indigo-600 hover:underline">View All</Link>
      </div>

      <div className="divide-y divide-slate-50">
        {reports.slice(0, 5).map((report) => (
          <div key={report.id} className="p-4 hover:bg-slate-50 transition-colors flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500">
                <FileText size={20} />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-900 truncate max-w-[200px] md:max-w-md">
                  {report.filename}
                </p>
                <p className="text-[10px] text-slate-400 font-medium uppercase">
                  {report.report_type || 'General Analysis'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              {/* Risk Status Badge */}
              <div className={`px-3 py-1 rounded-lg text-[10px] font-black uppercase ${
                report.risk_score 
                  ? 'bg-red-50 text-red-600' 
                  : 'bg-emerald-50 text-emerald-600'
              }`}>
                {report.risk_score ? `${report.risk_score}% Risk` : 'Stable'}
              </div>

              <Link href={`/reports/${report.id}`} className="text-slate-400 hover:text-indigo-600 transition-colors">
                <ArrowRight size={18} />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}