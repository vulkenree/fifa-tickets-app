import useSWR from 'swr';
import { ticketsApi } from '@/lib/api';
import { Ticket, TicketFormData } from '@/lib/types';

export function useTickets() {
  const { data, error, mutate } = useSWR<Ticket[]>(
    '/api/tickets',
    () => ticketsApi.getAll().then(res => res.data)
  );

  const createTicket = async (ticket: TicketFormData) => {
    try {
      await ticketsApi.create(ticket);
      mutate();
    } catch (error) {
      throw error;
    }
  };

  const updateTicket = async (id: number, ticket: Partial<TicketFormData>) => {
    try {
      await ticketsApi.update(id, ticket);
      mutate();
    } catch (error) {
      throw error;
    }
  };

  const deleteTicket = async (id: number) => {
    try {
      await ticketsApi.delete(id);
      mutate();
    } catch (error) {
      throw error;
    }
  };

  return {
    tickets: data || [],
    isLoading: !error && !data,
    isError: error,
    createTicket,
    updateTicket,
    deleteTicket,
    mutate,
  };
}
