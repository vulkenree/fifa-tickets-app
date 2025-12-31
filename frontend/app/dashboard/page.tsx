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
import { SearchableSelect } from '@/components/ui/searchable-select';
import { toast } from 'sonner';
import { Ticket, Match, TicketFormData } from '@/lib/types';
import { format, parseISO } from 'date-fns';
import { FloatingChatButton } from '@/components/chat/floating-button';
import { Sparkles, Home, User, Map } from 'lucide-react';

const ticketSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  match_number: z.string().min(1, 'Match number is required'),
  date: z.string().min(1, 'Date is required'),
  venue: z.string().min(1, 'Venue is required'),
  teams: z.string().optional(),
  match_type: z.string().optional(),
  ticket_category: z.string().min(1, 'Ticket category is required'),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  ticket_info: z.string().optional(),
  ticket_price: z.string().optional(),
});

type TicketForm = z.infer<typeof ticketSchema>;

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { tickets, isLoading, createTicket, updateTicket, deleteTicket } = useTickets();
  const { matches, isLoading: matchesLoading } = useMatches();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [userFilter, setUserFilter] = useState<string[]>([]);
  const [venueFilter, setVenueFilter] = useState<string[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string[]>([]);
  const [matchNumberFilter, setMatchNumberFilter] = useState<string[]>([]);
  const [matchTypeFilter, setMatchTypeFilter] = useState<string[]>([]);
  const [teamsFilter, setTeamsFilter] = useState<string[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTicket, setEditingTicket] = useState<Ticket | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  
  // Sorting state
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const form = useForm<TicketForm>({
    resolver: zodResolver(ticketSchema),
    defaultValues: {
      name: '',
      match_number: '',
      date: '',
      venue: '',
      teams: '',
      match_type: '',
      ticket_category: '',
      quantity: 1,
      ticket_info: '',
      ticket_price: '',
    },
  });

  // Get unique values for filters
  const uniqueUsers = [...new Set(tickets.map(t => t.username).filter(Boolean))].sort();
  const uniqueVenues = [...new Set(tickets.map(t => t.venue).filter(Boolean))].sort();
  const uniqueCategories = [...new Set(tickets.map(t => t.ticket_category).filter(Boolean))].sort();
  const uniqueMatchNumbers = [...new Set(tickets.map(t => t.match_number).filter(Boolean))].sort((a, b) => {
    const aNum = parseInt(a.replace('M', ''));
    const bNum = parseInt(b.replace('M', ''));
    return aNum - bNum;
  });
  
  // Filter out null, undefined, empty strings, and '-' for match types
  const uniqueMatchTypes = [...new Set(
    tickets
      .map(t => t.match_type)
      .filter(mt => mt && mt.trim() !== '' && mt.trim() !== '-')
  )].sort();
  
  // Extract unique teams from tickets (parse "Team1 - Team2" format)
  // Only include tickets that have valid teams data (not null, empty, or '-')
  const uniqueTeams = [...new Set(
    tickets
      .filter(t => t.teams && t.teams.trim() !== '' && t.teams.trim() !== '-')
      .map(t => t.teams)
      .flatMap(teams => teams.split(' - ').map(team => team.trim()))
      .filter(team => team.length > 0)
  )].sort();

  // Sort matches numerically by match number
  const sortedMatches = matches && matches.length > 0 ? [...matches].sort((a, b) => {
    const aNum = parseInt(a.match_number.replace('M', ''));
    const bNum = parseInt(b.match_number.replace('M', ''));
    return aNum - bNum;
  }) : [];

  // Handle match selection
  const handleMatchSelect = (matchNumber: string) => {
    const match = matches.find(m => m.match_number === matchNumber);
    if (match) {
      setSelectedMatch(match);
      form.setValue('match_number', match.match_number);
      form.setValue('date', match.date);
      form.setValue('venue', match.venue);
      form.setValue('teams', match.teams || '');
      form.setValue('match_type', match.match_type || '');
    }
  };

  // Handle column sorting
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
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
    setUserFilter([]);
    setVenueFilter([]);
    setCategoryFilter([]);
    setMatchNumberFilter([]);
    setMatchTypeFilter([]);
    setTeamsFilter([]);
  };

  // Filter tickets
  const filteredTickets = tickets.filter(ticket => {
    const matchesSearch = !searchTerm || 
      ticket.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.match_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.venue.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.ticket_category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.username.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesUser = userFilter.length === 0 || userFilter.includes(ticket.username);
    const matchesVenue = venueFilter.length === 0 || venueFilter.includes(ticket.venue);
    const matchesCategory = categoryFilter.length === 0 || categoryFilter.includes(ticket.ticket_category);
    const matchesMatchNumber = matchNumberFilter.length === 0 || matchNumberFilter.includes(ticket.match_number);
    // Match type filter: if filter is empty, show all. If filter has values, only show tickets with match_type that matches
    // Exclude tickets with null, empty, or '-' values when filter is active
    const matchesMatchType = matchTypeFilter.length === 0 || 
      (ticket.match_type && 
       ticket.match_type.trim() !== '' && 
       ticket.match_type.trim() !== '-' && 
       matchTypeFilter.includes(ticket.match_type));
    
    // Teams filter: if filter is empty, show all. If filter has values, only show tickets with teams that match
    // Exclude tickets with null, empty, or '-' values when filter is active
    const matchesTeams = teamsFilter.length === 0 || 
      (ticket.teams && 
       ticket.teams.trim() !== '' && 
       ticket.teams.trim() !== '-' && 
       teamsFilter.some(team => ticket.teams.toLowerCase().includes(team.toLowerCase())));
    
    return matchesSearch && matchesUser && matchesVenue && matchesCategory && matchesMatchNumber && matchesMatchType && matchesTeams;
  });

  // Sort filtered tickets
  const sortedTickets = [...filteredTickets].sort((a, b) => {
    if (!sortColumn) return 0;
    
    let aValue, bValue;
    
    switch (sortColumn) {
      case 'match_number':
        aValue = parseInt(a.match_number.replace('M', ''));
        bValue = parseInt(b.match_number.replace('M', ''));
        break;
      case 'date':
        aValue = parseISO(a.date).getTime();
        bValue = parseISO(b.date).getTime();
        break;
      case 'quantity':
        aValue = a.quantity || 0;
        bValue = b.quantity || 0;
        break;
      case 'ticket_price':
        aValue = a.ticket_price || 0;
        bValue = b.ticket_price || 0;
        break;
      case 'username':
        aValue = a.username?.toString().toLowerCase() || '';
        bValue = b.username?.toString().toLowerCase() || '';
        break;
      case 'name':
        aValue = a.name?.toString().toLowerCase() || '';
        bValue = b.name?.toString().toLowerCase() || '';
        break;
      case 'venue':
        aValue = a.venue?.toString().toLowerCase() || '';
        bValue = b.venue?.toString().toLowerCase() || '';
        break;
      case 'teams':
        aValue = a.teams?.toString().toLowerCase() || '';
        bValue = b.teams?.toString().toLowerCase() || '';
        break;
      case 'match_type':
        aValue = a.match_type?.toString().toLowerCase() || '';
        bValue = b.match_type?.toString().toLowerCase() || '';
        break;
      case 'ticket_category':
        aValue = a.ticket_category?.toString().toLowerCase() || '';
        bValue = b.ticket_category?.toString().toLowerCase() || '';
        break;
      case 'ticket_info':
        aValue = a.ticket_info?.toString().toLowerCase() || '';
        bValue = b.ticket_info?.toString().toLowerCase() || '';
        break;
      default:
        return 0;
    }
    
    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
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
      teams: ticket.teams || '',
      match_type: ticket.match_type || '',
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

  if (isLoading || matchesLoading) {
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
                      <Button
                        variant="outline"
                        onClick={() => window.location.href = '/dashboard'}
                        className="flex items-center space-x-2"
                      >
                        <Home size={16} />
                        <span>Home</span>
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => window.location.href = '/profile'}
                        className="flex items-center space-x-2"
                      >
                        <User size={16} />
                        <span>Profile</span>
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => window.location.href = '/chat'}
                        className="flex items-center space-x-2"
                      >
                        <Sparkles size={16} />
                        <span>AI Assistant</span>
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => window.location.href = '/venues'}
                        className="flex items-center space-x-2"
                      >
                        <Map size={16} />
                        <span>Venues</span>
                      </Button>
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
                      <Select 
                        onValueChange={handleMatchSelect} 
                        value={form.watch('match_number') || selectedMatch?.match_number || ''}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder={matchesLoading ? "Loading matches..." : "Select a match"} />
                        </SelectTrigger>
                        <SelectContent>
                          {sortedMatches.length > 0 ? (
                            sortedMatches.map((match) => (
                              <SelectItem key={match.match_number} value={match.match_number}>
                                {match.match_number}
                              </SelectItem>
                            ))
                          ) : (
                            <div className="px-2 py-1.5 text-sm text-gray-500">No matches available</div>
                          )}
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

                    {/* Teams */}
                    <div className="space-y-2">
                      <Label htmlFor="teams">Teams</Label>
                      <Input
                        id="teams"
                        type="text"
                        {...form.register('teams')}
                        readOnly
                        className="bg-gray-50"
                      />
                      <small className="text-gray-500">Auto-filled from match schedule</small>
                    </div>

                    {/* Match Type */}
                    <div className="space-y-2">
                      <Label htmlFor="match_type">Match Type</Label>
                      <Input
                        id="match_type"
                        type="text"
                        {...form.register('match_type')}
                        readOnly
                        className="bg-gray-50"
                      />
                      <small className="text-gray-500">Auto-filled from match schedule</small>
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <SearchableSelect
                options={uniqueUsers.map(user => ({ value: user, label: user }))}
                value={userFilter}
                onChange={(value) => setUserFilter(Array.isArray(value) ? value : [])}
                placeholder="All Users"
                searchPlaceholder="Search users..."
                multiSelect={true}
              />
              
              <SearchableSelect
                options={uniqueVenues.map(venue => ({ value: venue, label: venue }))}
                value={venueFilter}
                onChange={(value) => setVenueFilter(Array.isArray(value) ? value : [])}
                placeholder="All Venues"
                searchPlaceholder="Search venues..."
                multiSelect={true}
              />
              
              <SearchableSelect
                options={uniqueCategories.map(category => ({ value: category, label: category }))}
                value={categoryFilter}
                onChange={(value) => setCategoryFilter(Array.isArray(value) ? value : [])}
                placeholder="All Categories"
                searchPlaceholder="Search categories..."
                multiSelect={true}
              />
              
              <SearchableSelect
                options={uniqueMatchNumbers.map(match => ({ value: match, label: match }))}
                value={matchNumberFilter}
                onChange={(value) => setMatchNumberFilter(Array.isArray(value) ? value : [])}
                placeholder="All Matches"
                searchPlaceholder="Search match numbers..."
                multiSelect={true}
              />
              
              <SearchableSelect
                options={uniqueMatchTypes.map(matchType => ({ value: matchType, label: matchType }))}
                value={matchTypeFilter}
                onChange={(value) => setMatchTypeFilter(Array.isArray(value) ? value : [])}
                placeholder="All Match Types"
                searchPlaceholder="Search match types..."
                multiSelect={true}
              />
              
              <SearchableSelect
                options={uniqueTeams.map(team => ({ value: team, label: team }))}
                value={teamsFilter}
                onChange={(value) => setTeamsFilter(Array.isArray(value) ? value : [])}
                placeholder="All Teams"
                searchPlaceholder="Search teams..."
                multiSelect={true}
              />
            </div>
          </CardContent>
        </Card>

        {/* Tickets Table */}
        <Card>
          <CardHeader>
            <CardTitle>Tickets ({sortedTickets.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {sortedTickets.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No tickets found. Add your first ticket!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('username')}
                      >
                        User {sortColumn === 'username' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('name')}
                      >
                        Name {sortColumn === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('match_number')}
                      >
                        Match {sortColumn === 'match_number' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('date')}
                      >
                        Date {sortColumn === 'date' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('venue')}
                      >
                        Venue {sortColumn === 'venue' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('teams')}
                      >
                        Teams {sortColumn === 'teams' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('match_type')}
                      >
                        Match Type {sortColumn === 'match_type' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('ticket_category')}
                      >
                        Category {sortColumn === 'ticket_category' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('quantity')}
                      >
                        Quantity {sortColumn === 'quantity' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('ticket_price')}
                      >
                        Price {sortColumn === 'ticket_price' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-gray-100 select-none" 
                        onClick={() => handleSort('ticket_info')}
                      >
                        Ticket Info {sortColumn === 'ticket_info' && (sortDirection === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedTickets.map((ticket) => (
                      <TableRow key={ticket.id}>
                        <TableCell>{ticket.username}</TableCell>
                        <TableCell>{ticket.name}</TableCell>
                        <TableCell>{ticket.match_number}</TableCell>
                        <TableCell>{format(parseISO(ticket.date), 'MMM dd, yyyy')}</TableCell>
                        <TableCell>{ticket.venue}</TableCell>
                        <TableCell>{ticket.teams || '-'}</TableCell>
                        <TableCell>{ticket.match_type || '-'}</TableCell>
                        <TableCell>{ticket.ticket_category}</TableCell>
                        <TableCell>{ticket.quantity}</TableCell>
                        <TableCell>
                          {ticket.ticket_price ? `$${ticket.ticket_price.toFixed(2)}` : '-'}
                        </TableCell>
                        <TableCell>
                          {ticket.ticket_info || '-'}
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

      {/* Floating Chat Button */}
      <FloatingChatButton />
    </div>
  );
}
