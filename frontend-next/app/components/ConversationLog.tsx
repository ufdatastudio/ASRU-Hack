'use client';

import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'model' | 'system';
}

interface ConversationLogProps {
  messages: Message[];
}

export default function ConversationLog({ messages }: ConversationLogProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.length === 0 ? (
        <div className="h-full flex items-center justify-center">
          <p className="text-gray-500 text-sm italic">
            Start the conversation to see transcription and responses here.
          </p>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              text={message.text}
              sender={message.sender}
            />
          ))}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}

