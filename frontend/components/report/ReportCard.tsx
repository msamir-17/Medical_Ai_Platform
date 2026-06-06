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
      bg-white p-5 rounded-2xl border border-slate-100 shadow-sm 
      hover:shadow-lg hover:-translate-y-0.5
      transition-all duration-200 group
      flex flex-col
    ">
      {/* Top Row: Icon + Badge */}
      <div className="flex items-start justify-between mb-4">
        <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
          <FileText size={20} />
        </div>
        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Report</span>
      </div>

      {/* Filename */}
      <h3 className="font-bold text-slate-900 truncate mb-1 text-sm flex-1" title={filename}>
        {filename}
      </h3>

      {/* Date + Delete Row */}
      <div className="flex items-center justify-between mb-4 mt-2">
        <div className="flex items-center gap-1.5 text-slate-500 text-xs font-medium">
          <Calendar size={14} className="text-slate-400" />
          <span>{formattedDate}</span>
        </div>
        <button
          onClick={handleDelete}
          disabled={deleteMutation.isPending}
          className="p-1.5 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all duration-150"
          title="Delete Report"
          aria-label={`Delete report ${filename}`}
        >
          {deleteMutation.isPending ? (
            <Loader2 className="animate-spin" size={16} />
          ) : (
            <Trash2 size={16} />
          )}
        </button>
      </div>

      {/* View Details Button
          Base: indigo-50 bg with indigo-600 text
          Hover (via group): solid indigo-600 bg with white text
          — both states are fully visible and high-contrast */}
      <Link
        href={`/reports/${id}`}
        className="
          w-full py-2.5
          rounded-xl text-xs font-bold
          flex items-center justify-center gap-2
          bg-indigo-50 text-indigo-600
          group-hover:bg-indigo-600 group-hover:text-white
          transition-all duration-200
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/30
        "
      >
        View Details <ArrowRight size={14} />
      </Link>
    </div>
  );
}