export type UserRole = "associate" | "partner" | "client" | "staff" | null;

export interface User {
  username: string;
  role: UserRole;
}

export interface DocumentData {
  title: string;
  date: string;
  content: string;
}

export interface Citation {
  mongo_document_id: string;
  filename: string;
  matter_id: string;
  sensitivity: string;
  chunk_index: number;
  text_snippet: string;
  score: number;
}

export interface Message {
  id?: string;
  role: 'user' | 'ai';
  content: string;
  citations?: Citation[];
  created_at?: string;
}

export interface ChatSession {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}
