'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { authService } from '@/features/auth/authService';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get('token');
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    if (token) {
      authService.verifyEmail(token)
        .then(() => setStatus('success'))
        .catch(() => setStatus('error'));
    }
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-xl p-10 text-center border border-slate-100">
        {status === 'loading' && (
          <>
            <Loader2 className="animate-spin text-indigo-600 mx-auto mb-4" size={48} />
            <h1 className="text-xl font-bold">Verifying your account...</h1>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle2 className="text-green-500 mx-auto mb-4" size={48} />
            <h1 className="text-xl font-bold mb-2">Account Verified!</h1>
            <p className="text-slate-500 mb-6">You can now sign in to your dashboard.</p>
            <button 
              onClick={() => router.push('/login')}
              className="w-full py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition-all"
            >
              Go to Login
            </button>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle className="text-red-500 mx-auto mb-4" size={48} />
            <h1 className="text-xl font-bold mb-2">Verification Failed</h1>
            <p className="text-slate-500 mb-6">The link is invalid or has expired.</p>
            <button 
              onClick={() => router.push('/register')}
              className="w-full py-3 bg-slate-800 text-white rounded-xl font-bold"
            >
              Try Registering Again
            </button>
          </>
        )}
      </div>
    </div>
  );
}