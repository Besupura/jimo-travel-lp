import { useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

import LoginPage from './pages/LoginPage';
import RallyListPage from './pages/RallyListPage';
import CheckpointListPage from './pages/CheckpointListPage';
import CheckpointDetailPage from './pages/CheckpointDetailPage';
import StampBookPage from './pages/StampBookPage';
import NotFoundPage from './pages/NotFoundPage';

import Layout from './components/Layout';

const App = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated && window.location.pathname !== '/login') {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      {/* Protected routes */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/rallies" replace />} />
        <Route path="rallies" element={<RallyListPage />} />
        <Route path="rallies/:rallyId/checkpoints" element={<CheckpointListPage />} />
        <Route path="checkpoints/:checkpointId" element={<CheckpointDetailPage />} />
        <Route path="rallies/:rallyId/stamps" element={<StampBookPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};

export default App;
