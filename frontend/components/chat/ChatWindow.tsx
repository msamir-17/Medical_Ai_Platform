'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2, Database, Sparkles ,CheckCircle2} from 'lucide-react';
import { chatService } from '@/features/chat/chatService';
import { useAllReports } from '@/features/reports/useReports';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'ai';
  content: string;
}

export function ChatWindow() {
  const { data: reports } = useAllReports();
  const [selectedReportId, setSelectedReportId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [mode, setMode] = useState<'single' | 'compare' | 'overview'>('single');
  const [selectedIds, setSelectedIds] = useState<string[]>([]); // Ab ye List hogi

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Agar 'single' mode hai par koi report select nahi ki, toh error handle karein
    if (mode === 'single' && selectedIds.length === 0) {
      alert("Please select a report first");
      return;
    }

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      // Naya Service call (Passing mode and the list of IDs)
      const data = await chatService.askQuestion(currentInput, mode, selectedIds);
      const aiMessage: Message = { role: 'ai', content: data.answer };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleReportSelection = (id: string) => {
  setSelectedIds(prev => 
    prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
  );
};

  return (
  <div className="flex flex-col h-187.5 bg-white rounded-3xl border border-slate-100 overflow-hidden shadow-2xl shadow-slate-200/50">

    {/* ── TOP BAR: Mode & Knowledge Base ─────────────────────────── */}
    <div className="shrink-0 bg-slate-50 border-b border-slate-100 p-4 md:p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white rounded-xl shadow-sm border border-slate-100 text-indigo-600">
            <Database size={18} />
          </div>
          <div>
            <h3 className="text-sm font-black text-slate-900 uppercase tracking-tight">AI Analysis Engine</h3>
            <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Select your context below</p>
          </div>
        </div>

        {/* Mode Toggles */}
        <div className="flex bg-slate-200/60 p-1 rounded-xl">
          {(['single', 'compare', 'overview'] as const).map((m) => (
            <button
              key={m}
              onClick={() => { setMode(m); setSelectedIds([]); }}
              className={`px-4 py-1.5 text-[10px] font-black uppercase rounded-lg transition-all ${
                mode === m ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* DYNAMIC SELECTION AREA */}
      <div className="bg-white rounded-2xl border border-slate-200/60 p-1.5 shadow-inner">
        {mode === 'single' && (
          <select
            className="w-full bg-transparent border-none text-sm font-bold text-slate-700 outline-none cursor-pointer py-2 px-3"
            value={selectedIds[0] || ""}
            onChange={(e) => setSelectedIds([e.target.value])}
          >
            <option value="">Select a specific report to analyze...</option>
            {reports?.map((r: any) => (
              <option key={r.id} value={r.id}>{r.filename}</option>
            ))}
          </select>
        )}

        {mode === 'compare' && (
          <div className="p-2">
            <p className="text-[10px] font-black text-indigo-400 uppercase mb-3 px-1">Select reports to compare:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-32 overflow-y-auto pr-1 custom-scrollbar">
              {reports?.map((r: any) => (
                <label key={r.id} className={`flex items-center gap-3 p-2.5 rounded-xl border transition-all cursor-pointer group ${
                  selectedIds.includes(r.id) ? 'border-indigo-500 bg-indigo-50/50 ring-1 ring-indigo-500' : 'border-slate-100 hover:border-slate-300 bg-slate-50/30'
                }`}>
                  <div className={`w-4 h-4 rounded-md border flex items-center justify-center transition-all ${
                    selectedIds.includes(r.id) ? 'bg-indigo-600 border-indigo-600' : 'bg-white border-slate-300 group-hover:border-indigo-400'
                  }`}>
                    {selectedIds.includes(r.id) && <CheckCircle2 size={12} className="text-white" />}
                  </div>
                  <input 
                    type="checkbox" className="hidden" 
                    checked={selectedIds.includes(r.id)} 
                    onChange={() => toggleReportSelection(r.id)} 
                  />
                  <span className="text-xs font-bold text-slate-700 truncate">{r.filename}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {mode === 'overview' && (
          <div className="flex items-center gap-3 p-3 text-indigo-600">
            <Sparkles size={16} className="animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-tight">AI will synthesize all {reports?.length || 0} documents in your vault.</span>
          </div>
        )}
      </div>
    </div>

    {/* ── MESSAGE AREA ────────────────────────────── */}
    <div className="flex-1 min-h-0 overflow-y-auto p-5 md:p-8 space-y-8 bg-slate-50/30">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-center py-20">
          <div className="w-20 h-20 rounded-3xl bg-indigo-50 flex items-center justify-center mb-6 shadow-sm border border-indigo-100/50">
            <Bot className="text-indigo-400" size={40} />
          </div>
          <h2 className="text-xl font-black text-slate-900 tracking-tight">Clinical Assistant Ready</h2>
          <p className="text-sm text-slate-500 mt-2 max-w-xs mx-auto font-medium">
            Ask about diagnoses, trends, or specific values from your uploaded files.
          </p>
        </div>
      )}

      {messages.map((msg, i) => (
        <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          {msg.role === 'ai' && (
            <div className="w-9 h-9 rounded-xl bg-white shadow-sm border border-slate-100 flex items-center justify-center shrink-0 mt-1">
              <Sparkles size={18} className="text-indigo-600" />
            </div>
          )}

          <div className={`
            max-w-[85%] md:max-w-[75%]
            px-5 py-4 rounded-3xl text-sm leading-relaxed shadow-sm
            ${msg.role === 'user'
              ? 'bg-indigo-600 text-white rounded-tr-none'
              : 'bg-white text-slate-800 border border-slate-100 rounded-tl-none'
            }
          `}>
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>

          {msg.role === 'user' && (
            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center shrink-0 mt-1 shadow-lg shadow-indigo-200">
              <span className="text-white font-black text-xs italic">ME</span>
            </div>
          )}
        </div>
      ))}

      {isLoading && (
        <div className="flex gap-4 justify-start">
          <div className="w-9 h-9 rounded-xl bg-white shadow-sm border border-slate-100 flex items-center justify-center shrink-0">
            <Sparkles size={18} className="text-indigo-600 animate-spin-slow" />
          </div>
          <div className="bg-white border border-slate-100 px-5 py-4 rounded-3xl rounded-tl-none flex items-center gap-3">
            <Loader2 className="animate-spin text-indigo-500" size={18} />
            <span className="text-xs text-slate-400 font-black uppercase tracking-widest">AI Thinking...</span>
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>

    {/* ── INPUT AREA ──────────────────────────────── */}
    <div className="shrink-0 p-5 bg-white border-t border-slate-100">
      <div className="flex gap-3 items-center bg-slate-50 rounded-2xl px-4 py-2 border border-slate-200 focus-within:bg-white focus-within:border-indigo-400 focus-within:ring-4 focus-within:ring-indigo-500/5 transition-all duration-200 group">
        <input
          className="flex-1 bg-transparent border-none outline-none text-sm text-slate-800 placeholder:text-slate-400 py-3 font-medium"
          placeholder="Type your medical query here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="
            w-11 h-11 bg-indigo-600 text-white rounded-xl
            hover:bg-indigo-700 active:scale-95
            disabled:opacity-20 disabled:grayscale transition-all duration-200
            shadow-lg shadow-indigo-200 flex items-center justify-center shrink-0
          "
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  </div>

);}