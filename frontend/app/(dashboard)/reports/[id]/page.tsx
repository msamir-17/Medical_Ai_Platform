'use client';

import { useReport } from '@/features/reports/useReports';
import { useParams } from 'next/navigation';
import { Loader2, ArrowLeft, Activity, ShieldAlert, Pill, CheckCircle } from 'lucide-react';
import Link from 'next/link';

export default function ReportDetailPage() {

  const params = useParams();
  
  // Next.js [id] folder ke hisaab se params.id milega
  const reportId = params.id as string; 

  const { data: report, isLoading, error } = useReport(reportId);


  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <Loader2 className="animate-spin text-indigo-600" size={48} />
        <p className="text-slate-500 animate-pulse font-medium">Opening secure medical file...</p>
      </div>
    );
  }


    if (error || !report) {
    return (
      <div className="p-10 text-center">
        <h1 className="text-xl font-bold text-red-500">Report Not Found</h1>
        <p>Please go back to the vault and try again.</p>
      </div>
    );
  }


  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-20">
      {/* 1. Navigation */}
      <Link href="/reports" className="flex items-center gap-2 text-sm font-bold text-indigo-600 hover:gap-3 transition-all">
        <ArrowLeft size={16} /> Back to Vault
      </Link>

      {/* 2. Professional Header */}
      <header className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-black text-slate-900">{report.filename}</h1>
            <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-[10px] font-black uppercase tracking-tighter">
              {report.report_type || "General"}
            </span>
          </div>
          <p className="text-slate-500 text-sm font-medium">Processed on {new Date(report.created_at).toLocaleString()}</p>
        </div>
        <div className="px-6 py-3 bg-green-500 text-white rounded-2xl text-sm font-bold shadow-lg shadow-green-100 flex items-center gap-2">
          <CheckCircle size={18} /> AI Analysis Verified
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          
          {/* 3. NEW: Laboratory Values Grid */}
          <section className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
              <Pill className="text-indigo-500" size={20} /> Extracted Lab Markers
            </h2>
            
            {Object.keys(report.extracted_values).length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {Object.entries(report.extracted_values).map(([key, value]) => (
                  <div key={key} className="p-4 bg-slate-50 rounded-2xl border border-slate-100 hover:border-indigo-200 transition-colors">
                    <p className="text-[10px] font-black text-slate-400 uppercase mb-1">{key}</p>
                    <p className="text-lg font-mono font-bold text-indigo-600">{value as string}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-slate-400 italic bg-slate-50 p-4 rounded-xl text-center">
                No specific numerical markers detected in this document.
              </div>
            )}
          </section>

          {/* 4. Detected Entities Section (Keep your existing pills code here) */}
          <section className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-6">Medical Insights</h2>
              <div className="text-slate-400 text-sm font-mono leading-relaxed max-h-60 overflow-y-auto">
                {report.extracted_text}
              </div>
          </section>

        </div>

        {/* 5. Right Column: Risk Score (Polished) */}
        <aside className="space-y-8">
          <div className={`p-8 rounded-3xl text-white shadow-2xl transition-all ${
            report.risk_score ? 'bg-indigo-600 shadow-indigo-200' : 'bg-slate-400 opacity-60'
          }`}>
            <ShieldAlert size={40} className="mb-6 opacity-80" />
            <h3 className="text-xl font-bold mb-2">Health Risk Score</h3>
            <p className="text-indigo-100 text-xs leading-relaxed mb-6">
              {report.risk_score 
                ? "Based on your clinical markers, the AI predicts the following probability:" 
                : "Numerical data was insufficient to calculate a specific risk percentage."}
            </p>
            <div className="text-5xl font-black tracking-tighter">
              {report.risk_score !== null ? `${report.risk_score}%` : "--"}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );



}