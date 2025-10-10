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
  ticket_price?: number;
}
