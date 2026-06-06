'use client';

import { useReport } from '@/features/reports/useReports';
import { useParams } from 'next/navigation';
import { Loader2, ArrowLeft, Activity, ShieldAlert, Pill, CheckCircle ,Sparkles } from 'lucide-react';
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
        <Loader2 className="animate-spin text-[--color-primary-500]" size={40} />
        <p className="text-[--color-text-secondary] animate-pulse font-medium text-sm">Opening secure medical file...</p>
      </div>
    );
  }


    if (error || !report) {
    return (
      <div className="p-6 md:p-10 text-center">
        <h1 className="text-lg md:text-xl font-bold text-[--color-danger]">Report Not Found</h1>
        <p className="text-[--color-text-secondary] mt-2">Please go back to the vault and try again.</p>
      </div>
    );
  }


  return (
    <div className="space-y-6 md:space-y-8 pb-10 md:pb-20">
      {/* 1. Navigation */}
      <Link 
        href="/reports" 
        className="
          inline-flex items-center gap-2 text-sm font-bold text-[--color-primary-500] 
          hover:gap-3 transition-all duration-200
          focus-visible:ring-2 focus-visible:ring-[--color-primary-500]/30 focus-visible:outline-none
          rounded px-1 py-1
        "
      >
        <ArrowLeft size={16} /> Back to Vault
      </Link>

      {/* 2. Professional Header — responsive padding & stacking */}
      <header className="
        bg-[--color-bg-primary] p-5 md:p-8 rounded-2xl md:rounded-3xl 
        border border-[--color-border] shadow-sm 
        flex flex-col md:flex-row md:items-center justify-between gap-4
      ">
        <div className="min-w-0">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-2">
            <h1 className="text-lg md:text-xl lg:text-2xl font-bold text-[--color-text-primary] truncate">
              {report.filename}
            </h1>
            <span className="px-2.5 py-1 bg-[--color-primary-100] text-[--color-primary-700] rounded-full text-[11px] font-bold uppercase tracking-tight self-start sm:self-auto shrink-0">
              {report.report_type || "General"}
            </span>
          </div>
          <p className="text-[--color-text-secondary] text-sm font-medium">
            Processed on {new Date(report.created_at).toLocaleString()}
          </p>
        </div>
        <div className="
          px-4 md:px-6 py-2.5 md:py-3 
          bg-[--color-success] text-white rounded-xl md:rounded-2xl 
          text-sm font-bold shadow-lg shadow-emerald-100 
          flex items-center gap-2 
          self-start shrink-0
        ">
          <CheckCircle size={16} className="md:hidden" />
          <CheckCircle size={18} className="hidden md:block" />
          <span className="whitespace-nowrap">AI Verified</span>
        </div>
      </header>

      {/* 3. Content Grid — Right column (risk) shows FIRST on mobile via order */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8">

        {/* Right Column: Risk Score — appears first on mobile */}
        <aside className="space-y-6 md:space-y-8 order-first lg:order-last">
          {/* Risk Card */}
          <div className={`p-6 md:p-8 rounded-2xl md:rounded-3xl text-white shadow-xl transition-all duration-200 ${
            report.risk_score 
              ? (report.risk_score > 50 ? 'bg-[--color-danger] shadow-red-100' : 'bg-[--color-primary-600] shadow-indigo-100') 
              : 'bg-[--color-success] shadow-emerald-100'
          }`}>
            <ShieldAlert size={32} className="md:hidden mb-4 opacity-80" />
            <ShieldAlert size={40} className="hidden md:block mb-6 opacity-80" />
            <h3 className="text-lg md:text-xl font-bold mb-2">Clinical Status</h3>
            
            <p className="text-white/80 text-xs leading-relaxed mb-4 md:mb-6">
              {report.risk_score 
                ? `AI has detected a ${report.risk_score}% probability of clinical concern.` 
                : "No critical abnormalities detected. Patient status appears stable."}
            </p>

            <div className="text-3xl md:text-4xl font-bold tracking-tighter font-[family-name:var(--font-geist-mono)]">
              {report.risk_score !== null ? `${report.risk_score}%` : "STABLE"}
            </div>
          </div>

          {/* SHAP Chart Section */}
          {report.shap_values && report.shap_values.length > 0 && (
            <div className="bg-[--color-bg-primary] p-4 md:p-6 rounded-2xl md:rounded-3xl border border-[--color-border] shadow-sm">
              <h3 className="text-sm font-bold text-[--color-text-primary] uppercase tracking-widest mb-2 text-center">
                Risk Factor Analysis
              </h3>
              <p className="text-[11px] text-[--color-text-muted] text-center mb-4 md:mb-6 px-2 md:px-4">
                Red bars increase risk, Green bars decrease it.
              </p>
              
              {/* Hum wahi chart component use kar rahe hain jo humne pehle banaya tha */}
              <ShapBarChart data={report.shap_values} />
              
              <div className="mt-4 md:mt-6 pt-4 md:pt-6 border-t border-[--color-bg-tertiary] text-[11px] text-[--color-text-secondary] leading-relaxed italic">
                *This analysis is based on the Pima Indians Diabetes research model.
              </div>
            </div>
          )}
        </aside>

        {/* Left Column: Patient + Lab Results — takes 2/3 on desktop */}
        <div className="lg:col-span-2 space-y-6 md:space-y-8">
          

          {/* Patient Profile Card */}
          <section className="bg-[--color-bg-primary] p-5 md:p-8 rounded-2xl md:rounded-3xl border border-[--color-border] shadow-sm overflow-hidden relative">
            {/* Background Decoration */}
            <div className="absolute top-0 right-0 p-4 opacity-5 hidden md:block">
              <Activity size={120} />
            </div>

            <h2 className="text-sm font-bold text-[--color-text-muted] uppercase tracking-widest mb-4 md:mb-6">Patient Identity</h2>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-8 relative z-10">
              {/* Col 1: Name & ID */}
              <div className="space-y-3 md:space-y-4 col-span-2 md:col-span-1">
                <div>
                  <p className="text-[11px] text-[--color-text-secondary] font-bold uppercase">Patient Name</p>
                  <p className="text-base md:text-xl font-bold text-[--color-primary-500] uppercase">
                    {report.patient_info?.name || "Unknown"}
                  </p>
                </div>
                <div className="flex gap-6 md:gap-10">
                  <div>
                    <p className="text-[11px] text-[--color-text-secondary] font-bold uppercase">Patient ID</p>
                    <p className="font-bold text-[--color-text-primary] text-sm md:text-base">{report.patient_info?.patient_id || "N/A"}</p>
                  </div>
                  <div>
                    <p className="text-[11px] text-[--color-text-secondary] font-bold uppercase">Gender</p>
                    <p className="font-bold text-[--color-text-primary] text-sm md:text-base">{report.patient_info?.gender || "N/A"}</p>
                  </div>
                </div>
              </div>

              {/* Col 2: Age & Doctor */}
              <div className="space-y-3 md:space-y-4">
                <div>
                  <p className="text-[11px] text-[--color-text-secondary] font-bold uppercase">Age</p>
                  <p className="text-base md:text-lg font-bold text-[--color-text-primary]">{report.patient_info?.age || "N/A"}</p>
                </div>
                <div>
                  <p className="text-[11px] text-[--color-text-secondary] font-bold uppercase">Referring Doctor</p>
                  <p className="font-bold text-[--color-text-primary] text-sm md:text-base">{report.patient_info?.doctor_name || "N/A"}</p>
                </div>
              </div>

              {/* Col 3: Hospital & Sample */}
              <div className="space-y-3 md:space-y-4">
                <div>
                  <p className="text-[11px] text-[--color-text-secondary] font-bold uppercase">Facility / Hospital</p>
                  <p className="font-bold text-[--color-text-primary] text-sm md:text-base">{report.patient_info?.hospital_name || "N/A"}</p>
                </div>
                <div className="p-2.5 md:p-3 bg-[--color-primary-50] rounded-xl md:rounded-2xl inline-block">
                  <p className="text-[11px] text-[--color-primary-400] font-bold uppercase">Sample Source</p>
                  <p className="text-xs font-bold text-[--color-primary-700]">{report.patient_info?.sample_type || "N/A"}</p>
                </div>
              </div>
            </div>
          </section>


          {/* Lab Results Interpretation Grid */}
          <section className="bg-[--color-bg-primary] p-5 md:p-8 rounded-2xl md:rounded-3xl border border-[--color-border] shadow-sm">
            <h2 className="text-base md:text-lg font-bold text-[--color-text-primary] mb-4 md:mb-6 flex items-center gap-2">
              <Sparkles className="text-[--color-primary-500]" size={18} />
              <span>Lab Result Interpretation</span>
            </h2>
            
            {/* Horizontal scroll wrapper for mobile */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-6">
              {/* SAFETY: Check if extracted_values is a list before mapping */}
              {Array.isArray(report.extracted_values) ? (
                report.extracted_values.map((item: any) => (
                  <div key={item.marker} className="
                    p-3.5 md:p-5 bg-[--color-bg-secondary] rounded-xl md:rounded-2xl 
                    border border-[--color-border] 
                    relative overflow-hidden group 
                    hover:border-[--color-primary-200] transition-all duration-200
                  ">
                    <div className={`absolute left-0 top-0 bottom-0 w-1 md:w-1.5 ${
                      item.color === 'red' ? 'bg-[--color-danger]' : item.color === 'blue' ? 'bg-[--color-info]' : 'bg-[--color-success]'
                    }`} />
                    <div className="flex justify-between items-start mb-2 pl-2 md:pl-0">
                      <div className="min-w-0">
                        <p className="text-[11px] font-bold text-[--color-text-muted] uppercase tracking-tight truncate">{item.meaning}</p>
                        <h3 className="font-bold text-[--color-text-primary] text-sm md:text-base">{item.marker}</h3>
                      </div>
                      <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold uppercase whitespace-nowrap shrink-0 ml-2 ${
                        item.color === 'red' ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-600'
                      }`}>{item.status}</span>
                    </div>
                    <div className="flex items-baseline gap-1 pl-2 md:pl-0">
                      <span className="text-xl md:text-2xl font-bold text-[--color-primary-500] font-[family-name:var(--font-geist-mono)]">{item.value}</span>
                      <span className="text-[11px] font-bold text-[--color-text-muted]">{item.unit}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full text-center py-8 md:py-10 bg-[--color-bg-secondary] rounded-xl md:rounded-2xl border border-dashed border-[--color-border] text-[--color-text-muted] italic text-sm">
                  Old data format or no markers detected. Please re-upload for full analysis.
                </div>
              )}
            </div>
          </section>

          </div>
      </div>
    </div>
  );



}