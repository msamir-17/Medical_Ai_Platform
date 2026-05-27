'use client';

import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import { reportService } from '@/features/reports/reportService';

export function UploadZone() {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [fileName, setFileName] = useState('');

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setStatus('uploading');

    try {
      await reportService.upload(file);
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
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          onChange={handleFileUpload}
          accept=".pdf,.png,.jpg,.jpeg"
          disabled={status === 'uploading'}
        />

        <div className="flex flex-col items-center gap-4">
          {status === 'idle' && (
            <>
              <div className="p-4 rounded-full bg-[--color-primary-50] text-[--color-primary-500]">
                <Upload size={32} />
              </div>
              <div>
                <p className="text-lg font-semibold text-[--color-text-primary]">Click or drag report here</p>
                <p className="text-sm text-[--color-text-secondary]">PDF, PNG, or JPG (Max 10MB)</p>
              </div>
            </>
          )}

          {status === 'uploading' && (
            <>
              <Loader2 className="animate-spin text-[--color-primary-500]" size={40} />
              <p className="text-[--color-text-primary] font-medium">Analyzing {fileName}...</p>
              <p className="text-sm text-[--color-text-secondary]">Our AI is reading your medical data</p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircle2 className="text-[--color-success]" size={40} />
              <p className="text-[--color-text-primary] font-medium">Upload Complete!</p>
              <button 
                onClick={() => setStatus('idle')}
                className="text-sm text-[--color-primary-500] font-semibold hover:underline"
              >
                Upload another report
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}