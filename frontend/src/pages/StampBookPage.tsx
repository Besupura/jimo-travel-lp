import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

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

interface Rally {
  id: string;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
}

const StampBookPage: React.FC = () => {
  const { rallyId } = useParams<{ rallyId: string }>();
  const [rally, setRally] = useState<Rally | null>(null);
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const rallyResponse = await axios.get(`${apiUrl}/api/rallies/${rallyId}`);
        setRally(rallyResponse.data);
        
        const checkpointsResponse = await axios.get(`${apiUrl}/api/rallies/${rallyId}/checkpoints`);
        setCheckpoints(checkpointsResponse.data);
      } catch (err) {
        console.error('Error fetching stamp book data:', err);
        setError('Failed to load stamp book. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [rallyId, apiUrl]);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not acquired';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const calculateProgress = () => {
    if (checkpoints.length === 0) return 0;
    const acquiredCount = checkpoints.filter(cp => cp.acquired).length;
    return Math.round((acquiredCount / checkpoints.length) * 100);
  };

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

  return (
    <div className="container-mobile py-8">
      {rally && (
        <div className="mb-6">
          <h1 className="text-2xl font-bold">{rally.name} - Stamp Book</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">{rally.description}</p>
        </div>
      )}
      
      <div className="card p-4 mb-6">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-lg font-semibold">Progress</h2>
          <span className="text-lg font-bold text-primary-600">{calculateProgress()}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
          <div 
            className="bg-primary-600 h-2.5 rounded-full" 
            style={{ width: `${calculateProgress()}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-500 mt-2">
          {checkpoints.filter(cp => cp.acquired).length} of {checkpoints.length} stamps collected
        </p>
      </div>
      
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {checkpoints.map((checkpoint) => (
          <div 
            key={checkpoint.id} 
            className={`card p-4 text-center ${checkpoint.acquired ? 'border-green-500 border-2' : 'opacity-60'}`}
          >
            <div className="mb-2">
              {checkpoint.acquired ? (
                <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              ) : (
                <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              )}
            </div>
            
            <h3 className="font-semibold">{checkpoint.name}</h3>
            <p className="text-xs text-gray-500 mt-1">Type: {checkpoint.type}</p>
            
            {checkpoint.acquired ? (
              <p className="text-xs text-green-600 mt-1">
                Acquired: {formatDate(checkpoint.acquired_at)}
              </p>
            ) : (
              <Link
                to={`/checkpoints/${checkpoint.id}`}
                className="text-xs text-primary-600 hover:underline mt-2 inline-block"
              >
                Get this stamp
              </Link>
            )}
          </div>
        ))}
      </div>
      
      <div className="mt-6">
        <Link
          to={`/rallies/${rallyId}/checkpoints`}
          className="btn btn-primary"
        >
          Back to Checkpoints
        </Link>
      </div>
    </div>
  );
};

export default StampBookPage;
