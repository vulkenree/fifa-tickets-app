import axios from 'axios';
import { User, Ticket, Match, LoginCredentials, RegisterCredentials, TicketFormData } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Debug log to see what URL is being used
console.log('API_BASE_URL:', API_BASE_URL);
console.log('NEXT_PUBLIC_API_URL env var:', process.env.NEXT_PUBLIC_API_URL);
// Dummy line to trigger Railway redeploy

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
