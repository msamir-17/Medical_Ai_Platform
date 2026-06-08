'use client';

import { useReport } from '@/features/reports/useReports';
import { useParams } from 'next/navigation';
import { Loader2, ArrowLeft, ShieldAlert, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { ShapBarChart } from '@/components/risk/ShapBarChart';

export default function ReportDetailPage() {

  const params = useParams();
  
  // Next.js [id] folder ke hisaab se params.id milega
  const reportId = params.id as string; 

  const { data: report, isLoading, error } = useReport(reportId);


  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 md:h-96 gap-4">
        <Loader2 className="animate-spin text-primary-500" size={40} />
        <p className="text-text-secondary animate-pulse font-medium text-sm">Opening medical file...</p>
      </div>
    );
  }


    if (error || !report) {
    return (
      <div className="p-6 md:p-10 text-center">
        <h1 className="text-lg md:text-xl font-bold text-danger">Report Not Found</h1>
        <p className="text-text-secondary mt-2">Please go back and try again.</p>
      </div>
    );
  }


  return (
    <div className="space-y-6 md:space-y-8 pb-10 md:pb-20">
      {/* 1. Navigation */}
      <Link 
        href="/reports" 
        className="inline-flex items-center gap-2 text-sm font-medium text-primary-500 hover:gap-3 transition-all duration-200 focus-visible:ring-2 focus-visible:ring-primary-500/30 focus-visible:outline-none rounded px-1 py-1"
      >
        <ArrowLeft size={16} /> Back
      </Link>

      {/* 2. Professional Header */}
      <header className="bg-bg-primary p-5 md:p-8 rounded-2xl md:rounded-3xl border border-border shadow-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-2">
            <h1 className="text-lg md:text-xl lg:text-2xl font-bold text-text-primary truncate">
              {report.filename}
            </h1>
            <span className="px-2.5 py-1 bg-primary-50 text-primary-700 rounded-full text-[11px] font-bold uppercase tracking-tight self-start sm:self-auto shrink-0">
              {report.report_type || "Report"}
            </span>
          </div>
          <p className="text-text-secondary text-sm font-medium">
            {new Date(report.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="px-4 md:px-6 py-2.5 md:py-3 bg-success text-white rounded-lg md:rounded-xl text-sm font-medium shadow-lg shadow-emerald-500/20 flex items-center gap-2 self-start shrink-0">
          <CheckCircle size={16} className="md:hidden" />
          <CheckCircle size={18} className="hidden md:block" />
          <span className="whitespace-nowrap">Verified</span>
        </div>
      </header>

      {/* 3. Content Grid — Right column (risk) shows FIRST on mobile via order */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">

        {/* Right Column: Risk Score */}
        <aside className="space-y-6 md:space-y-8 order-first lg:order-last">
          {/* Risk Card */}
          <div className={`p-6 md:p-8 rounded-2xl md:rounded-3xl text-white shadow-xl transition-all duration-200 ${
            report.risk_score 
              ? (report.risk_score > 50 ? 'bg-danger shadow-red-500/20' : 'bg-primary-600 shadow-primary-500/20') 
              : 'bg-success shadow-emerald-500/20'
          }`}>
            <ShieldAlert size={32} className="md:hidden mb-4 opacity-90" />
            <ShieldAlert size={40} className="hidden md:block mb-6 opacity-90" />
            <h3 className="text-lg md:text-xl font-bold mb-2">Clinical Status</h3>
            
            <p className="text-white/85 text-xs leading-relaxed mb-4 md:mb-6">
              {report.risk_score 
                ? `${report.risk_score}% probability of clinical concern` 
                : "No critical abnormalities detected"}
            </p>

            <div className="text-3xl md:text-4xl font-bold tracking-tighter font-mono">
              {report.risk_score !== null ? `${report.risk_score}%` : "STABLE"}
            </div>
          </div>

          {/* SHAP Chart Section */}
          {report.shap_values && report.shap_values.length > 0 && (
            <div className="bg-bg-primary p-4 md:p-6 rounded-2xl md:rounded-3xl border border-border shadow-card">
              <h3 className="text-sm font-bold text-text-primary uppercase tracking-widest mb-4 md:mb-6 text-center">
                Risk Factor Analysis
              </h3>
              <ShapBarChart data={report.shap_values} />
            </div>
          )}
        </aside>

        {/* Left Column: Patient + Lab Results — takes 2/3 on desktop */}
        <div className="lg:col-span-2 space-y-6 md:space-y-8">
          

          {/* Patient Profile Card */}
          <section className="bg-bg-primary p-5 md:p-8 rounded-2xl md:rounded-3xl border border-border shadow-card">
            <h2 className="text-sm font-bold text-text-secondary uppercase tracking-widest mb-4 md:mb-6">Patient Info</h2>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-8">
              {/* Col 1: Name & ID */}
              <div className="space-y-2 md:space-y-3 col-span-2 md:col-span-1">
                <div>
                  <p className="text-[11px] text-text-muted font-medium uppercase">Name</p>
                  <p className="text-base md:text-lg font-bold text-text-primary">
                    {report.patient_info?.name || "—"}
                  </p>
                </div>
                <div className="flex gap-4">
                  <div>
                    <p className="text-[11px] text-text-muted font-medium uppercase">ID</p>
                    <p className="font-semibold text-text-primary text-sm">{report.patient_info?.patient_id || "—"}</p>
                  </div>
                  <div>
                    <p className="text-[11px] text-text-muted font-medium uppercase">Gender</p>
                    <p className="font-semibold text-text-primary text-sm">{report.patient_info?.gender || "—"}</p>
                  </div>
                </div>
              </div>

              {/* Col 2: Age & Doctor */}
              <div className="space-y-2 md:space-y-3">
                <div>
                  <p className="text-[11px] text-text-muted font-medium uppercase">Age</p>
                  <p className="text-base md:text-lg font-bold text-text-primary">{report.patient_info?.age || "—"}</p>
                </div>
                <div>
                  <p className="text-[11px] text-text-muted font-medium uppercase">Referring Doctor</p>
                  <p className="font-semibold text-text-primary text-sm">{report.patient_info?.doctor_name || "—"}</p>
                </div>
              </div>

              {/* Col 3: Hospital & Sample */}
              <div className="space-y-2 md:space-y-3">
                <div>
                  <p className="text-[11px] text-text-muted font-medium uppercase">Facility</p>
                  <p className="font-semibold text-text-primary text-sm">{report.patient_info?.hospital_name || "—"}</p>
                </div>
                <div className="p-2.5 md:p-3 bg-primary-50 rounded-lg md:rounded-xl inline-block">
                  <p className="text-[10px] text-primary-600 font-medium uppercase">Sample</p>
                  <p className="text-[11px] font-semibold text-primary-700">{report.patient_info?.sample_type || "—"}</p>
                </div>
              </div>
            </div>
          </section>


          {/* Lab Results Interpretation Grid */}
          <section className="bg-bg-primary p-5 md:p-8 rounded-2xl md:rounded-3xl border border-border shadow-card">
            <h2 className="text-base md:text-lg font-bold text-text-primary mb-4 md:mb-6">Lab Results</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-6">
              {/* SAFETY: Check if extracted_values is a list before mapping */}
              {Array.isArray(report.extracted_values) ? (
                report.extracted_values.map((item: any) => (
                  <div key={item.marker} className="p-3.5 md:p-5 bg-bg-secondary rounded-xl md:rounded-2xl border border-border relative overflow-hidden group hover:border-primary-200 transition-all duration-200">
                    <div className={`absolute left-0 top-0 bottom-0 w-1 md:w-1.5 ${
                      item.color === 'red' ? 'bg-danger' : item.color === 'blue' ? 'bg-info' : 'bg-success'
                    }`} />
                    <div className="flex justify-between items-start mb-2 pl-2 md:pl-0">
                      <div className="min-w-0">
                        <p className="text-[11px] font-medium text-text-muted uppercase tracking-tight truncate">{item.meaning}</p>
                        <h3 className="font-bold text-text-primary text-sm md:text-base">{item.marker}</h3>
                      </div>
                      <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold uppercase whitespace-nowrap shrink-0 ml-2 ${
                        item.color === 'red' ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'
                      }`}>{item.status}</span>
                    </div>
                    <div className="flex items-baseline gap-1 pl-2 md:pl-0">
                      <span className="text-xl md:text-2xl font-bold text-primary-500 font-mono">{item.value}</span>
                      <span className="text-[11px] font-medium text-text-muted">{item.unit}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full text-center py-8 md:py-10 bg-bg-secondary rounded-xl md:rounded-2xl border border-dashed border-border text-text-muted text-sm">
                  No lab data available
                </div>
              )}
            </div>
          </section>

          </div>
      </div>
    </div>
  );



}