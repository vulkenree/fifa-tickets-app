import axios from 'axios';
import { User, Ticket, Match, LoginCredentials, RegisterCredentials, TicketFormData, ChatMessage, ChatConversation, ChatResponse, ProfileUpdateData, Venue } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to all requests
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (token expired or invalid)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (credentials: LoginCredentials) =>
    api.post<{ token: string; user: User }>('/api/auth/login', credentials),
  logout: () => api.post('/api/auth/logout'),
  register: (credentials: RegisterCredentials) =>
    api.post<{ token: string; user: User }>('/api/auth/register', credentials),
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

// Venues API
export const venuesApi = {
  getVenues: () => api.get<Venue[]>('/api/venues'),
};
