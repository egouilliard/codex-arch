/**
 * Post Controller
 * Handles post-related operations including CRUD and interactions
 */
const Post = require('../models/Post');
const User = require('../models/User');
const logger = require('../utils/logger');
const cacheService = require('../services/cacheService');

/**
 * Create a new post
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.createPost = async (req, res) => {
  try {
    const { title, content, tags, status } = req.body;
    const userId = req.user.id;
    
    // Create new post
    const post = new Post({
      title,
      content,
      author: userId,
      tags: tags || [],
      status: status || 'draft'
    });
    
    await post.save();
    
    // Clear cache for posts by this user
    await cacheService.clearCache(`user-posts-${userId}`);
    
    res.status(201).json({
      success: true,
      post
    });
  } catch (error) {
    logger.error('Create post error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error creating post', 
      error: error.message 
    });
  }
};

/**
 * Get all published posts with pagination
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getPosts = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    const tag = req.query.tag;
    
    let query = { status: 'published' };
    
    // Filter by tag if provided
    if (tag) {
      query.tags = tag;
    }
    
    // Check if response is cached
    const cacheKey = `posts-page-${page}-limit-${limit}-tag-${tag || 'none'}`;
    const cachedData = await cacheService.getCache(cacheKey);
    
    if (cachedData) {
      return res.status(200).json(JSON.parse(cachedData));
    }
    
    // Get total count for pagination
    const total = await Post.countDocuments(query);
    
    // Get posts with pagination
    const posts = await Post.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .populate('author', 'username email');
    
    const response = {
      success: true,
      count: posts.length,
      total,
      totalPages: Math.ceil(total / limit),
      currentPage: page,
      posts
    };
    
    // Cache the response
    await cacheService.setCache(cacheKey, JSON.stringify(response));
    
    res.status(200).json(response);
  } catch (error) {
    logger.error('Get posts error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error getting posts', 
      error: error.message 
    });
  }
};

/**
 * Get post by ID
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getPostById = async (req, res) => {
  try {
    const postId = req.params.id;
    
    // Check if response is cached
    const cacheKey = `post-${postId}`;
    const cachedData = await cacheService.getCache(cacheKey);
    
    if (cachedData) {
      return res.status(200).json(JSON.parse(cachedData));
    }
    
    // Find post by ID
    const post = await Post.findById(postId);
    
    if (!post) {
      return res.status(404).json({ 
        success: false, 
        message: 'Post not found' 
      });
    }
    
    // Increment view count
    await post.incrementViewCount();
    
    // Populate comments with author information
    await post.populate('comments.author', 'username');
    
    const response = {
      success: true,
      post
    };
    
    // Cache the response
    await cacheService.setCache(cacheKey, JSON.stringify(response));
    
    res.status(200).json(response);
  } catch (error) {
    logger.error('Get post by ID error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error getting post', 
      error: error.message 
    });
  }
};

/**
 * Get posts by user
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getPostsByUser = async (req, res) => {
  try {
    const userId = req.params.userId || req.user.id;
    const isCurrentUser = userId === req.user.id;
    
    // Check if user exists
    const user = await User.findById(userId);
    
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }
    
    // Define query based on user role and ownership
    let query = { author: userId };
    
    // If not the post owner or admin, show only published posts
    if (!isCurrentUser && req.user.role !== 'admin') {
      query.status = 'published';
    }
    
    // Check if response is cached (for own posts)
    const cacheKey = `user-posts-${userId}`;
    const cachedData = await cacheService.getCache(cacheKey);
    
    if (cachedData && isCurrentUser) {
      return res.status(200).json(JSON.parse(cachedData));
    }
    
    // Get posts by user
    const posts = await Post.find(query).sort({ createdAt: -1 });
    
    const response = {
      success: true,
      count: posts.length,
      posts
    };
    
    // Cache the response for own posts
    if (isCurrentUser) {
      await cacheService.setCache(cacheKey, JSON.stringify(response));
    }
    
    res.status(200).json(response);
  } catch (error) {
    logger.error('Get posts by user error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error getting posts', 
      error: error.message 
    });
  }
};

/**
 * Update post
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.updatePost = async (req, res) => {
  try {
    const postId = req.params.id;
    const { title, content, tags, status } = req.body;
    const userId = req.user.id;
    
    // Find post by ID
    const post = await Post.findById(postId);
    
    if (!post) {
      return res.status(404).json({ 
        success: false, 
        message: 'Post not found' 
      });
    }
    
    // Check if user is the author or an admin
    if (post.author.toString() !== userId && req.user.role !== 'admin') {
      return res.status(403).json({ 
        success: false, 
        message: 'Not authorized to update this post' 
      });
    }
    
    // Update post fields
    if (title) post.title = title;
    if (content) post.content = content;
    if (tags) post.tags = tags;
    if (status) post.status = status;
    
    await post.save();
    
    // Clear cache
    await cacheService.clearCache(`post-${postId}`);
    await cacheService.clearCache(`user-posts-${post.author}`);
    
    res.status(200).json({
      success: true,
      post
    });
  } catch (error) {
    logger.error('Update post error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error updating post', 
      error: error.message 
    });
  }
};

/**
 * Delete post
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.deletePost = async (req, res) => {
  try {
    const postId = req.params.id;
    const userId = req.user.id;
    
    // Find post by ID
    const post = await Post.findById(postId);
    
    if (!post) {
      return res.status(404).json({ 
        success: false, 
        message: 'Post not found' 
      });
    }
    
    // Check if user is the author or an admin
    if (post.author.toString() !== userId && req.user.role !== 'admin') {
      return res.status(403).json({ 
        success: false, 
        message: 'Not authorized to delete this post' 
      });
    }
    
    // Delete post
    await Post.findByIdAndDelete(postId);
    
    // Clear cache
    await cacheService.clearCache(`post-${postId}`);
    await cacheService.clearCache(`user-posts-${post.author}`);
    
    res.status(200).json({
      success: true,
      message: 'Post deleted successfully'
    });
  } catch (error) {
    logger.error('Delete post error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error deleting post', 
      error: error.message 
    });
  }
};

/**
 * Add comment to post
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.addComment = async (req, res) => {
  try {
    const postId = req.params.id;
    const { content } = req.body;
    const userId = req.user.id;
    
    // Find post by ID
    const post = await Post.findById(postId);
    
    if (!post) {
      return res.status(404).json({ 
        success: false, 
        message: 'Post not found' 
      });
    }
    
    // Check if post is published
    if (post.status !== 'published') {
      return res.status(400).json({ 
        success: false, 
        message: 'Cannot comment on unpublished post' 
      });
    }
    
    // Add comment to post
    await post.addComment(content, userId);
    
    // Populate comment author info
    await post.populate('comments.author', 'username');
    
    // Clear cache
    await cacheService.clearCache(`post-${postId}`);
    
    res.status(200).json({
      success: true,
      comments: post.comments
    });
  } catch (error) {
    logger.error('Add comment error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error adding comment', 
      error: error.message 
    });
  }
};

/**
 * Toggle like status for a post
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.toggleLike = async (req, res) => {
  try {
    const postId = req.params.id;
    const userId = req.user.id;
    
    // Find post by ID
    const post = await Post.findById(postId);
    
    if (!post) {
      return res.status(404).json({ 
        success: false, 
        message: 'Post not found' 
      });
    }
    
    // Check if post is published
    if (post.status !== 'published') {
      return res.status(400).json({ 
        success: false, 
        message: 'Cannot like unpublished post' 
      });
    }
    
    // Toggle like status
    await post.toggleLike(userId);
    
    // Clear cache
    await cacheService.clearCache(`post-${postId}`);
    
    res.status(200).json({
      success: true,
      likes: post.likes,
      liked: post.likes.includes(userId)
    });
  } catch (error) {
    logger.error('Toggle like error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error toggling like status', 
      error: error.message 
    });
  }
}; 