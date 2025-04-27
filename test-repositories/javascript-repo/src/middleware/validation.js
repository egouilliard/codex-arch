/**
 * Validation Middleware
 * Handles request validation and error handling
 */
const logger = require('../utils/logger');

/**
 * Validation schemas for different request types
 */
const validationSchemas = {
  registerUser: {
    username: {
      required: true,
      minLength: 3,
      maxLength: 30,
      regex: /^[a-zA-Z0-9_]+$/
    },
    email: {
      required: true,
      isEmail: true
    },
    password: {
      required: true,
      minLength: 6
    }
  },
  loginUser: {
    email: {
      required: true,
      isEmail: true
    },
    password: {
      required: true
    }
  },
  updateProfile: {
    username: {
      minLength: 3,
      maxLength: 30,
      regex: /^[a-zA-Z0-9_]+$/
    },
    email: {
      isEmail: true
    }
  },
  changePassword: {
    currentPassword: {
      required: true
    },
    newPassword: {
      required: true,
      minLength: 6
    }
  },
  deleteAccount: {
    password: {
      required: true
    }
  },
  createPost: {
    title: {
      required: true,
      minLength: 3,
      maxLength: 100
    },
    content: {
      required: true
    },
    tags: {
      isArray: true
    },
    status: {
      isIn: ['draft', 'published', 'archived']
    }
  },
  updatePost: {
    title: {
      minLength: 3,
      maxLength: 100
    },
    content: {},
    tags: {
      isArray: true
    },
    status: {
      isIn: ['draft', 'published', 'archived']
    }
  },
  addComment: {
    content: {
      required: true,
      minLength: 1,
      maxLength: 500
    }
  }
};

/**
 * Validate value against validation rules
 * @param {*} value - Value to validate
 * @param {string} field - Field name
 * @param {Object} rules - Validation rules
 * @returns {string|null} - Error message or null if valid
 */
const validateField = (value, field, rules) => {
  // Check required
  if (rules.required && (value === undefined || value === null || value === '')) {
    return `${field} is required`;
  }
  
  // Skip further validation if value is not provided and not required
  if (value === undefined || value === null || value === '') {
    return null;
  }
  
  // Check minLength
  if (rules.minLength && value.length < rules.minLength) {
    return `${field} must be at least ${rules.minLength} characters long`;
  }
  
  // Check maxLength
  if (rules.maxLength && value.length > rules.maxLength) {
    return `${field} cannot be more than ${rules.maxLength} characters long`;
  }
  
  // Check regex
  if (rules.regex && !rules.regex.test(value)) {
    return `${field} contains invalid characters`;
  }
  
  // Check isEmail
  if (rules.isEmail) {
    const emailRegex = /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/;
    if (!emailRegex.test(value)) {
      return `${field} must be a valid email address`;
    }
  }
  
  // Check isArray
  if (rules.isArray && !Array.isArray(value)) {
    return `${field} must be an array`;
  }
  
  // Check isIn
  if (rules.isIn && !rules.isIn.includes(value)) {
    return `${field} must be one of: ${rules.isIn.join(', ')}`;
  }
  
  return null;
};

/**
 * Middleware for request validation
 * @param {string} schemaName - Name of validation schema to use
 * @returns {Function} - Express middleware function
 */
exports.validateRequest = (schemaName) => {
  return (req, res, next) => {
    const schema = validationSchemas[schemaName];
    
    if (!schema) {
      logger.error(`Validation schema not found: ${schemaName}`);
      return next();
    }
    
    const errors = [];
    
    // Validate each field
    Object.keys(schema).forEach(field => {
      const value = req.body[field];
      const error = validateField(value, field, schema[field]);
      
      if (error) {
        errors.push(error);
      }
    });
    
    // If validation errors exist, return them
    if (errors.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors
      });
    }
    
    next();
  };
};

/**
 * Error handling middleware
 * @param {Error} err - Error object
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
exports.errorHandler = (err, req, res, next) => {
  logger.error('Server error:', err);
  
  // MongoDB duplicate key error
  if (err.code === 11000) {
    return res.status(400).json({
      success: false,
      message: 'Duplicate key error',
      error: err.message
    });
  }
  
  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const errors = Object.values(err.errors).map(e => e.message);
    
    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors
    });
  }
  
  // JSON parsing error
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json({
      success: false,
      message: 'Invalid JSON',
      error: err.message
    });
  }
  
  // Default to 500 server error
  res.status(500).json({
    success: false,
    message: 'Server error',
    error: process.env.NODE_ENV === 'production' ? 'Something went wrong' : err.message
  });
}; 