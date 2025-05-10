import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

interface Checkpoint {
  id: string;
  rally_id: string;
  name: string;
  description: string;
  type: string;
  order: number;
  condition_data: any;
  acquired: boolean;
  acquired_at: string | null;
}

const CheckpointListPage: React.FC = () => {
  const { rallyId } = useParams<{ rallyId: string }>();
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchCheckpoints = async () => {
      try {
        const response = await axios.get(`${apiUrl}/api/rallies/${rallyId}/checkpoints`);
        setCheckpoints(response.data);
      } catch (err) {
        console.error('Error fetching checkpoints:', err);
        setError('Failed to load checkpoints. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCheckpoints();

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation([position.coords.latitude, position.coords.longitude]);
      },
      (err) => {
        console.warn('Error getting location:', err.message);
      }
    );
  }, [rallyId, apiUrl]);

  if (isLoading) {
    return (
      <div className="container-mobile py-8 flex justify-center">
        <div className="animate-pulse text-center">
          <div className="h-4 bg-gray-300 rounded w-3/4 mx-auto mb-4"></div>
          <div className="h-64 bg-gray-300 rounded mb-4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container-mobile py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  const getMapCenter = () => {
    if (checkpoints.length === 0) {
      return userLocation || [35.6762, 139.6503]; // Default to Tokyo
    }

    if (userLocation) {
      return userLocation;
    }

    const validCheckpoints = checkpoints.filter(cp => 
      cp.condition_data && 
      cp.condition_data.latitude !== undefined && 
      cp.condition_data.longitude !== undefined
    );

    if (validCheckpoints.length === 0) {
      return [35.6762, 139.6503]; // Default to Tokyo
    }

    const sumLat = validCheckpoints.reduce((sum, cp) => sum + cp.condition_data.latitude, 0);
    const sumLng = validCheckpoints.reduce((sum, cp) => sum + cp.condition_data.longitude, 0);
    
    return [sumLat / validCheckpoints.length, sumLng / validCheckpoints.length];
  };

  return (
    <div className="flex flex-col h-full">
      <div className="container-mobile py-4">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-xl font-bold">Checkpoints</h1>
          <div className="flex space-x-2">
            <button
              className={`px-3 py-1 rounded-md ${viewMode === 'map' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => setViewMode('map')}
            >
              Map
            </button>
            <button
              className={`px-3 py-1 rounded-md ${viewMode === 'list' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => setViewMode('list')}
            >
              List
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'map' && (
        <div className="flex-1 z-0">
          <MapContainer 
            center={getMapCenter() as [number, number]} 
            zoom={13} 
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            {userLocation && (
              <Marker position={userLocation}>
                <Popup>You are here</Popup>
              </Marker>
            )}
            
            {checkpoints.map(checkpoint => {
              if (checkpoint.condition_data && 
                  checkpoint.condition_data.latitude !== undefined && 
                  checkpoint.condition_data.longitude !== undefined) {
                
                const position: [number, number] = [
                  checkpoint.condition_data.latitude,
                  checkpoint.condition_data.longitude
                ];
                
                return (
                  <Marker 
                    key={checkpoint.id} 
                    position={position}
                    icon={checkpoint.acquired ? 
                      new L.Icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                        iconRetinaUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41],
                        popupAnchor: [1, -34],
                        shadowSize: [41, 41]
                      }) : 
                      undefined
                    }
                  >
                    <Popup>
                      <div>
                        <h3 className="font-bold">{checkpoint.name}</h3>
                        <p className="text-sm">{checkpoint.description}</p>
                        <Link 
                          to={`/checkpoints/${checkpoint.id}`}
                          className="text-primary-600 hover:underline text-sm block mt-2"
                        >
                          View Details
                        </Link>
                      </div>
                    </Popup>
                  </Marker>
                );
              }
              return null;
            })}
          </MapContainer>
        </div>
      )}

      {viewMode === 'list' && (
        <div className="container-mobile py-4 flex-1 overflow-auto">
          <div className="space-y-4">
            {checkpoints.map(checkpoint => (
              <Link 
                key={checkpoint.id} 
                to={`/checkpoints/${checkpoint.id}`}
                className="block"
              >
                <div className="card p-4 flex items-center">
                  <div className="flex-1">
                    <h2 className="text-lg font-semibold">{checkpoint.name}</h2>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">{checkpoint.description}</p>
                    <div className="flex items-center mt-1">
                      <span className="text-xs text-gray-500 mr-2">Type: {checkpoint.type}</span>
                      {checkpoint.acquired ? (
                        <span className="badge badge-success">Acquired</span>
                      ) : (
                        <span className="badge badge-pending">Not Acquired</span>
                      )}
                    </div>
                  </div>
                  <div className="ml-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CheckpointListPage;
