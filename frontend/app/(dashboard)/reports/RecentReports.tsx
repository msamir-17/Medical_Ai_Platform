'use client';
import React from 'react';
import { FileText, ArrowRight } from 'lucide-react';
import Link from 'next/link';

// Cycle through brand colors for the file icons — gives the list visual life
const iconColors = [
  { bg: 'bg-indigo-100', text: 'text-indigo-600' },
  { bg: 'bg-emerald-100', text: 'text-emerald-600' },
  { bg: 'bg-amber-100',   text: 'text-amber-600'   },
  { bg: 'bg-blue-100',    text: 'text-blue-600'    },
  { bg: 'bg-violet-100',  text: 'text-violet-600'  },
];

export function RecentReports({ reports }: { reports: any[] }) {
  if (!reports || reports.length === 0) return null;

  return (
    <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">

      {/* ── Header ────────────────────────────────────── */}
      <div className="px-6 py-4 border-b border-slate-50 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-indigo-500" />
          <h3 className="font-black text-slate-900 text-lg">Recent Medical Records</h3>
        </div>
        <Link
          href="/reports"
          className="text-xs font-bold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-lg transition-colors duration-150"
        >
          View All →
        </Link>
      </div>

      {/* ── Report Rows ───────────────────────────────── */}
      <div className="divide-y divide-slate-50">
        {reports.slice(0, 5).map((report, idx) => {
          const color = iconColors[idx % iconColors.length];
          const hasRisk = report.risk_score && report.risk_score > 0;

          return (
            <div
              key={report.id}
              className="group px-4 md:px-6 py-3.5 hover:bg-slate-50 transition-colors duration-150 flex items-center justify-between gap-4"
            >
              {/* Left: Colored Icon + Info */}
              <div className="flex items-center gap-4 min-w-0">
                <div className={`w-10 h-10 rounded-xl ${color.bg} ${color.text} flex items-center justify-center shrink-0`}>
                  <FileText size={20} />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-bold text-slate-900 truncate max-w-[180px] sm:max-w-xs md:max-w-sm lg:max-w-md">
                    {report.filename}
                  </p>
                  <p className="text-[11px] text-slate-400 font-semibold uppercase tracking-wide mt-0.5">
                    {report.report_type || 'General Analysis'}
                  </p>
                </div>
              </div>

              {/* Right: Risk Badge + Arrow */}
              <div className="flex items-center gap-3 shrink-0">
                {/* Risk / Stable Badge */}
                <span className={`
                  px-3 py-1 rounded-full text-[11px] font-black uppercase tracking-wide whitespace-nowrap
                  ${hasRisk
                    ? 'bg-red-50 text-red-600 border border-red-100'
                    : 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                  }
                `}>
                  {hasRisk ? `${report.risk_score}% Risk` : '✓ Stable'}
                </span>

                {/* Arrow — colored on hover */}
                <Link
                  href={`/reports/${report.id}`}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-300 hover:text-indigo-600 hover:bg-indigo-50 transition-all duration-150"
                  aria-label={`Open ${report.filename}`}
                >
                  <ArrowRight size={16} />
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Footer ────────────────────────────────────── */}
      <div className="px-6 py-3 bg-slate-50 border-t border-slate-50">
        <p className="text-[11px] text-slate-400 font-medium">
          Showing {Math.min(5, reports.length)} of {reports.length} records
        </p>
      </div>
    </div>
  );
}