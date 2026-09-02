import React from 'react';
import { FileText, Calendar, ArrowRight, Trash2, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { useDeleteReport } from '@/features/reports/useReports';

interface ReportCardProps {
  id: string;
  filename: string;
  date: string;
}

export function ReportCard({ id, filename, date }: ReportCardProps) {
  const formattedDate = new Date(date).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  });

  const deleteMutation = useDeleteReport();

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (confirm("Are you sure you want to delete this report?")) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="
      group bg-white rounded-2xl border border-slate-200 shadow-sm
      hover:shadow-xl hover:border-indigo-200 hover:-translate-y-1
      transition-all duration-300 ease-out
      flex flex-col h-full
      overflow-hidden
    ">
      {/* Top Accent Bar */}
      <div className="h-1 bg-gradient-to-r from-indigo-400 to-indigo-600" />
      
      {/* Content Container */}
      <div className="flex-1 flex flex-col p-4 sm:p-5 gap-4">
        {/* Header Row: Icon + Badge */}
        <div className="flex items-start justify-between gap-3">
          <div className="w-11 h-11 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0 group-hover:bg-indigo-100 transition-colors duration-300">
            <FileText size={20} strokeWidth={2} />
          </div>
          <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest px-2.5 py-1 bg-slate-50 rounded-lg">
            Report
          </span>
        </div>

        {/* Filename - with tooltip on truncate */}
        <div className="flex-1 min-w-0">
          <h3 
            className="font-bold text-slate-900 text-sm sm:text-base leading-snug truncate group-hover:text-indigo-600 transition-colors duration-300" 
            title={filename}
          >
            {filename}
          </h3>
        </div>

        {/* Date + Delete Row */}
        <div className="flex items-center justify-between gap-2 mt-1">
          <div className="flex items-center gap-1.5 text-slate-500 text-xs font-medium">
            <Calendar size={14} className="text-slate-400" strokeWidth={2} />
            <span className="whitespace-nowrap">{formattedDate}</span>
          </div>
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-200 active:scale-95"
            title="Delete Report"
            aria-label={`Delete report ${filename}`}
          >
            {deleteMutation.isPending ? (
              <Loader2 className="animate-spin" size={16} strokeWidth={2} />
            ) : (
              <Trash2 size={16} strokeWidth={2} />
            )}
          </button>
        </div>
      </div>

      {/* Action Button */}
      <Link
        href={`/reports/${id}`}
        className="
          flex-shrink-0
          mx-4 mb-4 h-11 px-4 py-3
          rounded-xl text-xs sm:text-sm font-semibold
          flex items-center justify-center gap-2
          bg-indigo-50 text-indigo-600
          group-hover:bg-indigo-600 group-hover:text-white group-hover:shadow-lg group-hover:shadow-indigo-200
          transition-all duration-300 ease-out
          active:scale-95
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/30
        "
      >
        View Details <ArrowRight size={14} strokeWidth={2} />
      </Link>
    </div>
  );
}