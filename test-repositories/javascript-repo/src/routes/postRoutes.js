/**
 * Post Routes
 * Defines API endpoints for post-related operations
 */
const express = require('express');
const router = express.Router();
const postController = require('../controllers/postController');
const { authenticate, authorize } = require('../middleware/auth');
const { validateRequest } = require('../middleware/validation');

// Public routes
router.get(
  '/',
  postController.getPosts
);

router.get(
  '/:id',
  postController.getPostById
);

router.get(
  '/user/:userId',
  postController.getPostsByUser
);

// Protected routes - require authentication
router.post(
  '/',
  authenticate,
  validateRequest('createPost'),
  postController.createPost
);

router.put(
  '/:id',
  authenticate,
  validateRequest('updatePost'),
  postController.updatePost
);

router.delete(
  '/:id',
  authenticate,
  postController.deletePost
);

router.post(
  '/:id/comments',
  authenticate,
  validateRequest('addComment'),
  postController.addComment
);

router.post(
  '/:id/like',
  authenticate,
  postController.toggleLike
);

// Admin routes
router.get(
  '/admin/all',
  authenticate,
  authorize('admin'),
  (req, res) => {
    // This would be implemented in a real application
    res.status(200).json({
      success: true,
      message: 'Admin access only - would return all posts regardless of status'
    });
  }
);

module.exports = router; 