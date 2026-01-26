"use client";

import { useState, useEffect } from "react";
import { User, UserRole } from "@/lib/types";


interface HeaderProps {
  user: User | null;
  setUser: (user: User | null) => void;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

export default function Header({ user, setUser }: HeaderProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Restore session on mount
  useEffect(() => {
    const token = localStorage.getItem("lexi_token");
    if (token && !user) {
      fetch("http://localhost:8000/auth/me", {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })
        .then((res) => {
          if (res.ok) {
            return res.json();
          }
          throw new Error("Token invalid");
        })
        .then((userData) => {
          setUser({
            username: userData.email,
            role: userData.system_role?.toLowerCase() || null,
          });
        })
        .catch(() => {
          localStorage.removeItem("lexi_token");
        });
    }
  }, [user, setUser]);

  const handleConnect = async () => {
    if (!username || !password) {
      setError("Please enter both username and password");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      // 2. Prepare Form Data (FastAPI requires x-www-form-urlencoded)
      const formData = new URLSearchParams();
      formData.append("username", username); // Map email/username input to 'username'
      formData.append("password", password);

      // 3. The Real Backend Call
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!response.ok) {
        // Try to get error message from response
        let errorMessage = "Invalid credentials";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }
    
      const data: AuthResponse = await response.json();

      // 4. Store the token (Minimalist persistence)
      localStorage.setItem("lexi_token", data.access_token);

      // Step 2: Fetch User Data using the Token
      const userResponse = await fetch("http://localhost:8000/auth/me", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${data.access_token}`,
          "Content-Type": "application/json",
        },
      });

      if (!userResponse.ok) {
        throw new Error("Failed to fetch user profile");
      }

      // Backend returns: { "email": "...", "system_role": "PARTNER", "full_name": "...", ... }
      const userData = await userResponse.json();

      // Step 3: Update State with REAL data from backend
      setUser({
        username: userData.email,
        role: userData.system_role?.toLowerCase() || null, // Map system_role to role
      });

      // Clear sensitive fields
      setPassword("");
      setUsername("");
      
    } catch (err) {
      // Handle different types of errors
      if (err instanceof TypeError && err.message.includes("fetch")) {
        setError("Cannot connect to server. Is the backend running?");
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Login failed. Please try again.");
      }
      console.error("Login error:", err);
    } finally {
      setIsLoading(false);
    }
  };


  const handleDisconnect = () => {
    localStorage.removeItem("lexi_token"); // Clear token
    setUser(null);
    setUsername("");
    setPassword("");
    setError("");
  };

  const isConnected = user !== null;

  return (
    <header className="h-16 border-b border-gray-300 bg-white flex items-center justify-between px-6 shadow-sm">
      {/* Logo */}
      <div className="font-bold text-xl tracking-tight text-gray-800">
        LEXI-RAG <span className="text-gray-400 text-sm font-normal">| Legal Workspace</span>
      </div>

      {/* Credentials Area */}
      <div className="flex items-center gap-4">
        {/* Status Indicator */}
        <div className="flex items-center gap-2 mr-4 border-r border-gray-300 pr-4">
          <span className="text-sm font-medium text-gray-600">Status:</span>
          <div
            className={`h-3 w-3 ${
              isConnected ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" : "bg-red-400"
            }`}
          ></div>
        </div>

        {isConnected ? (
          <div className="flex items-center gap-3">
            <div className="text-sm">
              <span className="font-medium text-gray-700">{user.username}</span>
              <span className="text-gray-500 ml-2 capitalize">({user.role})</span>
            </div>
            <button
              onClick={handleDisconnect}
              className="bg-gray-200 text-gray-700 px-4 py-1 text-sm font-medium hover:bg-gray-300 transition-colors"
            >
              Disconnect
            </button>
          </div>
        ) : (
          <div className="flex gap-2 items-center">
             {/* Show Error Message if exists */}
            {error && <span className="text-xs text-red-500 font-medium mr-2">{error}</span>}
            
            <input
              type="text"
              placeholder="Username"
              className="border border-gray-300 px-3 py-1 text-sm focus:outline-none focus:border-black w-32"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading}
            />
            <input
              type="password"
              placeholder="Password"
              className="border border-gray-300 px-3 py-1 text-sm focus:outline-none focus:border-black w-32"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleConnect();
              }}
            />
            <button
              onClick={handleConnect}
              disabled={isLoading}
              className={`bg-black text-white px-4 py-1 text-sm font-medium hover:bg-gray-800 transition-colors ${
                isLoading ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {isLoading ? "..." : "Connect"}
            </button>
          </div>
        )}
      </div>
    </header>
  );
}