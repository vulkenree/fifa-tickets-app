import axios from 'axios';
import { User, Ticket, Match, LoginCredentials, RegisterCredentials, TicketFormData, ChatMessage, ChatConversation, ChatResponse, ProfileUpdateData } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API
export const authApi = {
  login: (credentials: LoginCredentials) =>
    api.post<User>('/api/auth/login', credentials),
  logout: () => api.post('/api/auth/logout'),
  register: (credentials: RegisterCredentials) =>
    api.post<User>('/api/auth/register', credentials),
  me: () => api.get<User>('/api/auth/me'),
};

// Tickets API
export const ticketsApi = {
  getAll: () => api.get<Ticket[]>('/api/tickets'),
  getById: (id: number) => api.get<Ticket>(`/api/tickets/${id}`),
  create: (data: TicketFormData) => api.post<Ticket>('/api/tickets', data),
  update: (id: number, data: Partial<TicketFormData>) => api.put<Ticket>(`/api/tickets/${id}`, data),
  delete: (id: number) => api.delete(`/api/tickets/${id}`),
};

// Matches API
export const matchesApi = {
  getAll: () => api.get<Match[]>('/api/matches'),
  getByNumber: (matchNumber: string) => api.get<Match>(`/api/matches/${matchNumber}`),
};

// Chat API
export const chatApi = {
  sendMessage: (message: string, conversationId?: number) =>
    api.post<ChatResponse>('/api/chat/message', { message, conversation_id: conversationId }),
  getConversations: () => api.get<ChatConversation[]>('/api/chat/conversations'),
  getConversation: (conversationId: number) =>
    api.get<{ conversation: ChatConversation; messages: ChatMessage[] }>(`/api/chat/conversations/${conversationId}`),
  deleteConversation: (conversationId: number) =>
    api.delete(`/api/chat/conversations/${conversationId}`),
  saveConversation: (conversationId: number) =>
    api.post(`/api/chat/conversations/${conversationId}/save`),
  unsaveConversation: (conversationId: number) =>
    api.post(`/api/chat/conversations/${conversationId}/unsave`),
};

// Profile API
export const profileApi = {
  getProfile: () => api.get<User>('/api/profile'),
  updateProfile: (data: ProfileUpdateData) => api.put<User>('/api/profile', data),
};
