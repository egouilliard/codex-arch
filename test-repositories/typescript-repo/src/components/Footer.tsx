import React from 'react';

/**
 * Site footer component
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-100 mt-8">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-gray-600 text-sm">
              &copy; {currentYear} MyApp. All rights reserved.
            </p>
          </div>
          
          <div className="flex space-x-6">
            <a 
              href="/terms" 
              className="text-gray-600 hover:text-blue-600 text-sm transition-colors"
            >
              Terms of Service
            </a>
            <a 
              href="/privacy" 
              className="text-gray-600 hover:text-blue-600 text-sm transition-colors"
            >
              Privacy Policy
            </a>
            <a 
              href="/contact" 
              className="text-gray-600 hover:text-blue-600 text-sm transition-colors"
            >
              Contact Us
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 