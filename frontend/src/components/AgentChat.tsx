"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User } from 'lucide-react';
import api from '../lib/api-client';

interface Message {
  role: 'user' | 'agent';
  content: string;
}

interface PredictionData {
  positions: number[];
  spacings: number[];
}

interface AgentChatProps {
  onResultsUpdate: (data: PredictionData) => void;
}

export default function AgentChat({ onResultsUpdate }: AgentChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'agent', content: 'Hello! I am Sentinel AI. How can I help you design your radar array today? You can say things like "Design an array with 0.15 degrees error" or "Reduce the error by 0.05".' }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState<string>(() => 
    typeof window !== 'undefined' ? Math.random().toString(36).substring(2, 15) : ''
  );

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.post('/chat', {
        message: userMessage,
        session_id: sessionId
      });
      
      setMessages(prev => [...prev, { role: 'agent', content: response.data.reply }]);
      
      if (response.data.data) {
        onResultsUpdate(response.data.data as PredictionData);
      }
    } catch {
      setMessages(prev => [...prev, { role: 'agent', content: 'Agent: Error connecting to the server.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel flex flex-col h-[400px]">
      <div className="p-4 border-b border-white/10 flex items-center gap-3">
        <Bot className="w-5 h-5 text-purple-400" />
        <h3 className="font-bold text-slate-200">Agentic Assistant</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl p-3 text-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 border border-slate-700 text-slate-300'}`}>
              <div className="flex items-center gap-2 mb-1 opacity-70">
                {msg.role === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                <span className="text-xs font-semibold">{msg.role === 'user' ? 'You' : 'Sentinel AI'}</span>
              </div>
              <div className="whitespace-pre-wrap">{msg.content.replace(/^Agent:\s*/, '')}</div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-3 text-sm flex gap-1">
              <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce"></span>
              <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-3 border-t border-white/10 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the agent to configure an array..."
          className="flex-1 glass-input rounded-lg px-4 py-2 text-sm"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          disabled={isLoading || !input.trim()}
          className="glass-button p-2 px-4 rounded-lg flex items-center justify-center disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
