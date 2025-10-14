'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Venue } from '@/lib/types';
import { venuesApi } from '@/lib/api';
import { MapPin, Loader2 } from 'lucide-react';

// Dynamically import the map components to avoid SSR issues
const MapContainer = dynamic(() => import('react-leaflet').then((mod) => mod.MapContainer), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
      <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
    </div>
  ),
});

const TileLayer = dynamic(() => import('react-leaflet').then((mod) => mod.TileLayer), {
  ssr: false,
});

const Marker = dynamic(() => import('react-leaflet').then((mod) => mod.Marker), {
  ssr: false,
});

const Popup = dynamic(() => import('react-leaflet').then((mod) => mod.Popup), {
  ssr: false,
});

interface VenueMapProps {
  className?: string;
}

export function VenueMap({ className = '' }: VenueMapProps) {
  const [venues, setVenues] = useState<Venue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVenues = async () => {
      try {
        const response = await venuesApi.getVenues();
        setVenues(response.data);
      } catch (err) {
        console.error('Failed to fetch venues:', err);
        setError('Failed to load venue data');
      } finally {
        setLoading(false);
      }
    };

    fetchVenues();
  }, []);

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-100 rounded-lg ${className}`}>
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500 mx-auto mb-2" />
          <p className="text-gray-600">Loading venues...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-96 bg-gray-100 rounded-lg ${className}`}>
        <div className="text-center">
          <MapPin className="h-8 w-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  // Create a custom stadium icon
  const createStadiumIcon = () => {
    if (typeof window !== 'undefined' && window.L) {
      return window.L.divIcon({
        html: `
          <div class="stadium-marker">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" fill="#3B82F6" stroke="#1E40AF" stroke-width="2"/>
            </svg>
          </div>
        `,
        className: 'custom-stadium-icon',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });
    }
    return null;
  };

  return (
    <div className={`w-full h-96 rounded-lg overflow-hidden border border-gray-200 ${className}`}>
      <MapContainer
        center={[40, -100]} // Center on North America
        zoom={4}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {venues.map((venue, index) => (
          <Marker
            key={index}
            position={[venue.lat, venue.lng]}
            icon={createStadiumIcon() || undefined}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-semibold text-gray-900">{venue.name}</h3>
                <p className="text-sm text-gray-600">{venue.city}</p>
                <p className="text-sm text-gray-500">{venue.country}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      
      <style jsx global>{`
        .custom-stadium-icon {
          background: transparent !important;
          border: none !important;
        }
        .stadium-marker {
          display: flex;
          align-items: center;
          justify-content: center;
          filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
        }
        .leaflet-popup-content-wrapper {
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .leaflet-popup-content {
          margin: 0;
        }
      `}</style>
    </div>
  );
}
