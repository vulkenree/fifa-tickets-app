export interface User {
  id: number;
  username: string;
}

export interface Ticket {
  id: number;
  user_id: number;
  username: string;
  name: string;
  match_number: string;
  date: string;
  venue: string;
  ticket_category: string;
  quantity: number;
  ticket_info?: string;
  ticket_price?: number;
}

export interface Match {
  match_number: string;
  date: string;
  venue: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  password: string;
}

export interface TicketFormData {
  name: string;
  match_number: string;
  date: string;
  venue: string;
  ticket_category: string;
  quantity: number;
  ticket_info?: string;
  ticket_price?: number | undefined;
}

export interface ChatMessage {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface ChatConversation {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  is_saved: boolean;
  message_count: number;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  function_called?: string;
  function_result?: any;
  error: boolean;
}
