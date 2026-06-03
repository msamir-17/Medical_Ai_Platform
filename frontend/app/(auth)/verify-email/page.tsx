'use client';

import { useEffect, useState, Suspense } from 'react'; // 1. Suspense import karein
import { useSearchParams, useRouter } from 'next/navigation';
import { authService } from '@/features/auth/authService';
import { useAuthStore } from '@/store/authStore';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';

// Asli logic ko alag component mein rakhein
function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const setToken = useAuthStore((state) => state.setToken);
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    if (token) {
      authService.verifyEmail(token)
        .then((data) => {
          setToken(data.access_token);
          setStatus('success');
          setTimeout(() => router.push('/dashboard'), 2000);
        })
        .catch(() => setStatus('error'));
    }
  }, [token, setToken, router]);

  return (
    <div className="w-full max-w-md bg-white rounded-3xl shadow-xl p-10 text-center border border-slate-100">
      {status === 'loading' && (
        <div className="flex flex-col items-center">
          <Loader2 className="animate-spin text-indigo-600 mb-4" size={48} />
          <h1 className="text-xl font-bold text-slate-800">Verifying your account...</h1>
        </div>
      )}
      {status === 'success' && (
        <div className="flex flex-col items-center">
          <CheckCircle2 className="text-emerald-500 mb-4" size={48} />
          <h1 className="text-xl font-bold text-slate-800">Account Verified!</h1>
          <p className="text-slate-500 mt-2">Welcome to MediAI. Redirecting you...</p>
        </div>
      )}
      {status === 'error' && (
        <div className="flex flex-col items-center">
          <XCircle className="text-rose-500 mb-4" size={48} />
          <h1 className="text-xl font-bold text-slate-800">Verification Failed</h1>
          <p className="text-slate-500 mt-2">Invalid link. Please try registering again.</p>
        </div>
      )}
    </div>
  );
}

// Main page component jo Suspense boundary deta hai
export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <Suspense fallback={<Loader2 className="animate-spin text-indigo-600" size={48} />}>
        <VerifyEmailContent />
      </Suspense>
    </div>
  );
}