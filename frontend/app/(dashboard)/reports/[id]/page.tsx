'use client';

import { useReport } from '@/features/reports/useReports';
import { useParams } from 'next/navigation';
import { Loader2, ArrowLeft, Activity, ShieldAlert, Pill, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { ShapBarChart } from '@/components/risk/ShapBarChart';

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
          

          {/* Patient Profile Card */}
          <section className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm overflow-hidden relative">
            {/* Background Decoration */}
            <div className="absolute top-0 right-0 p-4 opacity-5">
              <Activity size={120} />
            </div>

            <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest mb-6">Patient Identity</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
              {/* Col 1: Name & ID */}
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-slate-500 font-bold uppercase">Patient Name</p>
                  <p className="text-xl font-black text-indigo-600 uppercase italic">
                    {report.patient_info?.name || "Unknown"}
                  </p>
                </div>
                <div className="flex gap-10">
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase">Patient ID</p>
                    <p className="font-bold text-slate-900">{report.patient_info?.patient_id || "N/A"}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 font-bold uppercase">Gender</p>
                    <p className="font-bold text-slate-900">{report.patient_info?.gender || "N/A"}</p>
                  </div>
                </div>
              </div>

              {/* Col 2: Age & Doctor */}
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-slate-500 font-bold uppercase">Age</p>
                  <p className="text-lg font-bold text-slate-900">{report.patient_info?.age || "N/A"}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-bold uppercase">Referring Doctor</p>
                  <p className="font-bold text-slate-900">{report.patient_info?.doctor_name || "N/A"}</p>
                </div>
              </div>

              {/* Col 3: Hospital & Sample */}
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-slate-500 font-bold uppercase">Facility / Hospital</p>
                  <p className="font-bold text-slate-900">{report.patient_info?.hospital_name || "N/A"}</p>
                </div>
                <div className="p-3 bg-indigo-50 rounded-2xl inline-block">
                  <p className="text-[10px] text-indigo-400 font-black uppercase">Sample Source</p>
                  <p className="text-xs font-bold text-indigo-700">{report.patient_info?.sample_type || "N/A"}</p>
                </div>
              </div>
            </div>
          </section>


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
          {/* <section className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-6">Medical Insights</h2>
              <div className="text-slate-400 text-sm font-mono leading-relaxed max-h-60 overflow-y-auto">
                {report.extracted_text}
              </div>
          </section> */}

        </div>

        {/* 5. Right Column: Risk Score (Polished) */}
        <aside className="space-y-8">
          {/* Updated Risk Card logic */}
          <div className={`p-8 rounded-3xl text-white shadow-2xl transition-all ${
            report.risk_score 
              ? (report.risk_score > 50 ? 'bg-red-500 shadow-red-100' : 'bg-indigo-600 shadow-indigo-100') 
              : 'bg-emerald-500 shadow-emerald-100'
          }`}>
            <ShieldAlert size={40} className="mb-6 opacity-80" />
            <h3 className="text-xl font-bold mb-2">Clinical Status</h3>
            
            <p className="text-white/80 text-xs leading-relaxed mb-6">
              {report.risk_score 
                ? `AI has detected a ${report.risk_score}% probability of clinical concern.` 
                : "No critical abnormalities detected. Patient status appears stable."}
            </p>

            <div className="text-4xl font-black tracking-tighter">
              {report.risk_score !== null ? `${report.risk_score}%` : "STABLE"}
            </div>
          </div>

          {/* THE MAGIC CHART SECTION */}
          {report.shap_values && report.shap_values.length > 0 && (
            <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
              <h3 className="text-sm font-black text-slate-900 uppercase tracking-widest mb-2 text-center">
                Risk Factor Analysis
              </h3>
              <p className="text-[10px] text-slate-400 text-center mb-6 px-4">
                Red bars increase risk, Green bars decrease it.
              </p>
              
              {/* Hum wahi chart component use kar rahe hain jo humne pehle banaya tha */}
              <ShapBarChart data={report.shap_values} />
              
              <div className="mt-6 pt-6 border-t border-slate-50 text-[11px] text-slate-500 leading-relaxed italic">
                *This analysis is based on the Pima Indians Diabetes research model.
              </div>
            </div>
          )}

        </aside>
      </div>
    </div>
  );



}