# JavaScript Express API Repository

This repository contains a Node.js Express API application for testing Codex-Arch functionality. It demonstrates various JavaScript patterns, relationships, and structures that can be analyzed by the Codex-Arch tool.

## Project Structure

The project follows a modular architecture with clear separation of concerns:

```
src/
├── controllers/     # Request handlers
├── middleware/      # Express middleware
├── models/          # Mongoose models
├── routes/          # API routes
├── services/        # Business logic
├── utils/           # Utility functions
├── app.js           # Express app setup
└── config.js        # Configuration
```

## Architecture Features

This repository showcases various JavaScript patterns and relationships, including:

- **ES6 Classes**: Used for models with inheritance patterns
- **Module Exports/Imports**: Demonstrates dependency relationships
- **Middleware Chains**: Shows function composition and execution flow
- **MVC Pattern**: Clear separation between Models, Routes, and Controllers
- **Service Layer**: Abstracted business logic in dedicated services
- **Authentication Flow**: JWT-based authentication with middleware protection
- **Caching Mechanism**: In-memory caching with TTL for API responses
- **Error Handling**: Centralized error handling with custom middleware

## Models and Relationships

The application contains two main models with relationships:

- **User Model**: Represents users with authentication capabilities
- **Post Model**: Represents blog posts with author relationships to users
- **Comments**: Embedded documents within posts, related to users

## API Endpoints

The API provides endpoints for user and post management:

### User Routes
- `POST /api/users/register` - Register a new user
- `POST /api/users/login` - Authenticate user
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `PUT /api/users/change-password` - Change user password
- `DELETE /api/users/account` - Delete user account

### Post Routes
- `GET /api/posts` - Get all posts
- `GET /api/posts/:id` - Get post by ID
- `POST /api/posts` - Create new post
- `PUT /api/posts/:id` - Update post
- `DELETE /api/posts/:id` - Delete post
- `POST /api/posts/:id/comments` - Add comment to post
- `POST /api/posts/:id/like` - Toggle like status for post

## Installation and Setup

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file with the following variables:
   ```
   PORT=3000
   MONGODB_URI=mongodb://localhost:27017/codex_test_api
   JWT_SECRET=your-secret-key
   NODE_ENV=development
   ```
4. Start the server:
   ```
   npm start
   ```
   
## Development

This repository is explicitly designed for testing Codex-Arch and demonstrates:

- Function calls between modules
- Inheritance hierarchies
- Middleware chains
- Authentication flows
- Database relationships
- Service-oriented architecture

## Testing with Codex-Arch

This repository is part of a test suite for validating Codex-Arch functionality across different programming languages and patterns. It can be used to verify entity extraction, relationship detection, and knowledge graph construction for JavaScript/Node.js applications. 