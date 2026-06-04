import React from 'react';
import { FileText, Calendar, ArrowRight , Trash2 ,Loader2  } from 'lucide-react';
import Link from 'next/link';
import { useDeleteReport } from '@/features/reports/useReports';

interface ReportCardProps {
  id: string;
  filename: string;
  date: string;
}

export function ReportCard({ id, filename, date }: ReportCardProps) {
  // Format the date into something readable
  const formattedDate = new Date(date).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  });

const deleteMutation = useDeleteReport();

const handleDelete = async (e: React.MouseEvent) => {
  e.preventDefault(); // Stop navigation to detail page
  if (confirm("Are you sure you want to delete this report?")) {
    deleteMutation.mutate(id);
  }
};

  return (
    <div className="relative bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-all group">
      <div className="flex items-start justify-between mb-4">
        <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
          <FileText size={20} />
        </div>
        <span className="text-[10px] font-bold text-slate-400 uppercase">Report</span>
      </div>
      
      <h3 className="font-bold text-slate-900 truncate mb-1" title={filename}>
        {filename}
      </h3>
      
      <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-4">
        <Calendar size={14} />
        <span>{formattedDate}</span>
      </div>

      <Link 
        href={`/reports/${id}`}
        className="w-full py-2 bg-slate-50 text-slate-600 rounded-lg text-xs font-bold flex items-center justify-center gap-2 group-hover:bg-indigo-600 group-hover:text-white transition-colors"
      >
        View Details <ArrowRight size={14} />
      </Link>
      <button 
        onClick={handleDelete}
        disabled={deleteMutation.isPending}
        className="absolute top-4 right-4 p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all z-10"
        title="Delete Report"
      >
      {deleteMutation.isPending ? (
          <Loader2 className="animate-spin" size={16} />
        ) : (
          <Trash2 size={16} />
        )}
      </button>
    </div>
  );
}