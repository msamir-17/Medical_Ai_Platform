'use client';

import React, { useState } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { chatService } from '@/features/chat/chatService';

interface Message {
  role: 'user' | 'ai';
  content: string;
}

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const data = await chatService.askQuestion(input);
      const aiMessage: Message = { role: 'ai', content: data.answer };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-150 border rounded-2xl bg-[--color-bg-secondary] overflow-hidden">
      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center mt-20 text-[--color-text-secondary]">
            <Bot className="mx-auto mb-4 opacity-20" size={48} />
            <p>Ask anything about your uploaded reports.</p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl flex gap-3 ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white ml-auto' // ml-auto will push it to the right
                : 'bg-gray-100 text-gray-800'
            }`}>
              {msg.role === 'ai' && <Bot size={20} className="mt-1 text-[--color-primary-500]" />}
              <p className="text-sm leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && <Loader2 className="animate-spin text-[--color-primary-500] mx-auto" />}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-[--color-bg-primary] border-t">
        <div className="flex gap-2">
          <input 
            className="flex-1 bg-[--color-bg-tertiary] border-none rounded-xl px-4 py-2 focus:ring-2 focus:ring-[--color-primary-500] outline-none"
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button 
            onClick={handleSend}
            disabled={isLoading}
            className="p-3 bg-[--color-primary-500] text-white rounded-xl hover:opacity-90 disabled:opacity-50 transition-all"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}