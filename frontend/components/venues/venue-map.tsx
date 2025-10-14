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

  useEffect(() => {
    // Fix Leaflet's default icon paths for Next.js
    if (typeof window !== 'undefined') {
      const L = require('leaflet');
      
      delete L.Icon.Default.prototype._getIconUrl;
      
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      });
    }
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


      return (
        <div className={`w-full h-96 rounded-lg overflow-hidden border border-gray-200 ${className}`}>
          <MapContainer
            center={[40, -100]} // Center on North America
            zoom={4}
            minZoom={3}
            maxZoom={10}
            zoomControl={true}
            scrollWheelZoom={true}
            doubleClickZoom={true}
            dragging={true}
            style={{ height: '100%', width: '100%' }}
            className="z-0"
            zoomAnimation={true}
            fadeAnimation={true}
            markerZoomAnimation={true}
            wheelPxPerZoomLevel={30}
            zoomSnap={0.5}
            zoomDelta={1.5}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              subdomains="abcd"
              maxZoom={20}
              tileSize={256}
              zoomOffset={0}
              updateWhenZooming={false}
              keepBuffer={2}
              maxNativeZoom={18}
              className="carto-tiles"
            />
            {venues.map((venue, index) => (
              <Marker
                key={index}
                position={[venue.lat, venue.lng]}
                riseOnHover={true}
                riseOffset={250}
              >
                <Popup
                  closeButton={true}
                  autoClose={false}
                  closeOnClick={false}
                  className="custom-popup"
                >
                  <div className="min-w-[140px]">
                    <div className="text-center">
                      <h3 className="text-base font-bold text-gray-900 mb-1">{venue.city}</h3>
                      <p className="text-xs text-gray-500 uppercase tracking-wider">
                        {venue.country === 'USA' && '🇺🇸 United States'}
                        {venue.country === 'Canada' && '🇨🇦 Canada'}
                        {venue.country === 'Mexico' && '🇲🇽 Mexico'}
                      </p>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
      
          <style jsx global>{`
            .leaflet-popup-content-wrapper {
              border-radius: 12px;
              box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
              padding: 8px 12px;
              background: linear-gradient(to bottom, #ffffff, #f9fafb);
            }
            .leaflet-popup-content {
              margin: 0;
              font-family: inherit;
            }
            .leaflet-popup-tip {
              background: #ffffff;
            }
            .leaflet-container {
              background: #f8fafc;
            }
            .leaflet-tile {
              image-rendering: -webkit-optimize-contrast;
              image-rendering: crisp-edges;
            }
            .leaflet-zoom-animated {
              will-change: transform;
            }
            .leaflet-marker-icon {
              will-change: transform;
            }
            .leaflet-popup {
              will-change: transform;
            }
            .custom-popup .leaflet-popup-content-wrapper {
              border: 1px solid #e5e7eb;
            }
            .carto-tiles {
              filter: brightness(0.95) contrast(1.1);
            }
          `}</style>
    </div>
  );
}
