/**
 * Email Service
 * Handles email sending functionality for the application
 */
const nodemailer = require('nodemailer');
const { 
  EMAIL_HOST, 
  EMAIL_PORT, 
  EMAIL_USER, 
  EMAIL_PASS, 
  EMAIL_FROM 
} = require('../config');
const logger = require('../utils/logger');

/**
 * Create and configure nodemailer transporter
 */
const transporter = nodemailer.createTransport({
  host: EMAIL_HOST,
  port: EMAIL_PORT,
  auth: {
    user: EMAIL_USER,
    pass: EMAIL_PASS
  }
});

/**
 * Send email with provided options
 * @async
 * @param {Object} mailOptions - Email options
 * @returns {Promise<Object>} - Email sending result
 */
const sendEmail = async (mailOptions) => {
  try {
    const info = await transporter.sendMail({
      from: EMAIL_FROM,
      ...mailOptions
    });
    
    logger.info(`Email sent: ${info.messageId}`);
    return info;
  } catch (error) {
    logger.error('Email sending error:', error);
    throw error;
  }
};

/**
 * Send verification email to user
 * @async
 * @param {string} to - Recipient email
 * @param {string} token - Verification token
 * @param {string} username - User's username
 * @returns {Promise<Object>} - Email sending result
 */
exports.sendVerificationEmail = async (to, token, username) => {
  const subject = 'Verify Your Email Address';
  const html = `
    <h1>Email Verification</h1>
    <p>Hello ${username},</p>
    <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
    <a href="http://localhost:3000/verify-email?token=${token}">Verify Email</a>
    <p>If you did not request this, please ignore this email.</p>
  `;
  
  return await sendEmail({ to, subject, html });
};

/**
 * Send password reset email to user
 * @async
 * @param {string} to - Recipient email
 * @param {string} token - Reset token
 * @param {string} username - User's username
 * @returns {Promise<Object>} - Email sending result
 */
exports.sendPasswordResetEmail = async (to, token, username) => {
  const subject = 'Password Reset Request';
  const html = `
    <h1>Password Reset</h1>
    <p>Hello ${username},</p>
    <p>You have requested to reset your password. Please click the link below to reset it:</p>
    <a href="http://localhost:3000/reset-password?token=${token}">Reset Password</a>
    <p>If you did not request this, please ignore this email and your password will remain unchanged.</p>
  `;
  
  return await sendEmail({ to, subject, html });
};

/**
 * Send password change notification email to user
 * @async
 * @param {string} to - Recipient email
 * @param {string} username - User's username
 * @returns {Promise<Object>} - Email sending result
 */
exports.sendPasswordChangeEmail = async (to, username) => {
  const subject = 'Password Changed';
  const html = `
    <h1>Password Changed</h1>
    <p>Hello ${username},</p>
    <p>Your password has been changed successfully.</p>
    <p>If you did not make this change, please contact support immediately.</p>
  `;
  
  return await sendEmail({ to, subject, html });
};

/**
 * Send account deletion notification email to user
 * @async
 * @param {string} to - Recipient email
 * @param {string} username - User's username
 * @returns {Promise<Object>} - Email sending result
 */
exports.sendAccountDeletionEmail = async (to, username) => {
  const subject = 'Account Deleted';
  const html = `
    <h1>Account Deleted</h1>
    <p>Hello ${username},</p>
    <p>Your account has been deleted successfully.</p>
    <p>We're sorry to see you go. If you believe this was a mistake, please contact support.</p>
  `;
  
  return await sendEmail({ to, subject, html });
};

/**
 * Send new comment notification email to post author
 * @async
 * @param {string} to - Recipient email
 * @param {string} username - User's username
 * @param {string} postTitle - Title of the post
 * @param {string} commenterName - Name of the user who commented
 * @returns {Promise<Object>} - Email sending result
 */
exports.sendCommentNotificationEmail = async (to, username, postTitle, commenterName) => {
  const subject = 'New Comment on Your Post';
  const html = `
    <h1>New Comment</h1>
    <p>Hello ${username},</p>
    <p>Your post "${postTitle}" has received a new comment from ${commenterName}.</p>
    <a href="http://localhost:3000/posts/view">View Post</a>
  `;
  
  return await sendEmail({ to, subject, html });
}; 