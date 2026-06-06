'use client';

import React from 'react';
import Link from 'next/link';
import { Activity, ShieldCheck, BrainCircuit, FileSearch, MessageSquare, ArrowRight, Zap, CheckCircle2 } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-900">
      {/* 1. Header / Navbar */}
      <nav className="flex items-center justify-between px-6 py-6 max-w-7xl mx-auto border-b border-slate-50">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-600 rounded-xl text-white">
            <Activity size={24} />
          </div>
          <span className="text-2xl font-black tracking-tighter">MediAI</span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/login" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors">Sign In</Link>
          <Link href="/register" className="px-5 py-2.5 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-800 transition-all shadow-md">
            Get Started
          </Link>
        </div>
      </nav>

      {/* 2. Hero Section */}
      <main className="max-w-7xl mx-auto px-6 pt-20 pb-32">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-[10px] font-black uppercase tracking-widest mb-6">
              <ShieldCheck size={14} /> AI-Powered Health Security
            </div>
            <h1 className="text-5xl md:text-7xl font-black text-slate-900 leading-[1.1] tracking-tight mb-8">
              Understand your <span className="text-indigo-600">Medical Reports</span> like a Doctor.
            </h1>
            <p className="text-lg md:text-xl text-slate-500 font-medium leading-relaxed mb-10 max-w-2xl">
              MediAI uses clinical-grade Vision OCR and BioBERT to transform messy PDFs into 
              actionable health insights. Resolve conflicting diagnoses with our AI Executive Summary.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <Link href="/register" className="px-8 py-4 bg-indigo-600 text-white rounded-2xl font-bold flex items-center justify-center gap-2 shadow-xl shadow-indigo-200 hover:bg-indigo-700 transition-all hover:gap-4 text-lg">
                Create Free Account <ArrowRight size={20} />
              </Link>
            </div>
            
            <div className="flex items-center gap-8 text-slate-400">
              <div className="flex flex-col">
                <span className="text-slate-900 font-black text-xl">99.2%</span>
                <span className="text-xs uppercase font-bold tracking-tighter">OCR Accuracy</span>
              </div>
              <div className="w-px h-10 bg-slate-100"></div>
              <div className="flex flex-col">
                <span className="text-slate-900 font-black text-xl">XGBoost</span>
                <span className="text-xs uppercase font-bold tracking-tighter">Risk Engine</span>
              </div>
              <div className="w-px h-10 bg-slate-100"></div>
              <div className="flex flex-col">
                <span className="text-slate-900 font-black text-xl">Llama 3.1</span>
                <span className="text-xs uppercase font-bold tracking-tighter">Medical RAG</span>
              </div>
            </div>
          </div>

          {/* Abstract AI Visualization (Right Side) */}
          <div className="hidden lg:block relative">
            <div className="absolute inset-0 bg-indigo-500/10 blur-3xl rounded-full"></div>
            <div className="relative bg-white border border-slate-100 p-8 rounded-[3rem] shadow-2xl">
              <div className="space-y-4">
                <div className="flex items-center gap-4 p-4 bg-slate-50 rounded-2xl">
                  <div className="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center text-white"><CheckCircle2 size={20}/></div>
                  <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div className="w-[85%] h-full bg-emerald-500 animate-pulse"></div>
                  </div>
                </div>
                <div className="p-4 border-2 border-dashed border-indigo-100 rounded-2xl flex flex-col items-center gap-2 text-indigo-400">
                   <FileSearch size={32} className="opacity-50"/>
                   <span className="text-[10px] font-bold uppercase tracking-widest">Scanning Document...</span>
                </div>
                <div className="flex items-center gap-4 p-4 bg-indigo-600 rounded-2xl text-white">
                  <MessageSquare size={20}/>
                  <p className="text-xs font-medium italic">"Explain my triglycerides result in Hinglish..."</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 3. Features Section */}
      <section className="bg-slate-50 py-24 px-6 border-t border-slate-100">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-black text-slate-900 mb-4">A Four-Layer AI Pipeline</h2>
            <p className="text-slate-500 font-medium max-w-xl mx-auto italic">Engineered to solve the Razorpay ITCH high-severity medical complexity problem.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard 
              icon={<Zap className="text-amber-500" />}
              title="Vision OCR"
              desc="150 DPI visual processing to fix broken character encodings in messy PDFs."
            />
            <FeatureCard 
              icon={<BrainCircuit className="text-indigo-600" />}
              title="BioBERT NER"
              desc="Specialized NLP to identify medications, diseases, and symptoms in context."
            />
            <FeatureCard 
              icon={<ShieldCheck className="text-emerald-500" />}
              title="SHAP Risk"
              desc="Explainable risk scoring showing exactly why a marker indicates clinical concern."
            />
            <FeatureCard 
              icon={<MessageSquare className="text-blue-500" />}
              title="Grounded RAG"
              desc="Conversational agent locked to your report context to eliminate hallucinations."
            />
          </div>
        </div>
      </section>

      {/* 4. Footer */}
      <footer className="py-12 border-t border-slate-100 text-center">
        <p className="text-slate-400 text-sm font-medium">
          &copy; 2026 MediAI Platform. Built for Senior Engineering Portfolios.
        </p>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
  return (
    <div className="bg-white p-8 rounded-4xl border border-slate-100 hover:border-indigo-300 transition-all hover:shadow-xl hover:shadow-indigo-500/5 group">
      <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-indigo-50 transition-colors">
        {icon}
      </div>
      <h3 className="text-lg font-bold text-slate-900 mb-3">{title}</h3>
      <p className="text-slate-500 text-sm leading-relaxed font-medium">{desc}</p>
    </div>
  );
}