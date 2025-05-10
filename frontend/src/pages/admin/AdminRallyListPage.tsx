import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

interface Rally {
  id: string;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
}

const AdminRallyListPage: React.FC = () => {
  const [rallies, setRallies] = useState<Rally[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchRallies = async () => {
      setIsLoading(true);
      setError('');
      
      try {
        const response = await axios.get(`${apiUrl}/api/admin/rallies`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        setRallies(response.data);
      } catch (err: any) {
        console.error('Error fetching rallies:', err);
        setError('Failed to load stamp rallies. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRallies();
  }, [apiUrl, token]);

  const handleDelete = async (rallyId: string) => {
    if (!window.confirm('Are you sure you want to delete this rally? This will also delete all associated checkpoints.')) {
      return;
    }

    try {
      await axios.delete(`${apiUrl}/api/admin/rallies/${rallyId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setRallies(rallies.filter(rally => rally.id !== rallyId));
    } catch (err: any) {
      console.error('Error deleting rally:', err);
      alert('Failed to delete rally. Please try again.');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Stamp Rally Management</h1>
        <Link 
          to="/admin/rallies/new" 
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
        >
          Create New Rally
        </Link>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-10">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading rallies...</p>
        </div>
      ) : rallies.length === 0 ? (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 text-center">
          <p className="text-gray-600 dark:text-gray-400">No stamp rallies found.</p>
          <p className="mt-2">
            <Link to="/admin/rallies/new" className="text-blue-600 hover:underline">
              Create your first stamp rally
            </Link>
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Period
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
              {rallies.map((rally) => (
                <tr key={rally.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">{rally.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(rally.start_date)} - {formatDate(rally.end_date)}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-xs">
                      {rally.description}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link 
                      to={`/admin/rallies/${rally.id}/edit`} 
                      className="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400 mr-4"
                    >
                      Edit
                    </Link>
                    <Link 
                      to={`/admin/rallies/${rally.id}/checkpoints`} 
                      className="text-green-600 hover:text-green-900 dark:hover:text-green-400 mr-4"
                    >
                      Checkpoints
                    </Link>
                    <button 
                      onClick={() => handleDelete(rally.id)} 
                      className="text-red-600 hover:text-red-900 dark:hover:text-red-400"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AdminRallyListPage;
