/**
 * Cache Service
 * Handles in-memory caching for API responses
 */
const { CACHE_TTL } = require('../config');
const logger = require('../utils/logger');

// In-memory cache store
const cacheStore = new Map();

/**
 * Get cached data by key
 * @async
 * @param {string} key - Cache key
 * @returns {Promise<string|null>} - Cached data or null if not found/expired
 */
exports.getCache = async (key) => {
  try {
    if (!cacheStore.has(key)) {
      return null;
    }
    
    const cacheEntry = cacheStore.get(key);
    const now = Date.now();
    
    // Check if cache has expired
    if (now > cacheEntry.expiry) {
      cacheStore.delete(key);
      return null;
    }
    
    logger.info(`Cache hit for key: ${key}`);
    return cacheEntry.data;
  } catch (error) {
    logger.error('Cache retrieval error:', error);
    return null;
  }
};

/**
 * Set data in cache with expiration
 * @async
 * @param {string} key - Cache key
 * @param {string} data - Data to cache
 * @param {number} ttl - Time to live in seconds
 * @returns {Promise<boolean>} - Success status
 */
exports.setCache = async (key, data, ttl = CACHE_TTL) => {
  try {
    const expiry = Date.now() + (ttl * 1000);
    
    cacheStore.set(key, {
      data,
      expiry
    });
    
    logger.info(`Cache set for key: ${key}`);
    return true;
  } catch (error) {
    logger.error('Cache setting error:', error);
    return false;
  }
};

/**
 * Clear specific cache entry
 * @async
 * @param {string} key - Cache key
 * @returns {Promise<boolean>} - Success status
 */
exports.clearCache = async (key) => {
  try {
    const deleted = cacheStore.delete(key);
    
    if (deleted) {
      logger.info(`Cache cleared for key: ${key}`);
    }
    
    return deleted;
  } catch (error) {
    logger.error('Cache clearing error:', error);
    return false;
  }
};

/**
 * Clear multiple cache entries by pattern
 * @async
 * @param {string} pattern - Pattern to match keys
 * @returns {Promise<number>} - Number of cleared entries
 */
exports.clearCacheByPattern = async (pattern) => {
  try {
    const regex = new RegExp(pattern);
    let count = 0;
    
    for (const key of cacheStore.keys()) {
      if (regex.test(key)) {
        cacheStore.delete(key);
        count++;
      }
    }
    
    if (count > 0) {
      logger.info(`Cleared ${count} cache entries matching pattern: ${pattern}`);
    }
    
    return count;
  } catch (error) {
    logger.error('Cache pattern clearing error:', error);
    return 0;
  }
};

/**
 * Clear all cache entries
 * @async
 * @returns {Promise<number>} - Number of cleared entries
 */
exports.clearAllCache = async () => {
  try {
    const count = cacheStore.size;
    cacheStore.clear();
    
    logger.info(`Cleared all ${count} cache entries`);
    return count;
  } catch (error) {
    logger.error('Cache clearing all error:', error);
    return 0;
  }
};

/**
 * Get cache statistics
 * @async
 * @returns {Promise<Object>} - Cache statistics
 */
exports.getCacheStats = async () => {
  try {
    const now = Date.now();
    let activeEntries = 0;
    let expiredEntries = 0;
    
    for (const [key, entry] of cacheStore.entries()) {
      if (now > entry.expiry) {
        expiredEntries++;
      } else {
        activeEntries++;
      }
    }
    
    return {
      totalEntries: cacheStore.size,
      activeEntries,
      expiredEntries
    };
  } catch (error) {
    logger.error('Cache stats error:', error);
    return {
      totalEntries: 0,
      activeEntries: 0,
      expiredEntries: 0
    };
  }
}; 