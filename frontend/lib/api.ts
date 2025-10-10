import axios from 'axios';
import { User, Ticket, Match, LoginCredentials, RegisterCredentials, TicketFormData } from './types';

// Function to get API base URL dynamically
const getApiBaseUrl = () => {
  // Check if we have the production environment variable set
  const hasProductionApiUrl = process.env.NEXT_PUBLIC_API_URL && 
    process.env.NEXT_PUBLIC_API_URL.includes('railway.app');
  
  const url = hasProductionApiUrl 
    ? process.env.NEXT_PUBLIC_API_URL
    : 'http://localhost:8000';
  
  console.log('getApiBaseUrl called - API_BASE_URL:', url);
  console.log('NEXT_PUBLIC_API_URL env var:', process.env.NEXT_PUBLIC_API_URL);
  console.log('All env vars:', Object.keys(process.env).filter(key => key.includes('API')));
  console.log('Current location:', typeof window !== 'undefined' ? window.location.href : 'server-side');
  console.log('Has production API URL:', hasProductionApiUrl);
  return url;
};

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Override the baseURL for each request to ensure it's always current
api.interceptors.request.use((config) => {
  config.baseURL = getApiBaseUrl();
  console.log('Request interceptor - using baseURL:', config.baseURL);
  return config;
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
