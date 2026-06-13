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
    <div className="max-w-2xl mx-auto mt-10">
      <div className={`
        relative border-2 border-dashed rounded-2xl p-12 text-center transition-all
        ${status === 'uploading' ? 'border-[--color-primary-500] bg-[--color-primary-50]' : 'border-[--color-border] bg-[--color-bg-secondary]'}
      `}>
        {/* 
          FIX 1: Added disabled state for success.
          FIX 2: Changed class pointer-events dynamically. When 'success', pointer-events-none ensures clicks pass straight through to buttons below.
        */}
        <input 
          type="file" 
          className={`absolute inset-0 w-full h-full opacity-0 z-50 ${status !== 'idle' ? 'hidden' : 'cursor-pointer'}
          `}
          onChange={handleFileUpload}
          accept=".pdf,.png,.jpg,.jpeg"
          disabled={status !== 'idle'}
        />

        <div className="flex flex-col items-center gap-6">
          {status === 'idle' && (
            <>
              <div className="w-16 h-16 rounded-2xl bg-indigo-100 text-indigo-600 flex items-center justify-center shadow-inner">
                <Upload size={32} />
              </div>
              <div>
                <p className="text-xl font-bold text-slate-900">Drop your medical report</p>
                <p className="text-sm text-slate-500 mt-1 font-medium">Support for PDF, PNG, or JPG (Max 10MB)</p>
              </div>
            </>
          )}

          {status === 'uploading' && (
            <>
              <Loader2 className="animate-spin text-indigo-600" size={48} />
              <div>
                <p className="text-lg font-bold text-slate-900">AI is reading your report...</p>
                <p className="text-sm text-slate-500 mt-1 font-medium italic">Extracting lab values and medical entities</p>
              </div>
            </>
          )}

          {status === 'success' && (
            <div className="flex flex-col items-center animate-in zoom-in duration-300 relative z-20">
              <div className="w-16 h-16 rounded-full bg-green-100 text-green-600 flex items-center justify-center mb-4">
                <CheckCircle2 size={32} />
              </div>
              <p className="text-xl font-bold text-slate-900 mb-8">Analysis Complete!</p>
              
              {/* Buttons Container */}
              <div className="flex flex-row items-center gap-4 justify-center w-full relative z-30">
                <button 
                  type="button"
                  onClick={(e) => { 
                    e.stopPropagation(); 
                    setStatus('idle'); 
                    setUploadedId(null); 
                  }}
                  className="h-11 px-6 bg-slate-100 text-slate-700 rounded-xl text-sm font-bold hover:bg-slate-200 transition-all border border-slate-200 pointer-events-auto"
                >
                  Upload Another
                </button>
                
                {/* FIX 3: Uncommented routing logic, forced higher z-index & explicit opacity styling */}
                <button 
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (uploadedId) {
                      router.push(`/reports/${uploadedId}`);
                    }
                  }}
                  className="h-11 px-6 bg-indigo-600 text-white rounded-xl text-sm font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-200 flex items-center justify-center gap-2 whitespace-nowrap min-w-[140px] pointer-events-auto relative z-30"
                >
                  <span className="text-white opacity-100">View Report</span>
                  <ArrowRight size={16} className="text-white" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
