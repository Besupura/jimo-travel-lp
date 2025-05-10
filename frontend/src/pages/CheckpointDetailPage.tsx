import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

import GPSCheckComponent from '../components/checkpoint/GPSCheckComponent';
import QRScanComponent from '../components/checkpoint/QRScanComponent';
import QuizComponent from '../components/checkpoint/QuizComponent';
import StepCheckComponent from '../components/checkpoint/StepCheckComponent';
import PhotoComponent from '../components/checkpoint/PhotoComponent';

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

const CheckpointDetailPage: React.FC = () => {
  const { checkpointId } = useParams<{ checkpointId: string }>();
  const navigate = useNavigate();
  const [checkpoint, setCheckpoint] = useState<Checkpoint | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchCheckpoint = async () => {
      try {
        const response = await axios.get(`${apiUrl}/api/checkpoints/${checkpointId}`);
        setCheckpoint(response.data);
      } catch (err) {
        console.error('Error fetching checkpoint:', err);
        setError('Failed to load checkpoint details. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCheckpoint();
  }, [checkpointId, apiUrl]);

  const handleComplete = async (data: any) => {
    try {
      setIsLoading(true);
      const response = await axios.post(`${apiUrl}/api/checkpoints/${checkpointId}/acquire`, data);
      
      if (response.data.success) {
        setSuccessMessage('Congratulations! You have acquired a stamp!');
        setCheckpoint(prev => prev ? { ...prev, acquired: true, acquired_at: new Date().toISOString() } : null);
      } else {
        setError(response.data.message || 'Failed to acquire stamp. Please try again.');
      }
    } catch (err: any) {
      console.error('Error acquiring stamp:', err);
      setError(err.response?.data?.message || 'Failed to acquire stamp. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !checkpoint) {
    return (
      <div className="container-mobile py-8 flex justify-center">
        <div className="animate-pulse text-center">
          <div className="h-4 bg-gray-300 rounded w-3/4 mx-auto mb-4"></div>
          <div className="h-64 bg-gray-300 rounded mb-4"></div>
        </div>
      </div>
    );
  }

  if (error && !successMessage) {
    return (
      <div className="container-mobile py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
        <button
          onClick={() => navigate(-1)}
          className="btn btn-outline"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!checkpoint) {
    return (
      <div className="container-mobile py-8">
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
          Checkpoint not found.
        </div>
        <button
          onClick={() => navigate('/rallies')}
          className="btn btn-outline"
        >
          Back to Rallies
        </button>
      </div>
    );
  }

  const componentMap: Record<string, React.FC<{ checkpoint: Checkpoint; onComplete: (data: any) => Promise<void> }>> = {
    gps: GPSCheckComponent,
    qr: QRScanComponent,
    quiz: QuizComponent,
    steps: StepCheckComponent,
    photo: PhotoComponent
  };

  const CheckComponent = componentMap[checkpoint.type];

  return (
    <div className="container-mobile py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{checkpoint.name}</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{checkpoint.description}</p>
        
        <div className="flex items-center mt-2">
          <span className="text-sm text-gray-500 mr-2">Type: {checkpoint.type}</span>
          {checkpoint.acquired ? (
            <span className="badge badge-success">Acquired</span>
          ) : (
            <span className="badge badge-pending">Not Acquired</span>
          )}
        </div>
      </div>

      {successMessage ? (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-6 rounded mb-6 text-center">
          <p className="text-lg font-semibold">{successMessage}</p>
          <div className="mt-4 flex justify-center">
            <Link
              to={`/rallies/${checkpoint.rally_id}/stamps`}
              className="btn btn-primary mr-2"
            >
              View Stamp Book
            </Link>
            <Link
              to={`/rallies/${checkpoint.rally_id}/checkpoints`}
              className="btn btn-outline"
            >
              Back to Checkpoints
            </Link>
          </div>
        </div>
      ) : checkpoint.acquired ? (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-6 rounded mb-6 text-center">
          <p className="text-lg font-semibold">You have already acquired this stamp!</p>
          <div className="mt-4 flex justify-center">
            <Link
              to={`/rallies/${checkpoint.rally_id}/stamps`}
              className="btn btn-primary mr-2"
            >
              View Stamp Book
            </Link>
            <Link
              to={`/rallies/${checkpoint.rally_id}/checkpoints`}
              className="btn btn-outline"
            >
              Back to Checkpoints
            </Link>
          </div>
        </div>
      ) : (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">Complete the challenge to get your stamp!</h2>
          
          {CheckComponent && (
            <CheckComponent 
              checkpoint={checkpoint} 
              onComplete={handleComplete} 
            />
          )}
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mt-4">
              {error}
            </div>
          )}
        </div>
      )}
      
      <div className="mt-6">
        <button
          onClick={() => navigate(-1)}
          className="btn btn-outline"
        >
          Go Back
        </button>
      </div>
    </div>
  );
};

export default CheckpointDetailPage;
