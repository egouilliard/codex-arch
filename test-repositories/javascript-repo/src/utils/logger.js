/**
 * Logger Utility
 * Provides consistent logging functionality throughout the application
 */
const { NODE_ENV } = require('../config');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

/**
 * Format the current timestamp
 * @returns {string} - Formatted timestamp
 */
const getTimestamp = () => {
  return new Date().toISOString();
};

/**
 * Format a log message with timestamp and level
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {Object|Error} [meta] - Additional metadata or error
 * @returns {string} - Formatted log message
 */
const formatLogMessage = (level, message, meta) => {
  const timestamp = getTimestamp();
  let formattedMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  
  if (meta) {
    if (meta instanceof Error) {
      formattedMessage += `\n${meta.stack || meta.message}`;
    } else if (typeof meta === 'object') {
      try {
        formattedMessage += `\n${JSON.stringify(meta, null, 2)}`;
      } catch (e) {
        formattedMessage += `\n[Object]`;
      }
    } else {
      formattedMessage += `\n${meta}`;
    }
  }
  
  return formattedMessage;
};

/**
 * Log a message with the info level
 * @param {string} message - Log message
 * @param {Object} [meta] - Additional metadata
 */
const info = (message, meta) => {
  const formattedMessage = formatLogMessage('info', message, meta);
  console.log(`${colors.green}${formattedMessage}${colors.reset}`);
};

/**
 * Log a message with the warn level
 * @param {string} message - Log message
 * @param {Object} [meta] - Additional metadata
 */
const warn = (message, meta) => {
  const formattedMessage = formatLogMessage('warn', message, meta);
  console.warn(`${colors.yellow}${formattedMessage}${colors.reset}`);
};

/**
 * Log a message with the error level
 * @param {string} message - Log message
 * @param {Error|Object} [error] - Error object or additional metadata
 */
const error = (message, error) => {
  const formattedMessage = formatLogMessage('error', message, error);
  console.error(`${colors.red}${formattedMessage}${colors.reset}`);
};

/**
 * Log a message with the debug level (only in development)
 * @param {string} message - Log message
 * @param {Object} [meta] - Additional metadata
 */
const debug = (message, meta) => {
  if (NODE_ENV === 'production') return;
  
  const formattedMessage = formatLogMessage('debug', message, meta);
  console.debug(`${colors.cyan}${formattedMessage}${colors.reset}`);
};

/**
 * Create a child logger with additional context
 * @param {string} context - Context name
 * @returns {Object} - Child logger instance
 */
const child = (context) => {
  return {
    info: (message, meta) => info(`[${context}] ${message}`, meta),
    warn: (message, meta) => warn(`[${context}] ${message}`, meta),
    error: (message, error) => error(`[${context}] ${message}`, error),
    debug: (message, meta) => debug(`[${context}] ${message}`, meta)
  };
};

module.exports = {
  info,
  warn,
  error,
  debug,
  child
}; 