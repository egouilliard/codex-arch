/**
 * Application configuration
 * Sets up environment variables and default values
 */
require('dotenv').config();

const config = {
  // Server configuration
  PORT: process.env.PORT || 3000,
  NODE_ENV: process.env.NODE_ENV || 'development',
  
  // Database configuration
  MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/codex_test_api',
  
  // JWT configuration
  JWT_SECRET: process.env.JWT_SECRET || 'codex-arch-test-secret',
  JWT_EXPIRATION: process.env.JWT_EXPIRATION || '1d',
  
  // Email configuration
  EMAIL_HOST: process.env.EMAIL_HOST || 'smtp.mailtrap.io',
  EMAIL_PORT: process.env.EMAIL_PORT || 2525,
  EMAIL_USER: process.env.EMAIL_USER || '',
  EMAIL_PASS: process.env.EMAIL_PASS || '',
  EMAIL_FROM: process.env.EMAIL_FROM || 'noreply@example.com',
  
  // Cache configuration
  CACHE_TTL: process.env.CACHE_TTL || 60 * 5, // 5 minutes
};

module.exports = config; 