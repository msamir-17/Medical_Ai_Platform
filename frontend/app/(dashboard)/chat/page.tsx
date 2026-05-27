import { ChatWindow } from '@/components/chat/ChatWindow';

export default function ChatPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-[--color-text-primary]">AI Medical Assistant</h1>
        <p className="text-[--color-text-secondary]">Discuss your reports and get instant explanations.</p>
      </header>

      <ChatWindow />
    </div>
  );
}