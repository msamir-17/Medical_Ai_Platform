'use client';

import React, { useState } from 'react';
import { Upload, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';
import { reportService } from '@/features/reports/reportService';
import { useRouter } from 'next/navigation';

export function UploadZone() {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [fileName, setFileName] = useState('');
  const [uploadedId, setUploadedId] = useState<string | null>(null);
  const router = useRouter();

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setStatus('uploading');

    try {
      const response = await reportService.upload(file);
      setUploadedId(response.id);
      setStatus('success');
    } catch (error) {
      console.error(error);
      setStatus('error');
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 sm:px-6">
      <div className={`
        relative border-2 border-dashed rounded-3xl transition-all duration-300
        ${status === 'uploading' 
          ? 'border-indigo-400 bg-indigo-50/50 shadow-lg shadow-indigo-100' 
          : 'border-slate-200 bg-slate-50/50 hover:border-slate-300 hover:bg-slate-50'
        }
        ${status === 'idle' ? 'cursor-pointer' : ''}
        p-6 sm:p-8 md:p-12 text-center
      `}>
        <input 
          type="file" 
          className={`absolute inset-0 w-full h-full opacity-0 z-50 ${status !== 'idle' ? 'hidden' : 'cursor-pointer'}`}
          onChange={handleFileUpload}
          accept=".pdf,.png,.jpg,.jpeg"
          disabled={status !== 'idle'}
        />

        <div className="flex flex-col items-center gap-4 sm:gap-6">
          {status === 'idle' && (
            <>
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gradient-to-br from-indigo-100 to-indigo-50 text-indigo-600 flex items-center justify-center shadow-md border border-indigo-100/50">
                <Upload size={32} className="sm:w-8 sm:h-8" strokeWidth={1.5} />
              </div>
              <div className="space-y-2">
                <p className="text-lg sm:text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
                  Drop your medical report
                </p>
                <p className="text-xs sm:text-sm text-slate-600 font-medium">
                  PDF, PNG, or JPG • Up to 10MB
                </p>
              </div>
            </>
          )}

          {status === 'uploading' && (
            <>
              <div className="relative">
                <div className="absolute inset-0 bg-indigo-200/20 rounded-full animate-pulse" />
                <Loader2 className="animate-spin text-indigo-600 relative z-10" size={48} strokeWidth={1.5} />
              </div>
              <div className="space-y-2 animate-in fade-in duration-300">
                <p className="text-base sm:text-lg md:text-xl font-bold text-slate-900 tracking-tight">
                  AI is reading your report
                </p>
                <p className="text-xs sm:text-sm text-slate-600 font-medium">
                  Extracting lab values and medical entities...
                </p>
              </div>
            </>
          )}

          {status === 'success' && (
            <div className="flex flex-col items-center space-y-4 sm:space-y-6 animate-in fade-in zoom-in duration-400 relative z-20">
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-br from-green-100 to-emerald-50 text-green-600 flex items-center justify-center shadow-md border border-green-100/50">
                <CheckCircle2 size={40} strokeWidth={1.5} />
              </div>
              <div className="space-y-1 text-center">
                <p className="text-lg sm:text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
                  Analysis Complete!
                </p>
                <p className="text-xs sm:text-sm text-slate-600 font-medium">
                  {fileName && `${fileName} • Ready to review`}
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row items-center gap-3 justify-center w-full relative z-30 pt-2">
                <button 
                  type="button"
                  onClick={(e) => { 
                    e.stopPropagation(); 
                    setStatus('idle'); 
                    setUploadedId(null); 
                  }}
                  className="w-full sm:w-auto h-12 px-6 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-semibold transition-all duration-200 border border-slate-200 hover:border-slate-300 pointer-events-auto active:scale-95"
                >
                  Upload Another
                </button>
                
                <button 
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (uploadedId) {
                      router.push(`/reports/${uploadedId}`);
                    }
                  }}
                  className="w-full sm:w-auto h-12 px-6 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold shadow-lg shadow-indigo-200 hover:shadow-indigo-300 flex items-center justify-center gap-2 whitespace-nowrap pointer-events-auto relative z-30 transition-all duration-200 active:scale-95"
                >
                  <span>View Report</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
