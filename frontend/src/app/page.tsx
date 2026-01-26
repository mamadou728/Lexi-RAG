"use client";

import { useState, useRef, useEffect } from "react";
import Header from "@/components/layout/Header";
import ChatInterface from "@/components/features/chat/ChatInterface";
import DocumentViewer from "@/components/features/document/DocumentViewer";
import { User } from "@/lib/types";

export default function Home() {
  const [leftWidth, setLeftWidth] = useState(35); // Percentage
  const [isResizing, setIsResizing] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing || !containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // Constrain between 20% and 70%
      const constrainedWidth = Math.max(20, Math.min(70, newLeftWidth));
      setLeftWidth(constrainedWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing]);

  return (
    <main className="h-screen flex flex-col bg-white text-black overflow-hidden">
      <Header user={user} setUser={setUser} />

      {/* Main Content Grid */}
      <div ref={containerRef} className="flex-1 flex overflow-hidden">
        {/* Left Side: Chat */}
        <div 
          className="h-full border-r border-gray-300 flex-shrink-0"
          style={{ width: `${leftWidth}%` }}
        >
          <ChatInterface user={user} />
        </div>

        {/* Resizable Divider */}
        <div
          className="w-1 bg-gray-300 hover:bg-gray-400 cursor-col-resize flex-shrink-0 transition-colors relative group"
          onMouseDown={() => setIsResizing(true)}
        >
          <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-2 group-hover:w-3 transition-all" />
        </div>

        {/* Right Side: Document */}
        <div className="flex-1 h-full bg-gray-50 min-w-0">
          <DocumentViewer document={null} />
        </div>
      </div>
    </main>
  );
}