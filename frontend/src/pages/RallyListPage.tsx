import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface Rally {
  id: string;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
}

const RallyListPage = () => {
  const [rallies, setRallies] = useState<Rally[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchRallies = async () => {
      try {
        const response = await axios.get(`${apiUrl}/api/rallies`);
        setRallies(response.data);
      } catch (err) {
        console.error('Error fetching rallies:', err);
        setError('Failed to load stamp rallies. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRallies();
  }, [apiUrl]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="container-mobile py-8 flex justify-center">
        <div className="animate-pulse text-center">
          <div className="h-4 bg-gray-300 rounded w-3/4 mx-auto mb-4"></div>
          <div className="h-32 bg-gray-300 rounded mb-4"></div>
          <div className="h-32 bg-gray-300 rounded"></div>
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
      <h1 className="text-2xl font-bold mb-6">Available Stamp Rallies</h1>
      
      {rallies.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No stamp rallies available at the moment.
        </div>
      ) : (
        <div className="space-y-4">
          {rallies.map((rally) => (
            <div key={rally.id} className="card p-4">
              <h2 className="text-xl font-semibold">{rally.name}</h2>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-1 mb-2">
                {formatDate(rally.start_date)} - {formatDate(rally.end_date)}
              </p>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                {rally.description}
              </p>
              <Link
                to={`/rallies/${rally.id}/checkpoints`}
                className="btn btn-primary inline-block"
              >
                Participate
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RallyListPage;
