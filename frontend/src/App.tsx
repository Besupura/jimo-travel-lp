import { useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

import LoginPage from './pages/LoginPage';
import AdminLoginPage from './pages/AdminLoginPage';
import RallyListPage from './pages/RallyListPage';
import CheckpointListPage from './pages/CheckpointListPage';
import CheckpointDetailPage from './pages/CheckpointDetailPage';
import StampBookPage from './pages/StampBookPage';
import NotFoundPage from './pages/NotFoundPage';

import Layout from './components/Layout';

const AdminLayout = () => {
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Digital Stamp Rally Admin</h1>
            <nav className="flex space-x-4">
              <a href="/admin/rallies" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                Rallies
              </a>
              <a href="/admin/checkpoints" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                Checkpoints
              </a>
              <a href="/admin/reports" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                Reports
              </a>
            </nav>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <Routes>
            <Route path="rallies" element={<div>Rally Management (placeholder)</div>} />
            <Route path="checkpoints" element={<div>Checkpoint Management (placeholder)</div>} />
            <Route path="reports" element={<div>Reports (placeholder)</div>} />
          </Routes>
        </div>
      </main>
    </div>
  );
};

const App = () => {
  const { isAuthenticated, isAdmin } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const path = window.location.pathname;
    if (!isAuthenticated && !path.includes('/login')) {
      if (path.includes('/admin')) {
        navigate('/admin/login');
      } else {
        navigate('/login');
      }
    }
  }, [isAuthenticated, navigate]);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/admin/login" element={<AdminLoginPage />} />
      
      {/* Protected user routes */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/rallies" replace />} />
        <Route path="rallies" element={<RallyListPage />} />
        <Route path="rallies/:rallyId/checkpoints" element={<CheckpointListPage />} />
        <Route path="checkpoints/:checkpointId" element={<CheckpointDetailPage />} />
        <Route path="rallies/:rallyId/stamps" element={<StampBookPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
      
      {/* Protected admin routes */}
      <Route 
        path="/admin/*" 
        element={isAdmin ? <AdminLayout /> : <Navigate to="/admin/login" replace />} 
      />
    </Routes>
  );
};

export default App;
