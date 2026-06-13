'use client';

import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, Loader2, Link, ArrowRight } from 'lucide-react';
import { reportService } from '@/features/reports/reportService';

export function UploadZone() {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [fileName, setFileName] = useState('');
  const [uploadedId, setUploadedId] = useState<string | null>(null);

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
        <input 
          type="file" 
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          onChange={handleFileUpload}
          accept=".pdf,.png,.jpg,.jpeg"
          disabled={status === 'uploading'}
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
              <>
                <div className="w-16 h-16 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                  <CheckCircle2 size={32} />
                </div>
                <p className="text-lg font-bold text-slate-900">Analysis Complete!</p>
                <button 
                  onClick={(e) => { e.stopPropagation(); setStatus('idle'); }}
                  className="px-6 py-2 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-800 transition-all"
                >
                  Upload Another
                </button>
                <Link 
                    href={`/reports/${uploadedId}`}
                    className="px-6 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-100 flex items-center gap-2"
                  >
                    View Report <ArrowRight size={16} />
                </Link>

              </>
            )}
        </div>
      </div>
    </div>
  );
}