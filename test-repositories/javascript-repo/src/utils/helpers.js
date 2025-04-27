/**
 * Helper Utilities
 * Common utility functions used throughout the application
 */
const crypto = require('crypto');

/**
 * Generate a random token of specified length
 * @param {number} [length=32] - Length of the token
 * @returns {string} - Random token
 */
exports.generateRandomToken = (length = 32) => {
  return crypto.randomBytes(length).toString('hex');
};

/**
 * Format a date to a readable string
 * @param {Date|string|number} date - Date to format
 * @param {string} [format='long'] - Format type: 'long', 'short', 'relative'
 * @returns {string} - Formatted date string
 */
exports.formatDate = (date, format = 'long') => {
  const dateObj = new Date(date);
  
  if (isNaN(dateObj)) {
    return 'Invalid date';
  }
  
  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString();
    
    case 'relative':
      const now = new Date();
      const diffInSeconds = Math.floor((now - dateObj) / 1000);
      
      if (diffInSeconds < 60) {
        return `${diffInSeconds} seconds ago`;
      }
      
      const diffInMinutes = Math.floor(diffInSeconds / 60);
      if (diffInMinutes < 60) {
        return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
      }
      
      const diffInHours = Math.floor(diffInMinutes / 60);
      if (diffInHours < 24) {
        return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
      }
      
      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays < 30) {
        return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
      }
      
      const diffInMonths = Math.floor(diffInDays / 30);
      if (diffInMonths < 12) {
        return `${diffInMonths} month${diffInMonths > 1 ? 's' : ''} ago`;
      }
      
      const diffInYears = Math.floor(diffInMonths / 12);
      return `${diffInYears} year${diffInYears > 1 ? 's' : ''} ago`;
    
    case 'long':
    default:
      return dateObj.toLocaleString();
  }
};

/**
 * Truncate a string to a specified length
 * @param {string} str - String to truncate
 * @param {number} [length=100] - Maximum length
 * @param {string} [suffix='...'] - Suffix to add if truncated
 * @returns {string} - Truncated string
 */
exports.truncateString = (str, length = 100, suffix = '...') => {
  if (!str || str.length <= length) {
    return str;
  }
  
  return str.substring(0, length).trim() + suffix;
};

/**
 * Convert a string to slug format
 * @param {string} str - String to convert
 * @returns {string} - Slug formatted string
 */
exports.slugify = (str) => {
  return str
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

/**
 * Sanitize a string for safe HTML output
 * @param {string} str - String to sanitize
 * @returns {string} - Sanitized string
 */
exports.sanitizeHTML = (str) => {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};

/**
 * Paginate an array of items
 * @param {Array} items - Array to paginate
 * @param {number} page - Current page number (1-based)
 * @param {number} limit - Items per page
 * @returns {Object} - Pagination result with items and metadata
 */
exports.paginateArray = (items, page = 1, limit = 10) => {
  const startIndex = (page - 1) * limit;
  const endIndex = page * limit;
  
  const results = {
    data: items.slice(startIndex, endIndex),
    pagination: {
      total: items.length,
      totalPages: Math.ceil(items.length / limit),
      currentPage: page,
      limit
    }
  };
  
  return results;
};

/**
 * Deep clone an object
 * @param {Object} obj - Object to clone
 * @returns {Object} - Cloned object
 */
exports.deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Debounce a function to limit how often it can be called
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
exports.debounce = (func, wait = 300) => {
  let timeout;
  
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}; 