/**
 * User Controller
 * Handles user-related operations including authentication
 */
const User = require('../models/User');
const { createToken, verifyToken } = require('../middleware/auth');
const emailService = require('../services/emailService');
const logger = require('../utils/logger');
const helpers = require('../utils/helpers');

/**
 * Register a new user
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.register = async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    // Check if user already exists
    const existingUser = await User.findOne({ 
      $or: [{ email }, { username }] 
    });
    
    if (existingUser) {
      return res.status(400).json({ 
        success: false, 
        message: 'User with that email or username already exists' 
      });
    }
    
    // Create new user
    const user = new User({
      username,
      email,
      password
    });
    
    await user.save();
    
    // Generate verification token
    const verificationToken = helpers.generateRandomToken();
    
    // Send verification email
    await emailService.sendVerificationEmail(
      user.email, 
      verificationToken,
      user.username
    );
    
    // Create JWT token
    const token = user.generateAuthToken();
    
    res.status(201).json({
      success: true,
      token,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        role: user.role
      }
    });
  } catch (error) {
    logger.error('User registration error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error registering user', 
      error: error.message 
    });
  }
};

/**
 * Login user
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user by email
    const user = await User.findByEmail(email);
    
    if (!user) {
      return res.status(401).json({ 
        success: false, 
        message: 'Invalid credentials' 
      });
    }
    
    // Check password
    const isMatch = await user.comparePassword(password);
    
    if (!isMatch) {
      return res.status(401).json({ 
        success: false, 
        message: 'Invalid credentials' 
      });
    }
    
    // Update last login timestamp
    await user.updateLoginTimestamp();
    
    // Generate token
    const token = user.generateAuthToken();
    
    res.status(200).json({
      success: true,
      token,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        role: user.role
      }
    });
  } catch (error) {
    logger.error('User login error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error logging in', 
      error: error.message 
    });
  }
};

/**
 * Get current user profile
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }
    
    res.status(200).json({
      success: true,
      user
    });
  } catch (error) {
    logger.error('Get profile error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error getting profile', 
      error: error.message 
    });
  }
};

/**
 * Update user profile
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.updateProfile = async (req, res) => {
  try {
    const { username, email } = req.body;
    
    // Find user by ID
    const user = await User.findById(req.user.id);
    
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }
    
    // Check if username or email is taken by another user
    if (username && username !== user.username) {
      const existingUser = await User.findOne({ username });
      if (existingUser) {
        return res.status(400).json({ 
          success: false, 
          message: 'Username is already taken' 
        });
      }
      user.username = username;
    }
    
    if (email && email !== user.email) {
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return res.status(400).json({ 
          success: false, 
          message: 'Email is already taken' 
        });
      }
      user.email = email;
      user.isVerified = false;
      
      // Send new verification email
      const verificationToken = helpers.generateRandomToken();
      await emailService.sendVerificationEmail(
        email, 
        verificationToken,
        user.username
      );
    }
    
    // Save updated user
    await user.save();
    
    res.status(200).json({
      success: true,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        role: user.role,
        isVerified: user.isVerified
      }
    });
  } catch (error) {
    logger.error('Update profile error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error updating profile', 
      error: error.message 
    });
  }
};

/**
 * Change user password
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.changePassword = async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;
    
    // Find user by ID
    const user = await User.findById(req.user.id);
    
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }
    
    // Check current password
    const isMatch = await user.comparePassword(currentPassword);
    
    if (!isMatch) {
      return res.status(401).json({ 
        success: false, 
        message: 'Current password is incorrect' 
      });
    }
    
    // Update password
    user.password = newPassword;
    await user.save();
    
    // Send password change notification email
    await emailService.sendPasswordChangeEmail(user.email, user.username);
    
    res.status(200).json({
      success: true,
      message: 'Password changed successfully'
    });
  } catch (error) {
    logger.error('Change password error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error changing password', 
      error: error.message 
    });
  }
};

/**
 * Delete user account
 * @async
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.deleteAccount = async (req, res) => {
  try {
    const { password } = req.body;
    
    // Find user by ID
    const user = await User.findById(req.user.id);
    
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }
    
    // Check password
    const isMatch = await user.comparePassword(password);
    
    if (!isMatch) {
      return res.status(401).json({ 
        success: false, 
        message: 'Password is incorrect' 
      });
    }
    
    // Delete user
    await User.findByIdAndDelete(user._id);
    
    // Send account deletion email
    await emailService.sendAccountDeletionEmail(user.email, user.username);
    
    res.status(200).json({
      success: true,
      message: 'Account deleted successfully'
    });
  } catch (error) {
    logger.error('Delete account error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Error deleting account', 
      error: error.message 
    });
  }
}; 