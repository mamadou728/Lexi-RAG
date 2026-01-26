"use client";

import { useState, useEffect, useRef } from "react";
import { User, Message, Citation } from "@/lib/types";

interface ChatInterfaceProps {
  user: User | null;
}

function getWelcomeMessage(user: User | null): string {
  if (!user) {
    return "Hello, please log in to access the case assistant.";
  }

  switch (user.role) {
    case "partner":
      return `Hello ${user.username}, welcome back! As a partner, you have full access to all case documents, client communications, and strategic insights. How can I assist you with your case today?`;
    
    case "associate":
      return `Hello ${user.username}! As an associate, you can access case documents, research materials, and draft responses. What would you like to explore today?`;
    
    case "staff":
      return `Hello ${user.username}! As staff, you have access to administrative functions and case support. How can I help you today?`;
    
    case "client":
      return `Hello ${user.username}, thank you for using our legal services. As a client, you can view your case documents and ask questions about your matter. How can I help you today?`;
    
    default:
      return `Hello ${user.username}, welcome! How can I assist you today?`;
  }
}

export default function ChatInterface({ user }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 1. Initialize Session on Mount (when user is available)
  useEffect(() => {
    if (!user) {
      setMessages([]);
      setSessionId(null);
      setIsInitializing(false);
      return;
    }

    const initializeSession = async () => {
      try {
        const token = localStorage.getItem("lexi_token");
        if (!token) {
          setIsInitializing(false);
          return;
        }

        // Create a new session
        const response = await fetch("http://localhost:8000/chat/sessions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify({ name: "New Chat" }),
        });

        if (!response.ok) {
          throw new Error("Failed to create session");
        }

        const session = await response.json();
        setSessionId(session.id);

        // Add welcome message
        const welcomeMsg = getWelcomeMessage(user);
        setMessages([
          {
            role: "ai",
            content: welcomeMsg,
          },
        ]);
      } catch (error) {
        console.error("Error initializing session:", error);
        setMessages([
          {
            role: "ai",
            content: "⚠️ Sorry, I encountered an error connecting to the secure server.",
          },
        ]);
      } finally {
        setIsInitializing(false);
      }
    };

    initializeSession();
  }, [user]);

  // 2. Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !sessionId || !user) return;

    const userQuery = input;
    setInput("");
    setIsLoading(true);

    // Add User Message to UI immediately
    const newMessages = [...messages, { role: "user", content: userQuery } as Message];
    setMessages(newMessages);

    try {
      const token = localStorage.getItem("lexi_token");
      if (!token) {
        throw new Error("No authentication token");
      }

      // 3. Call the Backend (POST /chat)
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          query: userQuery,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch answer" }));
        throw new Error(errorData.detail || "Failed to fetch answer");
      }

      const data = await response.json();

      // 4. Add AI Response + Citations to UI
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content: data.answer,
          citations: data.sources || [], // Backend returns "sources" not "citations"
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content: `⚠️ Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const welcomeMessage = getWelcomeMessage(user);

  if (!user) {
    return (
      <div className="flex flex-col h-full bg-gray-50">
        <div className="p-4 border-b border-gray-200 bg-white">
          <h2 className="font-semibold text-gray-700">Case Assistant</h2>
          <p className="text-xs text-gray-500">Please log in to start chatting.</p>
        </div>
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          <div className="flex flex-col items-start">
            <div className="bg-white border border-gray-300 p-3 text-sm max-w-[90%] shadow-sm">
              {welcomeMessage}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <h2 className="font-semibold text-gray-700">Case Assistant</h2>
        <p className="text-xs text-gray-500">
          Ask questions about the open file. ({user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : "User"})
        </p>
      </div>

      {/* Messages Area (Scrollable) */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {isInitializing ? (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-500 rounded-lg p-4 animate-pulse">
              Initializing chat session...
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] ${
                    msg.role === "user"
                      ? "bg-black text-white"
                      : "bg-white border border-gray-200 text-gray-800"
                  } rounded-lg p-4 shadow-sm`}
                >
                  {/* Message Text */}
                  <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>

                  {/* --- CITATION CARDS (Only for AI) --- */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-100">
                      <p className="text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">
                        Sources Referenced:
                      </p>
                      <div className="grid grid-cols-1 gap-2">
                        {msg.citations.map((cite, cIdx) => (
                          <div
                            key={cIdx}
                            className="bg-blue-50 hover:bg-blue-100 transition-colors border border-blue-100 rounded p-2 cursor-pointer group"
                            onClick={() =>
                              alert(
                                `Opening Document: ${cite.filename}\nPage/Chunk: ${cite.chunk_index}`
                              )
                            }
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-semibold text-blue-800 truncate">
                                📄 {cite.filename}
                              </span>
                              <span className="text-[10px] bg-blue-200 text-blue-800 px-1.5 py-0.5 rounded">
                                Match: {Math.round(cite.score * 100)}%
                              </span>
                            </div>
                            <p className="text-xs text-gray-600 mt-1 line-clamp-2 italic">
                              "...{cite.text_snippet}..."
                            </p>
                            <div className="flex gap-2 mt-1">
                              <span className="text-[10px] text-gray-400">
                                Matter ID: {cite.matter_id.substring(0, 6)}...
                              </span>
                              <span className="text-[10px] text-gray-400 uppercase border border-gray-200 px-1 rounded">
                                {cite.sensitivity}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-500 rounded-lg p-4 animate-pulse">
                  Lexi is researching...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            className="flex-1 border border-gray-300 p-2 text-sm focus:outline-none focus:border-black rounded"
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={isLoading || isInitializing || !sessionId}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || isInitializing || !sessionId}
            className={`px-4 py-2 text-sm font-bold border border-gray-300 rounded transition-all ${
              isLoading || isInitializing || !sessionId
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-black text-white hover:bg-gray-800"
            }`}
          >
            SEND
          </button>
        </div>
      </div>
    </div>
  );
}
