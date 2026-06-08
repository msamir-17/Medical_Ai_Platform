'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2, Database, Sparkles } from 'lucide-react';
import { chatService } from '@/features/chat/chatService';
import { useAllReports } from '@/features/reports/useReports';

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

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      const data = await chatService.askQuestion(currentInput, selectedReportId);
      const aiMessage: Message = { role: 'ai', content: data.answer };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-3xl border border-slate-100 overflow-hidden shadow-xl">

      {/* ── TOP BAR ─────────────────────────────────── */}
      <div className="shrink-0 flex flex-col md:flex-row md:items-center md:justify-between gap-3 md:gap-4 px-4 md:px-5 py-3 bg-slate-50 border-b border-slate-100">
        {/* Left: Knowledge Base selector */}
        <div className="flex items-center gap-2.5 min-w-0">
          <Database size={15} className="text-slate-400 shrink-0" />
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest whitespace-nowrap">
            Knowledge Base:
          </span>
          <select
            className="bg-transparent border-none text-xs font-bold text-primary-600 outline-none cursor-pointer truncate"
            value={selectedReportId}
            onChange={(e) => setSelectedReportId(e.target.value)}
            aria-label="Select report for context"
          >
            <option value="">All Uploaded Reports</option>
            {reports?.map((report: any) => (
              <option key={report.id} value={report.id}>{report.filename}</option>
            ))}
          </select>
        </div>

        {/* Right: AI Status */}
        <div className="flex items-center gap-2 shrink-0">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest whitespace-nowrap">AI Online</span>
        </div>
      </div>

      {/* ── MESSAGE AREA ────────────────────────────── */}
      <div className="flex-1 min-h-0 overflow-y-auto p-5 md:p-6 space-y-5">

        {/* Empty State */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-slate-300 py-16">
            <div className="w-16 h-16 rounded-2xl bg-primary-50 flex items-center justify-center mb-4">
              <Bot className="text-primary-300" size={32} />
            </div>
            <p className="font-semibold text-slate-400 text-sm">
              Select a report or ask a general health question.
            </p>
            <p className="text-xs text-slate-300 mt-1">
              Powered by your medical records
            </p>
          </div>
        )}

        {/* Messages */}
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>

            {/* AI Avatar */}
            {msg.role === 'ai' && (
              <div className="w-8 h-8 rounded-xl bg-primary-100 flex items-center justify-center shrink-0 mt-0.5">
                <Sparkles size={14} className="text-primary-600" />
              </div>
            )}

            {/* Bubble
                USER  → primary-600 background, white text
                AI    → primary-50 background, text-primary text, primary-100 border
            */}
            <div className={`
              max-w-[80%] md:max-w-[72%]
              px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm
              ${msg.role === 'user'
                ? 'bg-primary-600 text-white rounded-br-sm'
                : 'bg-primary-50 text-slate-800 border border-primary-100 rounded-bl-sm'
              }
            `}>
              <p className="break-words">{msg.content}</p>
            </div>

            {/* User Avatar */}
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-primary-600 flex items-center justify-center shrink-0 mt-0.5">
                <span className="text-white font-black text-xs">U</span>
              </div>
            )}
          </div>
        ))}

        {/* Typing Indicator */}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-xl bg-primary-100 flex items-center justify-center shrink-0">
              <Sparkles size={14} className="text-primary-600" />
            </div>
            <div className="bg-primary-50 border border-primary-100 px-4 py-3 rounded-2xl rounded-bl-sm flex items-center gap-2">
              <Loader2 className="animate-spin text-primary-500" size={16} />
              <span className="text-xs text-slate-500 font-medium">Analyzing your records…</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── INPUT AREA ──────────────────────────────── */}
      <div className="shrink-0 p-4 bg-white border-t border-slate-100">
        <div className="flex gap-3 items-center bg-slate-50 rounded-2xl px-4 py-2 border border-slate-200 focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-500/10 transition-all duration-150">
          <input
            className="flex-1 bg-transparent border-none outline-none text-sm text-slate-800 placeholder:text-slate-400 py-2"
            placeholder="Type your medical query..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="
              p-2.5 bg-primary-600 text-white rounded-xl
              hover:bg-primary-700
              disabled:opacity-40 disabled:cursor-not-allowed
              transition-all duration-150
              shadow-md shadow-primary-200
              flex items-center justify-center shrink-0
              min-w-[40px] min-h-[40px]
            "
            aria-label="Send message"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-[10px] text-slate-300 text-center mt-2">
          Press Enter to send · AI responses may take a few seconds
        </p>
      </div>

    </div>
  );
}