import { ChatWindow } from '@/components/chat/ChatWindow';

export default function ChatPage() {
  return (
    <div className="
      flex flex-col 
      h-[calc(100vh-72px)] md:h-[calc(100vh-48px)]
    ">
      {/* Header — compact on mobile */}
      <header className="shrink-0 mb-3 md:mb-5">
        <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-[--color-text-primary]">
          AI Medical Assistant
        </h1>
        <p className="text-[--color-text-secondary] text-sm md:text-base">
          Discuss your reports and get instant explanations.
        </p>
      </header>

      {/* Chat Window — fills all remaining vertical space */}
      <div className="flex-1 min-h-0">
        <ChatWindow />
      </div>
    </div>
  );
}