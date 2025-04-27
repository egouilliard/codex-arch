/**
 * User Routes
 * Defines API endpoints for user-related operations
 */
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const { authenticate, authorize } = require('../middleware/auth');
const { validateRequest } = require('../middleware/validation');

// Public routes
router.post(
  '/register',
  validateRequest('registerUser'),
  userController.register
);

router.post(
  '/login',
  validateRequest('loginUser'),
  userController.login
);

// Protected routes - require authentication
router.get(
  '/profile',
  authenticate,
  userController.getProfile
);

router.put(
  '/profile',
  authenticate,
  validateRequest('updateProfile'),
  userController.updateProfile
);

router.put(
  '/change-password',
  authenticate,
  validateRequest('changePassword'),
  userController.changePassword
);

router.delete(
  '/account',
  authenticate,
  validateRequest('deleteAccount'),
  userController.deleteAccount
);

// Admin routes
router.get(
  '/all',
  authenticate,
  authorize('admin'),
  (req, res) => {
    // This would be implemented in a real application
    res.status(200).json({
      success: true,
      message: 'Admin access only - would return all users'
    });
  }
);

module.exports = router; 