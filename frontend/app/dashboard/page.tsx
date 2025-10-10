'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/hooks/use-auth';
import { useTickets } from '@/hooks/use-tickets';
import { useMatches } from '@/hooks/use-matches';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Ticket, Match, TicketFormData } from '@/lib/types';
import { format } from 'date-fns';

const ticketSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  match_number: z.string().min(1, 'Match number is required'),
  date: z.string().min(1, 'Date is required'),
  venue: z.string().min(1, 'Venue is required'),
  ticket_category: z.string().min(1, 'Ticket category is required'),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  ticket_info: z.string().optional(),
  ticket_price: z.string().optional(),
});

type TicketForm = z.infer<typeof ticketSchema>;

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { tickets, isLoading, createTicket, updateTicket, deleteTicket } = useTickets();
  const { matches } = useMatches();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [userFilter, setUserFilter] = useState('all');
  const [venueFilter, setVenueFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTicket, setEditingTicket] = useState<Ticket | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);

  const form = useForm<TicketForm>({
    resolver: zodResolver(ticketSchema),
    defaultValues: {
      name: '',
      match_number: '',
      date: '',
      venue: '',
      ticket_category: '',
      quantity: 1,
      ticket_info: '',
      ticket_price: '',
    },
  });

  // Get unique values for filters
  const uniqueUsers = [...new Set(tickets.map(t => t.username))];
  const uniqueVenues = [...new Set(tickets.map(t => t.venue))];
  const uniqueCategories = [...new Set(tickets.map(t => t.ticket_category))];

  // Sort matches numerically by match number
  const sortedMatches = [...matches].sort((a, b) => {
    const aNum = parseInt(a.match_number.replace('M', ''));
    const bNum = parseInt(b.match_number.replace('M', ''));
    return aNum - bNum;
  });

  // Handle match selection
  const handleMatchSelect = (matchNumber: string) => {
    const match = matches.find(m => m.match_number === matchNumber);
    if (match) {
      setSelectedMatch(match);
      form.setValue('match_number', match.match_number);
      form.setValue('date', match.date);
      form.setValue('venue', match.venue);
    }
  };

  // Form submission
  const onSubmit = async (data: TicketForm) => {
    try {
      // Convert ticket_price string to number or undefined
      const ticketData: TicketFormData = {
        ...data,
        ticket_price: data.ticket_price && data.ticket_price.trim() !== '' 
          ? parseFloat(data.ticket_price) 
          : undefined
      };

      if (editingTicket) {
        await updateTicket(editingTicket.id, ticketData);
        toast.success('Ticket updated successfully');
      } else {
        await createTicket(ticketData);
        toast.success('Ticket created successfully');
      }
      setIsDialogOpen(false);
      setEditingTicket(null);
      form.reset();
      setSelectedMatch(null);
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to save ticket');
    }
  };

  // Clear filters function
  const clearFilters = () => {
    setSearchTerm('');
    setUserFilter('all');
    setVenueFilter('all');
    setCategoryFilter('all');
  };

  // Filter tickets
  const filteredTickets = tickets.filter(ticket => {
    const matchesSearch = !searchTerm || 
      ticket.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.match_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.venue.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.ticket_category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.username.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesUser = userFilter === 'all' || ticket.username === userFilter;
    const matchesVenue = venueFilter === 'all' || ticket.venue === venueFilter;
    const matchesCategory = categoryFilter === 'all' || ticket.ticket_category === categoryFilter;
    
    return matchesSearch && matchesUser && matchesVenue && matchesCategory;
  });

  const handleDeleteTicket = async (id: number) => {
    if (confirm('Are you sure you want to delete this ticket?')) {
      try {
        await deleteTicket(id);
        toast.success('Ticket deleted successfully');
      } catch (error: any) {
        toast.error(error.response?.data?.error || 'Failed to delete ticket');
      }
    }
  };

  const handleEditTicket = (ticket: Ticket) => {
    setEditingTicket(ticket);
    form.reset({
      name: ticket.name,
      match_number: ticket.match_number,
      date: ticket.date,
      venue: ticket.venue,
      ticket_category: ticket.ticket_category,
      quantity: ticket.quantity,
      ticket_info: ticket.ticket_info || '',
      ticket_price: ticket.ticket_price ? ticket.ticket_price.toString() : '',
    });
    // Find and set the selected match
    const match = matches.find(m => m.match_number === ticket.match_number);
    setSelectedMatch(match || null);
    setIsDialogOpen(true);
  };

  const canEditTicket = (ticket: Ticket) => {
    return user && ticket.user_id === user.id;
  };

  const handleOpenDialog = () => {
    setEditingTicket(null);
    form.reset();
    setSelectedMatch(null);
    setIsDialogOpen(true);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading tickets...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold text-gray-900">FIFA 2026 Tickets</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, <span className="font-medium text-gray-900">{user?.username}</span>!
              </span>
              <Button variant="outline" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">All Tickets</h1>
              <p className="text-gray-600 mt-2">FIFA 2026 World Cup Ticket Management</p>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="mt-4 sm:mt-0" onClick={handleOpenDialog}>
                  + Add New Ticket
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>
                    {editingTicket ? 'Edit Ticket' : 'Add New Ticket'}
                  </DialogTitle>
                  <DialogDescription>
                    {editingTicket ? 'Update ticket information' : 'Add a new FIFA 2026 ticket'}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Match Number */}
                    <div className="space-y-2">
                      <Label htmlFor="match_number">Match Number *</Label>
                      <Select onValueChange={handleMatchSelect} value={selectedMatch?.match_number || ''}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a match" />
                        </SelectTrigger>
                        <SelectContent>
                          {sortedMatches.map((match) => (
                            <SelectItem key={match.match_number} value={match.match_number}>
                              {match.match_number}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {form.formState.errors.match_number && (
                        <p className="text-sm text-red-600">{form.formState.errors.match_number.message}</p>
                      )}
                    </div>

                    {/* Date */}
                    <div className="space-y-2">
                      <Label htmlFor="date">Date *</Label>
                      <Input
                        id="date"
                        type="text"
                        {...form.register('date')}
                        readOnly
                        className="bg-gray-50"
                      />
                      {form.formState.errors.date && (
                        <p className="text-sm text-red-600">{form.formState.errors.date.message}</p>
                      )}
                    </div>

                    {/* Venue */}
                    <div className="space-y-2">
                      <Label htmlFor="venue">Venue *</Label>
                      <Input
                        id="venue"
                        type="text"
                        {...form.register('venue')}
                        readOnly
                        className="bg-gray-50"
                      />
                      {form.formState.errors.venue && (
                        <p className="text-sm text-red-600">{form.formState.errors.venue.message}</p>
                      )}
                    </div>

                    {/* Name */}
                    <div className="space-y-2">
                      <Label htmlFor="name">Name *</Label>
                      <Input
                        id="name"
                        type="text"
                        placeholder="Who is attending?"
                        {...form.register('name')}
                      />
                      {form.formState.errors.name && (
                        <p className="text-sm text-red-600">{form.formState.errors.name.message}</p>
                      )}
                    </div>

                    {/* Ticket Category */}
                    <div className="space-y-2">
                      <Label htmlFor="ticket_category">Category *</Label>
                      <Select onValueChange={(value) => form.setValue('ticket_category', value)} value={form.watch('ticket_category')}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Category 1">Category 1</SelectItem>
                          <SelectItem value="Category 2">Category 2</SelectItem>
                          <SelectItem value="Category 3">Category 3</SelectItem>
                          <SelectItem value="Category 4">Category 4</SelectItem>
                        </SelectContent>
                      </Select>
                      {form.formState.errors.ticket_category && (
                        <p className="text-sm text-red-600">{form.formState.errors.ticket_category.message}</p>
                      )}
                    </div>

                    {/* Quantity */}
                    <div className="space-y-2">
                      <Label htmlFor="quantity">Quantity *</Label>
                      <Input
                        id="quantity"
                        type="number"
                        min="1"
                        {...form.register('quantity', { valueAsNumber: true })}
                      />
                      {form.formState.errors.quantity && (
                        <p className="text-sm text-red-600">{form.formState.errors.quantity.message}</p>
                      )}
                    </div>

                    {/* Ticket Info */}
                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="ticket_info">Ticket Info (Optional)</Label>
                      <Input
                        id="ticket_info"
                        type="text"
                        placeholder="Additional ticket information"
                        {...form.register('ticket_info')}
                      />
                    </div>

                    {/* Ticket Price */}
                    <div className="space-y-2">
                      <Label htmlFor="ticket_price">Price (Optional)</Label>
                      <Input
                        id="ticket_price"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="0.00"
                        {...form.register('ticket_price')}
                      />
                    </div>
                  </div>

                  <div className="flex justify-end space-x-2 pt-4">
                    <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={form.formState.isSubmitting}>
                      {form.formState.isSubmitting ? 'Saving...' : (editingTicket ? 'Update Ticket' : 'Create Ticket')}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="max-w-md">
            <Input
              type="text"
              placeholder="Search tickets by name, match, venue..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Filters</CardTitle>
              <Button variant="outline" size="sm" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">User</label>
                <Select value={userFilter} onValueChange={setUserFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Users" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Users</SelectItem>
                    {uniqueUsers.map(user => (
                      <SelectItem key={user} value={user}>{user}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Venue</label>
                <Select value={venueFilter} onValueChange={setVenueFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Venues" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Venues</SelectItem>
                    {uniqueVenues.map(venue => (
                      <SelectItem key={venue} value={venue}>{venue}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {uniqueCategories.map(category => (
                      <SelectItem key={category} value={category}>{category}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tickets Table */}
        <Card>
          <CardHeader>
            <CardTitle>Tickets ({filteredTickets.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {filteredTickets.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No tickets found. Add your first ticket!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Match</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Venue</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredTickets.map((ticket) => (
                      <TableRow key={ticket.id}>
                        <TableCell>{ticket.username}</TableCell>
                        <TableCell>{ticket.name}</TableCell>
                        <TableCell>{ticket.match_number}</TableCell>
                        <TableCell>{format(new Date(ticket.date), 'MMM dd, yyyy')}</TableCell>
                        <TableCell>{ticket.venue}</TableCell>
                        <TableCell>{ticket.ticket_category}</TableCell>
                        <TableCell>{ticket.quantity}</TableCell>
                        <TableCell>
                          {ticket.ticket_price ? `$${ticket.ticket_price.toFixed(2)}` : '-'}
                        </TableCell>
                        <TableCell>
                          {canEditTicket(ticket) ? (
                            <div className="flex space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleEditTicket(ticket)}
                              >
                                Edit
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDeleteTicket(ticket.id)}
                              >
                                Delete
                              </Button>
                            </div>
                          ) : (
                            <span className="text-gray-400 text-sm">View Only</span>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
