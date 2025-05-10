import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Layout = () => {
  const { logout } = useAuth();
  const location = useLocation();

  return (
    <div className="flex flex-col min-h-screen">
      <header className="bg-primary-600 text-white shadow-md">
        <div className="container-mobile py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold">Digital Stamp Rally</Link>
          <button 
            onClick={logout}
            className="text-sm px-3 py-1 rounded-md bg-primary-700 hover:bg-primary-800"
          >
            Logout
          </button>
        </div>
      </header>
      
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
      
      <footer className="bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="container-mobile py-4">
          <nav className="flex justify-around">
            <Link 
              to="/rallies" 
              className={`flex flex-col items-center p-2 ${
                location.pathname.includes('/rallies') && !location.pathname.includes('/stamps') 
                  ? 'text-primary-600' 
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span className="text-xs mt-1">Rallies</span>
            </Link>
            
            {location.pathname.includes('/rallies/') && !location.pathname.includes('/stamps') && (
              <Link 
                to={`${location.pathname.split('/checkpoints')[0]}/stamps`}
                className="flex flex-col items-center p-2 text-gray-600 dark:text-gray-400"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
                <span className="text-xs mt-1">Stamps</span>
              </Link>
            )}
            
            {location.pathname.includes('/stamps') && (
              <Link 
                to={`${location.pathname.split('/stamps')[0]}/checkpoints`}
                className="flex flex-col items-center p-2 text-gray-600 dark:text-gray-400"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
                <span className="text-xs mt-1">Map</span>
              </Link>
            )}
            
            <Link 
              to="/profile" 
              className={`flex flex-col items-center p-2 ${
                location.pathname === '/profile' 
                  ? 'text-primary-600' 
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span className="text-xs mt-1">Profile</span>
            </Link>
          </nav>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
