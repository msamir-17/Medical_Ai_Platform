'use client';

import React, { useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  Activity,
  ShieldCheck,
  BrainCircuit,
  FileSearch,
  MessageSquare,
  ArrowRight,
  Zap,
  ScanLine,
  Layers,
  Lock,
  Eye,
  Sparkles,
  BarChart3,
} from 'lucide-react';

/* ------------------------------------------------------------------ */
/*  Landing Page — Premium Clinical Design                            */
/*  Routes preserved: /login, /register                               */
/* ------------------------------------------------------------------ */

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-[#111827] antialiased selection:bg-indigo-100 selection:text-indigo-900">
      <Navbar />
      <HeroSection />
      <SocialProof />
      <PipelineSection />
      <ProblemSolutionSection />
      <CTASection />
      <Footer />

      {/* Keyframe animations + reduced-motion override */}
      <style>{`
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
        @keyframes float-medium {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-6px); }
        }
        @keyframes float-fast {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.15), 0 0 30px rgba(6, 182, 212, 0.08); }
          50% { box-shadow: 0 0 25px rgba(99, 102, 241, 0.25), 0 0 50px rgba(6, 182, 212, 0.15); }
        }
        @keyframes score-fill {
          from { stroke-dashoffset: 264; }
        }
        .animate-float-slow { animation: float-slow 6s ease-in-out infinite; }
        .animate-float-medium { animation: float-medium 4.5s ease-in-out infinite; }
        .animate-float-fast { animation: float-fast 5s ease-in-out infinite; }
        .animate-float-delayed { animation: float-slow 5.5s ease-in-out infinite 0.8s; }
        .animate-pulse-glow { animation: pulse-glow 3s ease-in-out infinite; }
        .animate-score-fill { animation: score-fill 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards; }

        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>
    </div>
  );
}

/* ================================================================== */
/*  NAVBAR                                                            */
/* ================================================================== */

function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-[#E5E7EB]">
      <nav className="mx-auto flex max-w-[1280px] items-center justify-between px-6 py-4 md:px-8 lg:px-12">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 group" aria-label="MediAI home">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#6366F1] text-white transition-transform duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] group-hover:scale-105">
            <Activity size={18} strokeWidth={2.5} />
          </div>
          <span className="text-xl font-semibold tracking-tight text-[#111827]">
            Medi<span className="text-[#6366F1]">AI</span>
          </span>
        </Link>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="hidden sm:inline-flex items-center px-4 py-2 text-sm font-medium text-[#6B7280] rounded-lg hover:text-[#111827] hover:bg-[#F9FAFB] transition-colors duration-150 ease-[cubic-bezier(0.4,0,0.2,1)]"
          >
            Sign in
          </Link>
          <Link
            href="/register"
            className="inline-flex items-center gap-1.5 rounded-lg bg-[#111827] px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-150 ease-[cubic-bezier(0.4,0,0.2,1)] hover:bg-[#1F2937] active:scale-[0.98]"
          >
            Get started
            <ArrowRight size={14} strokeWidth={2.5} />
          </Link>
        </div>
      </nav>
    </header>
  );
}

/* ================================================================== */
/*  HERO                                                              */
/* ================================================================== */

function HeroSection() {
  const heroRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = heroRef.current;
    if (!el) return;
    el.style.opacity = '0';
    el.style.transform = 'translateY(16px)';
    requestAnimationFrame(() => {
      el.style.transition = 'opacity 600ms cubic-bezier(0,0,0.2,1), transform 600ms cubic-bezier(0,0,0.2,1)';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
  }, []);

  return (
    <section ref={heroRef} className="relative overflow-hidden">
      {/* Gradient mesh background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-0 right-0 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-[#3B82F6]/8 via-[#06B6D4]/6 to-[#6366F1]/4 blur-3xl" />
        <div className="absolute bottom-0 left-0 h-[400px] w-[400px] rounded-full bg-gradient-to-tr from-[#06B6D4]/6 via-[#3B82F6]/4 to-transparent blur-3xl" />
      </div>

      {/* Subtle dot grid */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: 'radial-gradient(#3B82F6 1px, transparent 1px)',
          backgroundSize: '32px 32px',
        }}
      />

      <div className="relative mx-auto max-w-[1280px] px-6 pt-16 pb-20 md:px-8 md:pt-24 md:pb-28 lg:px-12 lg:pt-28 lg:pb-32">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-2 lg:items-center lg:gap-16">
          {/* Left: Copy */}
          <div className="max-w-xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#E0E7FF] bg-[#EEF2FF] px-3.5 py-1.5 text-xs font-semibold tracking-wide text-[#4338CA] uppercase">
              <ShieldCheck size={14} strokeWidth={2.5} />
              Clinical-grade intelligence
            </div>

            <h1 className="text-4xl font-bold leading-[1.15] tracking-tight text-[#111827] sm:text-5xl lg:text-[3.5rem]">
              Understand your medical reports{' '}
              <span className="bg-gradient-to-r from-[#3B82F6] via-[#6366F1] to-[#06B6D4] bg-clip-text text-transparent">
                with precision.
              </span>
            </h1>

            <p className="mt-6 max-w-lg text-base leading-relaxed text-[#6B7280] sm:text-lg">
              MediAI transforms unstructured medical PDFs into structured, actionable
              health intelligence — using Vision OCR, BioBERT NER, and explainable
              risk scoring.
            </p>

            <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                href="/register"
                className="group inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#6366F1] px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] hover:shadow-xl hover:shadow-blue-500/30 active:scale-[0.98]"
              >
                Create free account
                <ArrowRight
                  size={16}
                  strokeWidth={2.5}
                  className="transition-transform duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] group-hover:translate-x-0.5"
                />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-[#D1D5DB] bg-white px-6 py-3.5 text-sm font-medium text-[#111827] transition-all duration-150 ease-[cubic-bezier(0.4,0,0.2,1)] hover:bg-[#F9FAFB] hover:border-[#9CA3AF] active:scale-[0.98]"
              >
                Sign in
              </Link>
            </div>
          </div>

          {/* Right: Glassmorphism Dashboard Mockup */}
          <div className="relative flex justify-center lg:justify-end">
            <DashboardMockup />
          </div>
        </div>
      </div>
    </section>
  );
}

/* ================================================================== */
/*  GLASSMORPHISM DASHBOARD MOCKUP                                    */
/* ================================================================== */

function DashboardMockup() {
  return (
    <div className="relative w-full max-w-md lg:max-w-lg">
      {/* Ambient gradient glow behind dashboard */}
      <div className="absolute -inset-8 rounded-3xl bg-gradient-to-br from-[#3B82F6]/15 via-[#06B6D4]/10 to-[#6366F1]/12 blur-3xl" />

      {/* === Floating feature badges === */}
      <FloatingBadge
        label="Vision OCR"
        icon={<Eye size={12} strokeWidth={2.5} />}
        className="absolute -top-3 -left-4 sm:-left-8 z-20 animate-float-slow"
      />
      <FloatingBadge
        label="BioBERT NER"
        icon={<BrainCircuit size={12} strokeWidth={2.5} />}
        className="absolute top-16 -right-3 sm:-right-6 z-20 animate-float-medium"
      />
      <FloatingBadge
        label="Explainable AI"
        icon={<Sparkles size={12} strokeWidth={2.5} />}
        className="absolute bottom-24 -left-3 sm:-left-6 z-20 animate-float-fast"
      />
      <FloatingBadge
        label="Risk Scoring"
        icon={<BarChart3 size={12} strokeWidth={2.5} />}
        className="absolute -bottom-2 right-4 sm:right-8 z-20 animate-float-delayed"
      />

      {/* === Main glassmorphism card === */}
      <div className="animate-pulse-glow relative rounded-2xl border border-white/30 bg-white/70 p-5 shadow-2xl shadow-blue-900/10 backdrop-blur-xl sm:p-6">
        {/* Card header */}
        <div className="mb-5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#06B6D4] shadow-md shadow-cyan-500/20">
              <FileSearch size={16} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-[#111827]">Medical Report Analysis</p>
              <p className="text-xs text-[#9CA3AF]">blood_panel_2026.pdf</p>
            </div>
          </div>
          <span className="rounded-full border border-[#D1FAE5] bg-[#ECFDF5] px-2.5 py-1 text-xs font-semibold text-[#065F46]">
            Analyzed
          </span>
        </div>

        {/* Biomarker rows */}
        <div className="space-y-2.5">
          <BiomarkerRow label="Hemoglobin" value="14.2 g/dL" status="normal" statusLabel="Normal" />
          <BiomarkerRow label="Cholesterol" value="242 mg/dL" status="danger" statusLabel="High" />
          <BiomarkerRow label="Vitamin D" value="18 ng/mL" status="warning" statusLabel="Low" />
          <BiomarkerRow label="Glucose" value="94 mg/dL" status="normal" statusLabel="Normal" />
        </div>

        {/* Health Score circular indicator */}
        <div className="mt-5 flex items-center gap-5 rounded-xl border border-[#E5E7EB]/60 bg-gradient-to-br from-[#F0F9FF] to-[#F0FDFA] p-4">
          <HealthScoreRing score={82} />
          <div className="flex-1">
            <p className="text-sm font-semibold text-[#111827]">Overall Health Score</p>
            <p className="mt-0.5 text-xs leading-relaxed text-[#6B7280]">
              Based on 4 biomarkers analyzed. Cholesterol flagged for physician review.
            </p>
          </div>
        </div>

        {/* AI insight line */}
        <div className="mt-4 flex items-start gap-3 rounded-xl border border-[#E5E7EB]/40 bg-white/60 p-3 backdrop-blur-sm">
          <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-[#6366F1] to-[#3B82F6]">
            <MessageSquare size={11} className="text-white" />
          </div>
          <p className="text-xs leading-relaxed text-[#6B7280]">
            <span className="font-medium text-[#111827]">MediAI:</span>{' '}
            &ldquo;Elevated LDL cholesterol at 242 mg/dL — consider lipid panel follow-up with your
            physician.&rdquo;
          </p>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Floating badge component                                          */
/* ------------------------------------------------------------------ */

function FloatingBadge({
  label,
  icon,
  className = '',
}: {
  label: string;
  icon: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full border border-white/50 bg-white/80 px-3 py-1.5 text-xs font-medium text-[#111827] shadow-lg shadow-blue-900/8 backdrop-blur-md ${className}`}
    >
      <span className="text-[#6366F1]">{icon}</span>
      {label}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Biomarker row                                                     */
/* ------------------------------------------------------------------ */

function BiomarkerRow({
  label,
  value,
  status,
  statusLabel,
}: {
  label: string;
  value: string;
  status: 'normal' | 'warning' | 'danger';
  statusLabel: string;
}) {
  const config = {
    normal: {
      dot: 'bg-[#10B981]',
      badge: 'bg-[#ECFDF5] text-[#065F46] border-[#D1FAE5]',
    },
    warning: {
      dot: 'bg-[#F59E0B]',
      badge: 'bg-[#FFFBEB] text-[#92400E] border-[#FDE68A]',
    },
    danger: {
      dot: 'bg-[#EF4444]',
      badge: 'bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]',
    },
  }[status];

  return (
    <div className="flex items-center justify-between rounded-lg bg-white/80 px-4 py-2.5 border border-[#E5E7EB]/40 backdrop-blur-sm">
      <div className="flex items-center gap-2.5">
        <div className={`h-2 w-2 rounded-full ${config.dot}`} />
        <span className="text-sm text-[#374151]">{label}</span>
      </div>
      <div className="flex items-center gap-2.5">
        <span className="text-sm font-semibold text-[#111827] font-mono">{value}</span>
        <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${config.badge}`}>
          {statusLabel}
        </span>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Health score circular indicator (SVG)                             */
/* ------------------------------------------------------------------ */

function HealthScoreRing({ score }: { score: number }) {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex h-20 w-20 shrink-0 items-center justify-center">
      <svg className="h-20 w-20 -rotate-90" viewBox="0 0 96 96">
        {/* Track */}
        <circle cx="48" cy="48" r={radius} fill="none" stroke="#E5E7EB" strokeWidth="6" />
        {/* Fill arc */}
        <circle
          cx="48"
          cy="48"
          r={radius}
          fill="none"
          stroke="url(#scoreGradient)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="animate-score-fill"
          style={{ '--score-offset': offset } as React.CSSProperties}
        />
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="50%" stopColor="#06B6D4" />
            <stop offset="100%" stopColor="#10B981" />
          </linearGradient>
        </defs>
      </svg>
      {/* Score text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xl font-bold tracking-tight text-[#111827]">{score}</span>
        <span className="text-[9px] font-semibold uppercase tracking-wider text-[#9CA3AF]">/100</span>
      </div>
    </div>
  );
}

/* ================================================================== */
/*  SOCIAL PROOF BAR                                                  */
/* ================================================================== */

function SocialProof() {
  const stats = [
    { value: '99.2%', label: 'OCR Accuracy' },
    { value: '4-Layer', label: 'AI Pipeline' },
    { value: 'XGBoost', label: 'Risk Engine' },
    { value: 'Llama 3.1', label: 'Medical RAG' },
  ];

  return (
    <section className="border-y border-[#E5E7EB] bg-[#F9FAFB]">
      <div className="mx-auto max-w-[1280px] px-6 py-6 md:px-8 lg:px-12">
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-xl font-bold tracking-tight text-[#111827] sm:text-2xl">
                {stat.value}
              </p>
              <p className="mt-0.5 text-xs font-medium uppercase tracking-wider text-[#9CA3AF]">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ================================================================== */
/*  PIPELINE SECTION (Features)                                       */
/* ================================================================== */

function PipelineSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.style.transition = 'opacity 500ms cubic-bezier(0,0,0.2,1), transform 500ms cubic-bezier(0,0,0.2,1)';
          el.style.opacity = '1';
          el.style.transform = 'translateY(0)';
          observer.disconnect();
        }
      },
      { threshold: 0.15 }
    );

    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    observer.observe(el);

    return () => observer.disconnect();
  }, []);

  const steps = [
    {
      icon: <ScanLine size={20} strokeWidth={2} />,
      step: '01',
      title: 'Vision OCR',
      description:
        '150 DPI visual processing corrects broken character encodings and extracts structured lab values from complex medical PDFs.',
      color: '#F59E0B',
      bgColor: '#FFFBEB',
    },
    {
      icon: <BrainCircuit size={20} strokeWidth={2} />,
      step: '02',
      title: 'BioBERT NER',
      description:
        'Biomedical language model identifies medications, diseases, and symptoms with clinical-context awareness — not keyword matching.',
      color: '#6366F1',
      bgColor: '#EEF2FF',
    },
    {
      icon: <Layers size={20} strokeWidth={2} />,
      step: '03',
      title: 'SHAP Risk Scoring',
      description:
        'XGBoost classifiers produce explainable risk scores. SHAP values show exactly which markers contribute to clinical concern.',
      color: '#10B981',
      bgColor: '#ECFDF5',
    },
    {
      icon: <MessageSquare size={20} strokeWidth={2} />,
      step: '04',
      title: 'Grounded RAG',
      description:
        'Conversational agent retrieves answers strictly from your report context via FAISS embeddings — eliminating hallucination.',
      color: '#3B82F6',
      bgColor: '#EFF6FF',
    },
  ];

  return (
    <section ref={sectionRef} className="py-20 md:py-28 lg:py-32">
      <div className="mx-auto max-w-[1280px] px-6 md:px-8 lg:px-12">
        {/* Section header */}
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-wider text-[#6366F1]">
            Architecture
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-[#111827] sm:text-4xl">
            A four-layer clinical AI pipeline
          </h2>
          <p className="mt-4 text-base leading-relaxed text-[#6B7280]">
            Each layer is purpose-built to handle the unique challenges of medical document
            intelligence — from OCR noise to clinical context preservation.
          </p>
        </div>

        {/* Cards */}
        <div className="mt-16 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step) => (
            <PipelineCard key={step.step} {...step} />
          ))}
        </div>
      </div>
    </section>
  );
}

function PipelineCard({
  icon,
  step,
  title,
  description,
  color,
  bgColor,
}: {
  icon: React.ReactNode;
  step: string;
  title: string;
  description: string;
  color: string;
  bgColor: string;
}) {
  return (
    <div className="group rounded-2xl border border-[#E5E7EB] bg-white p-6 shadow-[0_1px_3px_rgba(0,0,0,0.06),0_1px_2px_rgba(0,0,0,0.04)] transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)] hover:-translate-y-px">
      <div className="flex items-center justify-between">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl transition-colors duration-200"
          style={{ backgroundColor: bgColor, color }}
        >
          {icon}
        </div>
        <span className="text-xs font-bold text-[#D1D5DB] tabular-nums">{step}</span>
      </div>
      <h3 className="mt-5 text-base font-semibold text-[#111827]">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-[#6B7280]">{description}</p>
    </div>
  );
}

/* ================================================================== */
/*  PROBLEM → SOLUTION SECTION (Razorpay ITCH)                       */
/* ================================================================== */

function ProblemSolutionSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.style.transition = 'opacity 500ms cubic-bezier(0,0,0.2,1), transform 500ms cubic-bezier(0,0,0.2,1)';
          el.style.opacity = '1';
          el.style.transform = 'translateY(0)';
          observer.disconnect();
        }
      },
      { threshold: 0.15 }
    );

    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    observer.observe(el);

    return () => observer.disconnect();
  }, []);

  const problems = [
    {
      title: 'Fragmented reports',
      detail: 'Patients receive multiple PDFs from different labs with inconsistent formats, encoding errors, and no unified view.',
    },
    {
      title: 'Opaque risk factors',
      detail: 'Standard blood work returns raw numbers without context. Patients cannot tell which values are clinically concerning.',
    },
    {
      title: 'Conflicting diagnoses',
      detail: 'Different specialists may flag different concerns from the same data. No single executive summary reconciles them.',
    },
  ];

  const solutions = [
    {
      title: 'Unified extraction',
      detail: 'Vision OCR + BioBERT normalize all report formats into a structured, searchable data layer.',
    },
    {
      title: 'Explainable scoring',
      detail: 'SHAP-powered XGBoost models quantify risk and attribute it to specific biomarkers.',
    },
    {
      title: 'AI executive summary',
      detail: 'Grounded RAG synthesizes insights from all your reports into one coherent, context-locked narrative.',
    },
  ];

  return (
    <section ref={sectionRef} className="border-t border-[#E5E7EB] bg-[#F9FAFB] py-20 md:py-28 lg:py-32">
      <div className="mx-auto max-w-[1280px] px-6 md:px-8 lg:px-12">
        {/* Section header */}
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-wider text-[#6366F1]">
            Why MediAI
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-[#111827] sm:text-4xl">
            The medical complexity problem
          </h2>
          <p className="mt-4 text-base leading-relaxed text-[#6B7280]">
            Medical data is high-dimensional, format-inconsistent, and clinically nuanced.
            Standard tools treat it like any other document — we don&apos;t.
          </p>
        </div>

        {/* Problem → Solution grid */}
        <div className="mt-16 grid grid-cols-1 gap-10 lg:grid-cols-2 lg:gap-16">
          {/* Problems */}
          <div>
            <div className="mb-6 flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-[#EF4444]" />
              <h3 className="text-sm font-semibold uppercase tracking-wider text-[#991B1B]">
                The challenge
              </h3>
            </div>
            <div className="space-y-4">
              {problems.map((p) => (
                <div
                  key={p.title}
                  className="rounded-2xl border border-[#E5E7EB] bg-white p-5 shadow-[0_1px_3px_rgba(0,0,0,0.06),0_1px_2px_rgba(0,0,0,0.04)]"
                >
                  <h4 className="text-sm font-semibold text-[#111827]">{p.title}</h4>
                  <p className="mt-1.5 text-sm leading-relaxed text-[#6B7280]">{p.detail}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Solutions */}
          <div>
            <div className="mb-6 flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-[#10B981]" />
              <h3 className="text-sm font-semibold uppercase tracking-wider text-[#065F46]">
                Our approach
              </h3>
            </div>
            <div className="space-y-4">
              {solutions.map((s) => (
                <div
                  key={s.title}
                  className="rounded-2xl border border-[#D1FAE5] bg-[#F0FDF4] p-5 shadow-[0_1px_3px_rgba(0,0,0,0.06),0_1px_2px_rgba(0,0,0,0.04)]"
                >
                  <h4 className="text-sm font-semibold text-[#111827]">{s.title}</h4>
                  <p className="mt-1.5 text-sm leading-relaxed text-[#6B7280]">{s.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ================================================================== */
/*  CTA SECTION                                                       */
/* ================================================================== */

function CTASection() {
  return (
    <section className="py-20 md:py-28 lg:py-32">
      <div className="mx-auto max-w-[1280px] px-6 md:px-8 lg:px-12">
        <div className="relative overflow-hidden rounded-2xl border border-[#E5E7EB] bg-[#111827] px-8 py-16 text-center shadow-2xl sm:px-16 sm:py-20">
          {/* Background dot pattern */}
          <div
            className="pointer-events-none absolute inset-0 opacity-[0.06]"
            style={{
              backgroundImage: 'radial-gradient(#6366F1 1px, transparent 1px)',
              backgroundSize: '24px 24px',
            }}
          />

          <div className="relative">
            <div className="mb-4 inline-flex items-center gap-1.5 rounded-full border border-[#3D4266] bg-[#1A1D27] px-3 py-1 text-xs font-medium text-[#818CF8]">
              <Lock size={12} strokeWidth={2.5} />
              Free tier available
            </div>
            <h2 className="mx-auto max-w-lg text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Start understanding your health data today.
            </h2>
            <p className="mx-auto mt-4 max-w-md text-base leading-relaxed text-[#9CA3AF]">
              Upload your first medical report and receive structured insights in under
              sixty seconds. No credit card required.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                href="/register"
                className="group inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#6366F1] px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition-all duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] hover:shadow-xl hover:shadow-blue-500/40 active:scale-[0.98]"
              >
                Create free account
                <ArrowRight
                  size={16}
                  strokeWidth={2.5}
                  className="transition-transform duration-200 ease-[cubic-bezier(0.4,0,0.2,1)] group-hover:translate-x-0.5"
                />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-[#3D4266] bg-transparent px-6 py-3.5 text-sm font-medium text-[#D1D5DB] transition-all duration-150 ease-[cubic-bezier(0.4,0,0.2,1)] hover:bg-[#1A1D27] hover:text-white active:scale-[0.98]"
              >
                Sign in to existing account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ================================================================== */
/*  FOOTER                                                            */
/* ================================================================== */

function Footer() {
  return (
    <footer className="border-t border-[#E5E7EB] bg-[#F9FAFB]">
      <div className="mx-auto max-w-[1280px] px-6 py-8 md:px-8 lg:px-12">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[#6366F1] text-white">
              <Activity size={14} strokeWidth={2.5} />
            </div>
            <span className="text-sm font-semibold text-[#111827]">MediAI</span>
          </div>
          <p className="text-sm text-[#9CA3AF]">
            &copy; {new Date().getFullYear()} MediAI Platform. Built for clinical-grade intelligence.
          </p>
        </div>
      </div>
    </footer>
  );
}