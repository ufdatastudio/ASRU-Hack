'use client';

interface ChatMessageProps {
  text: string;
  sender: 'user' | 'model' | 'ai' | 'system';
}

export default function ChatMessage({ text, sender }: ChatMessageProps) {
  const baseStyles = 'px-4 py-3 rounded-lg max-w-[85%] animate-in fade-in slide-in-from-bottom-2';
  
  const senderStyles = {
    user: 'bg-primary-600 text-white ml-auto rounded-br-sm',
    model: 'bg-dark-800 text-gray-100 mr-auto rounded-bl-sm border border-dark-700',
    ai: 'bg-dark-800 text-gray-100 mr-auto rounded-bl-sm border border-dark-700',
    system: 'bg-dark-900/50 text-gray-400 mx-auto rounded-full text-sm px-3 py-1.5 border border-dark-800',
  };

  return (
    <div className={`${baseStyles} ${senderStyles[sender]}`}>
      <p className="text-sm leading-relaxed whitespace-pre-wrap">{text}</p>
    </div>
  );
}

