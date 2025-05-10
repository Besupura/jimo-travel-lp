import React, { useState } from 'react';

interface GPSCheckProps {
  checkpoint: {
    id: string;
    name: string;
    type: string;
    condition_data: {
      latitude: number;
      longitude: number;
      radius: number;
    };
  };
  onComplete: (data: any) => Promise<void>;
}

const GPSCheckComponent: React.FC<GPSCheckProps> = ({ checkpoint, onComplete }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [locationStatus, setLocationStatus] = useState<'idle' | 'acquiring' | 'acquired' | 'error'>('idle');
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null);

  const handleCheckIn = async () => {
    setIsLoading(true);
    setError('');
    setLocationStatus('acquiring');

    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        });
      });

      const location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      };

      setUserLocation(location);
      setLocationStatus('acquired');

      await onComplete({ location });
    } catch (err: any) {
      console.error('Error getting location:', err);
      setError(err.message || 'Failed to get your location. Please try again.');
      setLocationStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCoordinate = (coord: number) => {
    return coord.toFixed(6);
  };

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-md">
        <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">GPS Check-in Required</h3>
        <p className="text-sm text-blue-700 dark:text-blue-400">
          You need to be physically present at this location to acquire this stamp.
          Please allow location access when prompted.
        </p>
      </div>

      {userLocation && (
        <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-md text-sm">
          <p className="font-semibold mb-1">Your current location:</p>
          <p>Latitude: {formatCoordinate(userLocation.latitude)}</p>
          <p>Longitude: {formatCoordinate(userLocation.longitude)}</p>
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-semibold">Error:</p>
          <p>{error}</p>
          {error.includes('permission') && (
            <p className="text-sm mt-2">
              Please enable location services in your browser settings and try again.
            </p>
          )}
        </div>
      )}

      <button
        onClick={handleCheckIn}
        disabled={isLoading}
        className={`btn btn-primary w-full ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
      >
        {locationStatus === 'idle' && 'Check In at This Location'}
        {locationStatus === 'acquiring' && 'Getting Your Location...'}
        {locationStatus === 'acquired' && 'Verify Location'}
        {locationStatus === 'error' && 'Try Again'}
      </button>
    </div>
  );
};

export default GPSCheckComponent;
