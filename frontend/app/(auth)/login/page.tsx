'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/features/auth/authService';
import { useAuthStore } from '@/store/authStore';
import { Lock, Mail, Loader2, Activity } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const router = useRouter();
  const setToken = useAuthStore((state) => state.setToken);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const data = await authService.login({ email, password });
      setToken(data.access_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl shadow-indigo-100/50 p-10 border border-slate-100">
        
        {/* Logo & Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-indigo-600 text-white mb-4 shadow-lg shadow-indigo-200">
            <Activity size={28} />
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">MediAI Portal</h1>
          <p className="text-slate-500 mt-2 font-medium">Secure Patient Login</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 text-red-600 text-sm rounded-xl border border-red-100 font-medium">
              {error}
            </div>
          )}
          
          <div className="space-y-2">
            <label className="text-sm font-bold text-slate-700 ml-1">Email Address</label>
            <div className="relative group">
              <Mail className="absolute left-4 top-3.5 text-slate-400 group-focus-within:text-indigo-600 transition-colors" size={20} />
              <input 
                type="email" required 
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border-transparent rounded-2xl outline-none focus:bg-white focus:ring-2 focus:ring-indigo-600/20 focus:border-indigo-600 transition-all text-slate-900 placeholder:text-slate-400"
                placeholder="Enter your email"
                value={email} onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center ml-1">
              <label className="text-sm font-bold text-slate-700">Password</label>
              <button type="button" className="text-xs font-semibold text-indigo-600 hover:text-indigo-700">Forgot?</button>
            </div>
            <div className="relative group">
              <Lock className="absolute left-4 top-3.5 text-slate-400 group-focus-within:text-indigo-600 transition-colors" size={20} />
              <input 
                type="password" required 
                className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border-transparent rounded-2xl outline-none focus:bg-white focus:ring-2 focus:ring-indigo-600/20 focus:border-indigo-600 transition-all text-slate-900 placeholder:text-slate-400"
                placeholder="••••••••"
                value={password} onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {/* THE MISSING BUTTONS */}
          <button 
            type="submit" disabled={isLoading}
            className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 active:scale-[0.98] transition-all flex items-center justify-center gap-3 shadow-lg shadow-indigo-200 disabled:opacity-70"
          >
            {isLoading ? <Loader2 className="animate-spin" size={22} /> : 'Sign In to Dashboard'}
          </button>

          <div className="text-center pt-2">
            <p className="text-sm text-slate-500 font-medium">
              Don't have an account?{' '}
              <Link href="/register" className="text-indigo-600 font-bold hover:underline">
                Create Account
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}