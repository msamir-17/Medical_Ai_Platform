'use client';

import React, { useState } from 'react';
import { Send, Bot, Loader2, Database } from 'lucide-react';
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

  const handleSend = async () => {
    // Inside ChatWindow.tsx -> handleSend function:
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
    // 3. AB API CALL KAREIN (Sirf ek baar!)
    // Note: '123' ki jagah real ID use karenge jab Auth fully integrated ho
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
    <div className="flex flex-col h-150 border rounded-3xl bg-white overflow-hidden shadow-xl border-slate-100">
      
      {/* 1. TOP BAR: Report Selector */}
      <div className="p-3 bg-slate-50 border-b flex items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <Database size={16} className="text-slate-400" />
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Knowledge Base:</span>
          <select 
            className="bg-transparent border-none text-xs font-bold text-indigo-600 outline-none cursor-pointer focus:ring-0"
            value={selectedReportId}
            onChange={(e) => setSelectedReportId(e.target.value)}
          >
            <option value="">All Uploaded Reports</option>
            {reports?.map((report: any) => (
              <option key={report.id} value={report.id}>{report.filename}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-1.5">
           <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
           <span className="text-[10px] font-bold text-slate-400 uppercase">AI Online</span>
        </div>
      </div>

      {/* 2. MESSAGE AREA */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="text-center mt-20 text-slate-300">
            <Bot className="mx-auto mb-4 opacity-10" size={64} />
            <p className="font-medium">Select a report or ask a general health question.</p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : 'bg-slate-50 text-slate-800 border border-slate-100 rounded-tl-none'
            }`}>
              <p>{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
             <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 rounded-tl-none">
                <Loader2 className="animate-spin text-indigo-600" size={20} />
             </div>
          </div>
        )}
      </div>

      {/* 3. INPUT AREA */}
      <div className="p-4 bg-white border-t border-slate-100">
        <div className="flex gap-2">
          <input 
            className="flex-1 bg-slate-50 border-none rounded-2xl px-5 py-3 text-sm focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
            placeholder="Type your medical query..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button 
            onClick={handleSend}
            disabled={isLoading}
            className="p-4 bg-indigo-600 text-white rounded-2xl hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-lg shadow-indigo-100"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}