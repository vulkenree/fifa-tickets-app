'use client';

import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { VenueMap } from '@/components/venues/venue-map';
import { Map, Home, User, Sparkles, Building2 } from 'lucide-react';

export default function VenuesPage() {
  const { user, logout } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Please log in to access the venues page.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Map className="h-6 w-6 text-blue-500" />
              <h1 className="text-xl font-bold text-gray-900">FIFA 2026 Venues</h1>
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
              <span className="text-sm text-gray-600">
                Welcome, <span className="font-medium text-gray-900">{user.username}</span>!
              </span>
              <Button variant="outline" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          {/* Page Header */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              FIFA 2026 World Cup Venues
            </h2>
            <p className="text-gray-600">
              Explore all 16 venues across North America where the FIFA 2026 World Cup matches will be held.
            </p>
          </div>

          {/* Map Container */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <Building2 className="h-5 w-5 text-blue-500 mr-2" />
                Venue Locations
              </h3>
              <p className="text-sm text-gray-600">
                Click on any stadium marker to see venue details. The map shows all 16 venues across USA, Canada, and Mexico.
              </p>
            </div>
            
            <VenueMap className="w-full" />
          </div>

          {/* Venue Statistics */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-2 bg-red-100 rounded-lg">
                  <Building2 className="h-6 w-6 text-red-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Venues</p>
                  <p className="text-2xl font-bold text-gray-900">16</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Map className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Countries</p>
                  <p className="text-2xl font-bold text-gray-900">3</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Building2 className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">USA Venues</p>
                  <p className="text-2xl font-bold text-gray-900">11</p>
                </div>
              </div>
            </div>
          </div>

          {/* Venue List */}
          <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">All Venues</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">🇺🇸 United States (11 venues)</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Atlanta</li>
                  <li>• Boston</li>
                  <li>• Dallas</li>
                  <li>• Houston</li>
                  <li>• Kansas City</li>
                  <li>• Los Angeles</li>
                  <li>• Miami</li>
                  <li>• New York/New Jersey</li>
                  <li>• Philadelphia</li>
                  <li>• San Francisco Bay Area</li>
                  <li>• Seattle</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">🇨🇦 Canada (2 venues)</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Toronto</li>
                  <li>• Vancouver</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">🇲🇽 Mexico (3 venues)</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Guadalajara</li>
                  <li>• Mexico City</li>
                  <li>• Monterrey</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
