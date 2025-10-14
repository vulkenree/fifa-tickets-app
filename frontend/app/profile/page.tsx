'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { useProfile } from '@/hooks/use-profile';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SearchableSelect } from '@/components/ui/searchable-select';
import { User, ArrowLeft, Save, Loader2, Map } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';

// FIFA 2026 World Cup Teams (48 teams)
const FIFA_2026_TEAMS = [
  // CONCACAF (Hosts + Qualified)
  'Canada', 'Mexico', 'USA',
  // CONMEBOL (Major teams)
  'Argentina', 'Brazil', 'Uruguay', 'Colombia', 'Chile', 'Ecuador', 'Peru', 'Paraguay', 'Bolivia', 'Venezuela',
  // UEFA (Major teams)
  'England', 'France', 'Germany', 'Spain', 'Italy', 'Portugal', 'Netherlands', 'Belgium', 'Croatia', 'Denmark',
  'Switzerland', 'Austria', 'Sweden', 'Norway', 'Poland', 'Czech Republic', 'Hungary', 'Turkey', 'Russia', 'Ukraine',
  'Scotland', 'Wales', 'Ireland', 'Finland', 'Iceland', 'Greece', 'Serbia', 'Montenegro', 'Bosnia and Herzegovina',
  // CAF (Major teams)
  'Morocco', 'Senegal', 'Tunisia', 'Nigeria', 'Cameroon', 'Ghana', 'Egypt', 'Algeria', 'Ivory Coast', 'Mali',
  // AFC (Major teams)
  'Japan', 'South Korea', 'Iran', 'Australia', 'Saudi Arabia', 'Qatar', 'UAE', 'Iraq', 'China', 'Thailand',
  // OFC
  'New Zealand',
];

// Sort teams alphabetically and convert to options format for SearchableSelect
const TEAM_OPTIONS = [
  { value: 'none', label: 'No favorite team' },
  ...FIFA_2026_TEAMS.sort().map(team => ({ value: team, label: team }))
];

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const { profile, isLoading, isUpdating, error, updateProfile } = useProfile();
  
  const [formData, setFormData] = useState({
    favorite_team: '',
  });

  // Update form data when profile loads
  useEffect(() => {
    if (profile) {
      setFormData({
        favorite_team: profile.favorite_team || 'none',
      });
    }
  }, [profile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await updateProfile({
        favorite_team: formData.favorite_team === 'none' ? undefined : formData.favorite_team,
      });
    } catch (err) {
      // Error is already handled in the hook
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Please log in to access your profile.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading profile...</span>
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
              <Link href="/dashboard">
                <Button variant="outline" size="sm">
                  <ArrowLeft size={16} className="mr-2" />
                  Back to Dashboard
                </Button>
              </Link>
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

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User size={24} />
              <span>Profile Settings</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username Field - Read Only */}
              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium text-gray-700">
                  Username
                </label>
                <Input
                  id="username"
                  type="text"
                  value={profile?.username || ''}
                  readOnly
                  className="bg-gray-50 cursor-not-allowed"
                  disabled={isUpdating}
                />
                <p className="text-xs text-gray-500">
                  Username cannot be changed
                </p>
              </div>

              {/* Favorite Team Field */}
              <div className="space-y-2">
                <label htmlFor="favorite_team" className="text-sm font-medium text-gray-700">
                  Favorite FIFA 2026 Team
                </label>
                <SearchableSelect
                  options={TEAM_OPTIONS}
                  value={formData.favorite_team}
                  onChange={(value) => handleInputChange('favorite_team', value as string)}
                  placeholder="Select your favorite team (optional)"
                  searchPlaceholder="Search teams..."
                  className="w-full"
                />
                <p className="text-xs text-gray-500">
                  Choose your favorite team for FIFA 2026 World Cup (optional)
                </p>
              </div>

              {/* Error Display */}
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-4">
                <Button
                  type="submit"
                  disabled={isUpdating}
                  className="flex items-center space-x-2"
                >
                  {isUpdating ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Save size={16} />
                  )}
                  <span>{isUpdating ? 'Saving...' : 'Save Changes'}</span>
                </Button>
                
                <Link href="/dashboard">
                  <Button type="button" variant="outline">
                    Cancel
                  </Button>
                </Link>
              </div>
            </form>

            {/* Profile Info */}
            {profile && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Profile Information</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Member since:</span>
                    <span className="ml-2 text-gray-900">
                      {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Unknown'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">User ID:</span>
                    <span className="ml-2 text-gray-900">{profile.id}</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
