import React from 'react';
import { authService } from '../services/auth';

interface HeaderProps {
  onSignOut?: () => void;
}

/**
 * Site header with navigation
 */
const Header: React.FC<HeaderProps> = ({ onSignOut }) => {
  const isLoggedIn = authService.isAuthenticated();
  const currentUser = authService.getCurrentUser();
  
  const handleSignOut = () => {
    authService.logout();
    if (onSignOut) {
      onSignOut();
    }
  };
  
  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-xl font-bold text-gray-800">
            <a href="/" className="hover:text-blue-600 transition-colors">
              MyApp
            </a>
          </h1>
          
          <nav className="ml-8">
            <ul className="flex space-x-6">
              <li>
                <a href="/" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Home
                </a>
              </li>
              <li>
                <a href="/posts" className="text-gray-600 hover:text-blue-600 transition-colors">
                  Posts
                </a>
              </li>
              <li>
                <a href="/about" className="text-gray-600 hover:text-blue-600 transition-colors">
                  About
                </a>
              </li>
            </ul>
          </nav>
        </div>
        
        <div>
          {isLoggedIn ? (
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">
                Welcome, {currentUser?.firstName || currentUser?.username}
              </span>
              <button
                onClick={handleSignOut}
                className="text-sm px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 transition-colors"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="space-x-2">
              <a 
                href="/login" 
                className="text-sm px-3 py-1 rounded bg-white border border-gray-300 hover:bg-gray-100 transition-colors"
              >
                Log In
              </a>
              <a 
                href="/signup" 
                className="text-sm px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              >
                Sign Up
              </a>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 