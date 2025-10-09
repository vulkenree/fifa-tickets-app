// Global variables
let tickets = [];
let currentTicketId = null;
let isEditMode = false;
let currentUserId = null;
let currentSortColumn = null;
let currentSortDirection = 'asc';

// DOM elements
const addTicketBtn = document.getElementById('addTicketBtn');
const ticketModal = document.getElementById('ticketModal');
const ticketForm = document.getElementById('ticketForm');
const ticketsTableBody = document.getElementById('ticketsTableBody');
const noTicketsMessage = document.getElementById('noTicketsMessage');
const searchInput = document.getElementById('searchInput');
const loadingSpinner = document.getElementById('loadingSpinner');
const modalTitle = document.getElementById('modalTitle');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    loadCurrentUser();
    loadTickets();
    
    addTicketBtn.addEventListener('click', openAddModal);
    ticketForm.addEventListener('submit', handleFormSubmit);
    searchInput.addEventListener('input', filterTickets);
    
    // Filter event listeners
    document.getElementById('userFilter').addEventListener('change', filterTickets);
    document.getElementById('venueFilter').addEventListener('change', filterTickets);
    document.getElementById('categoryFilter').addEventListener('change', filterTickets);
    document.getElementById('dateFromFilter').addEventListener('change', filterTickets);
    document.getElementById('dateToFilter').addEventListener('change', filterTickets);
    
    // Sort event listeners
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', () => sortTickets(header.dataset.column));
    });
});

// API functions
async function apiCall(url, options = {}) {
    try {
        showLoading(true);
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        showAlert(error.message, 'error');
        throw error;
    } finally {
        showLoading(false);
    }
}

// User management functions
async function loadCurrentUser() {
    try {
        const user = await apiCall('/api/user');
        currentUserId = user.id;
    } catch (error) {
        console.error('Error loading current user:', error);
        // If authentication fails, redirect to login
        if (error.message.includes('Authentication required')) {
            window.location.href = '/login';
        }
    }
}

// Ticket management functions
async function loadTickets() {
    try {
        tickets = await apiCall('/api/tickets');
        populateFilterDropdowns();
        renderTickets();
    } catch (error) {
        console.error('Error loading tickets:', error);
        // If authentication fails, redirect to login
        if (error.message.includes('Authentication required')) {
            window.location.href = '/login';
        }
    }
}

function populateFilterDropdowns() {
    // Get unique values for filters
    const users = [...new Set(tickets.map(t => t.username))].sort();
    const venues = [...new Set(tickets.map(t => t.venue))].sort();
    const categories = [...new Set(tickets.map(t => t.ticket_category))].sort();
    
    // Populate user filter
    const userFilter = document.getElementById('userFilter');
    userFilter.innerHTML = '<option value="">All Users</option>';
    users.forEach(user => {
        const option = document.createElement('option');
        option.value = user;
        option.textContent = user;
        userFilter.appendChild(option);
    });
    
    // Populate venue filter
    const venueFilter = document.getElementById('venueFilter');
    venueFilter.innerHTML = '<option value="">All Venues</option>';
    venues.forEach(venue => {
        const option = document.createElement('option');
        option.value = venue;
        option.textContent = venue;
        venueFilter.appendChild(option);
    });
    
    // Populate category filter
    const categoryFilter = document.getElementById('categoryFilter');
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}

function renderTickets(ticketsToRender = tickets) {
    if (ticketsToRender.length === 0) {
        ticketsTableBody.innerHTML = '';
        noTicketsMessage.classList.remove('hidden');
        return;
    }
    
    noTicketsMessage.classList.add('hidden');
    
    ticketsTableBody.innerHTML = ticketsToRender.map(ticket => {
        const canEdit = ticket.user_id === currentUserId;
        return `
        <tr>
            <td><span class="username-badge">${escapeHtml(ticket.username)}</span></td>
            <td>${escapeHtml(ticket.name)}</td>
            <td><span class="match-number">${escapeHtml(ticket.match_number)}</span></td>
            <td>${formatDate(ticket.date)}</td>
            <td>${escapeHtml(ticket.venue)}</td>
            <td><span class="category-badge">${escapeHtml(ticket.ticket_category)}</span></td>
            <td>${ticket.quantity}</td>
            <td>${escapeHtml(ticket.ticket_info || '-')}</td>
            <td>${ticket.ticket_price ? `$${parseFloat(ticket.ticket_price).toFixed(2)}` : '-'}</td>
            <td class="actions">
                ${canEdit ? `<button class="btn btn-warning btn-sm" onclick="editTicket(${ticket.id})">Edit</button>` : ''}
                ${canEdit ? `<button class="btn btn-danger btn-sm" onclick="deleteTicket(${ticket.id})">Delete</button>` : ''}
                ${!canEdit ? '<span class="text-muted">View Only</span>' : ''}
            </td>
        </tr>
    `;
    }).join('');
}

function filterTickets() {
    const searchTerm = searchInput.value.toLowerCase();
    const userFilter = document.getElementById('userFilter').value;
    const venueFilter = document.getElementById('venueFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const dateFromFilter = document.getElementById('dateFromFilter').value;
    const dateToFilter = document.getElementById('dateToFilter').value;
    
    const filteredTickets = tickets.filter(ticket => {
        // Text search
        const matchesSearch = !searchTerm || 
            ticket.name.toLowerCase().includes(searchTerm) ||
            ticket.match_number.toLowerCase().includes(searchTerm) ||
            ticket.venue.toLowerCase().includes(searchTerm) ||
            ticket.ticket_category.toLowerCase().includes(searchTerm) ||
            ticket.username.toLowerCase().includes(searchTerm) ||
            (ticket.ticket_info && ticket.ticket_info.toLowerCase().includes(searchTerm));
        
        // User filter
        const matchesUser = !userFilter || ticket.username === userFilter;
        
        // Venue filter
        const matchesVenue = !venueFilter || ticket.venue === venueFilter;
        
        // Category filter
        const matchesCategory = !categoryFilter || ticket.ticket_category === categoryFilter;
        
        // Date range filter
        const ticketDate = new Date(ticket.date);
        const fromDate = dateFromFilter ? new Date(dateFromFilter) : null;
        const toDate = dateToFilter ? new Date(dateToFilter) : null;
        
        const matchesDateFrom = !fromDate || ticketDate >= fromDate;
        const matchesDateTo = !toDate || ticketDate <= toDate;
        
        return matchesSearch && matchesUser && matchesVenue && matchesCategory && matchesDateFrom && matchesDateTo;
    });
    
    renderTickets(filteredTickets);
}

function sortTickets(column) {
    // Toggle sort direction if clicking the same column
    if (currentSortColumn === column) {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = column;
        currentSortDirection = 'asc';
    }
    
    // Update sort indicators
    document.querySelectorAll('.sort-indicator').forEach(indicator => {
        indicator.className = 'sort-indicator';
    });
    
    const currentHeader = document.querySelector(`[data-column="${column}"] .sort-indicator`);
    if (currentHeader) {
        currentHeader.classList.add(currentSortDirection);
    }
    
    // Sort tickets
    const sortedTickets = [...tickets].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle different data types
        if (column === 'date') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        } else if (column === 'quantity' || column === 'ticket_price') {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
        } else {
            aVal = String(aVal || '').toLowerCase();
            bVal = String(bVal || '').toLowerCase();
        }
        
        if (aVal < bVal) return currentSortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return currentSortDirection === 'asc' ? 1 : -1;
        return 0;
    });
    
    renderTickets(sortedTickets);
}

// Modal functions
function openAddModal() {
    isEditMode = false;
    currentTicketId = null;
    modalTitle.textContent = 'Add New Ticket';
    ticketForm.reset();
    ticketModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function openEditModal(ticket) {
    isEditMode = true;
    currentTicketId = ticket.id;
    modalTitle.textContent = 'Edit Ticket';
    
    // Populate form with ticket data
    document.getElementById('ticketName').value = ticket.name;
    document.getElementById('matchNumber').value = ticket.match_number;
    document.getElementById('ticketDate').value = ticket.date;
    document.getElementById('venue').value = ticket.venue;
    document.getElementById('ticketCategory').value = ticket.ticket_category;
    document.getElementById('quantity').value = ticket.quantity;
    document.getElementById('ticketInfo').value = ticket.ticket_info || '';
    document.getElementById('ticketPrice').value = ticket.ticket_price || '';
    
    ticketModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    ticketModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
    ticketForm.reset();
    isEditMode = false;
    currentTicketId = null;
}

// Form handling
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(ticketForm);
    const ticketData = {
        name: formData.get('name'),
        match_number: formData.get('match_number'),
        date: formData.get('date'),
        venue: formData.get('venue'),
        ticket_category: formData.get('ticket_category'),
        quantity: parseInt(formData.get('quantity')),
        ticket_info: formData.get('ticket_info'),
        ticket_price: formData.get('ticket_price') ? parseFloat(formData.get('ticket_price')) : null
    };
    
    // Validate match number format
    if (!validateMatchNumber(ticketData.match_number)) {
        showAlert('Match number must start with M followed by digits (e.g., M1, M23)', 'error');
        return;
    }
    
    // Validate date is within FIFA 2026 World Cup period
    if (!validateDate(ticketData.date)) {
        showAlert('Date must be between June 11, 2026 and July 19, 2026 (FIFA 2026 World Cup period)', 'error');
        return;
    }
    
    try {
        if (isEditMode) {
            await apiCall(`/api/tickets/${currentTicketId}`, {
                method: 'PUT',
                body: JSON.stringify(ticketData)
            });
            showAlert('Ticket updated successfully!', 'success');
        } else {
            await apiCall('/api/tickets', {
                method: 'POST',
                body: JSON.stringify(ticketData)
            });
            showAlert('Ticket added successfully!', 'success');
        }
        
        closeModal();
        loadTickets();
    } catch (error) {
        console.error('Error saving ticket:', error);
    }
}

// Ticket actions
async function editTicket(ticketId) {
    const ticket = tickets.find(t => t.id === ticketId);
    if (ticket) {
        openEditModal(ticket);
    }
}

async function deleteTicket(ticketId) {
    if (!confirm('Are you sure you want to delete this ticket?')) {
        return;
    }
    
    try {
        await apiCall(`/api/tickets/${ticketId}`, {
            method: 'DELETE'
        });
        showAlert('Ticket deleted successfully!', 'success');
        loadTickets();
    } catch (error) {
        console.error('Error deleting ticket:', error);
    }
}

// Validation functions
function validateMatchNumber(matchNumber) {
    const pattern = /^M\d+$/;
    return pattern.test(matchNumber);
}

function validateDate(dateString) {
    const date = new Date(dateString);
    const minDate = new Date('2026-06-11');
    const maxDate = new Date('2026-07-19');
    
    return date >= minDate && date <= maxDate;
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showLoading(show) {
    if (show) {
        loadingSpinner.classList.remove('hidden');
    } else {
        loadingSpinner.classList.add('hidden');
    }
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Insert at the top of the dashboard
    const dashboardMain = document.querySelector('.dashboard-main');
    dashboardMain.insertBefore(alert, dashboardMain.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Close modal when clicking outside
ticketModal.addEventListener('click', function(e) {
    if (e.target === ticketModal) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && !ticketModal.classList.contains('hidden')) {
        closeModal();
    }
});
