'use client';

import { useReport } from '@/features/reports/useReports';
import { useParams } from 'next/navigation';
import { Loader2, ArrowLeft, Activity, ShieldAlert, Pill } from 'lucide-react';
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
      {/* Navigation */}
      <Link href="/reports" className="flex items-center gap-2 text-sm font-bold text-indigo-600 hover:gap-3 transition-all">
        <ArrowLeft size={16} /> Back to Vault
      </Link>

      {/* Hero Header */}
      <header className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-black text-slate-900">{report.filename}</h1>
          <p className="text-slate-500 text-sm">Processed on {new Date(report.created_at).toLocaleString()}</p>
        </div>
        <div className="px-4 py-2 bg-green-50 text-green-600 rounded-xl text-sm font-bold">
          AI Analysis Complete
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Analysis Results */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Section 1: Detected Entities */}
          <section className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
            <h2 className="flex items-center gap-2 text-lg font-bold mb-6">
              <Activity className="text-red-500" /> Medical Entities Detected
            </h2>
            
            <div className="space-y-6">
              <div>
                <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-3">Diseases & Conditions</p>
                <div className="flex flex-wrap gap-2">
                  {report.detected_entities.diseases.map((d: string) => (
                    <span key={d} className="px-3 py-1.5 bg-red-50 text-red-700 rounded-lg text-xs font-bold border border-red-100">{d}</span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-3">Symptoms / Signs</p>
                <div className="flex flex-wrap gap-2">
                  {report.detected_entities.symptoms.map((s: string) => (
                    <span key={s} className="px-3 py-1.5 bg-amber-50 text-amber-700 rounded-lg text-xs font-bold border border-amber-100">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* Section 2: Raw Extracted Text */}
          <section className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl">
            <h2 className="text-white text-lg font-bold mb-4 opacity-90">Digital Text Version</h2>
            <div className="text-slate-400 text-sm font-mono leading-relaxed max-h-60 overflow-y-auto">
              {report.extracted_text}
            </div>
          </section>
        </div>

        {/* Right Column: Risk & Quick Stats */}
        <div className="space-y-8">
          <div className="bg-indigo-600 p-6 rounded-3xl text-white shadow-lg shadow-indigo-200">
            <ShieldAlert size={32} className="mb-4 opacity-80" />
            <h3 className="text-lg font-bold mb-1">Risk Assessment</h3>
            <p className="text-indigo-100 text-sm mb-4">Our AI models are calculating your specific risk scores based on this data.</p>
            <div className="text-3xl font-black italic opacity-50">SCORING...</div>
          </div>
        </div>
      </div>
    </div>
  );
}