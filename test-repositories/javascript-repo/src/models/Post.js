/**
 * Post Model
 * Defines the schema and methods for post entities
 * Contains relationships to User model
 */
const mongoose = require('mongoose');

const commentSchema = new mongoose.Schema({
  content: {
    type: String,
    required: [true, 'Comment content is required'],
    trim: true,
    maxlength: [500, 'Comment cannot be more than 500 characters']
  },
  author: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Comment author is required']
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

const postSchema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, 'Post title is required'],
    trim: true,
    maxlength: [100, 'Title cannot be more than 100 characters']
  },
  content: {
    type: String,
    required: [true, 'Post content is required'],
    trim: true
  },
  author: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Post author is required']
  },
  tags: [{
    type: String,
    trim: true
  }],
  status: {
    type: String,
    enum: ['draft', 'published', 'archived'],
    default: 'draft'
  },
  likes: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }],
  comments: [commentSchema],
  viewCount: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true
});

/**
 * Pre-find hook to populate author field with user data
 */
postSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'author',
    select: 'username email'
  });
  next();
});

/**
 * Instance method to add a comment to a post
 * @param {string} content - Comment content
 * @param {ObjectId} userId - User ID of comment author
 * @returns {Promise<Post>} - Updated post document
 */
postSchema.methods.addComment = function(content, userId) {
  this.comments.push({
    content,
    author: userId
  });
  return this.save();
};

/**
 * Instance method to toggle like status for a user
 * @param {ObjectId} userId - User ID
 * @returns {Promise<Post>} - Updated post document
 */
postSchema.methods.toggleLike = function(userId) {
  const userIdStr = userId.toString();
  const userLikedIndex = this.likes.findIndex(id => id.toString() === userIdStr);
  
  if (userLikedIndex > -1) {
    // User already liked the post, remove like
    this.likes.splice(userLikedIndex, 1);
  } else {
    // User hasn't liked the post, add like
    this.likes.push(userId);
  }
  
  return this.save();
};

/**
 * Instance method to increment view count
 * @returns {Promise<Post>} - Updated post document
 */
postSchema.methods.incrementViewCount = function() {
  this.viewCount += 1;
  return this.save();
};

/**
 * Static method to find posts by tag
 * @param {string} tag - Tag to search for
 * @returns {Promise<Post[]>} - Array of post documents
 */
postSchema.statics.findByTag = function(tag) {
  return this.find({ tags: tag, status: 'published' });
};

const Post = mongoose.model('Post', postSchema);

module.exports = Post; 