/**
 * API service for making HTTP requests
 */
import { ApiResponse, User, Post } from '../types';

const API_URL = 'https://api.example.com';

/**
 * Generic fetch function with error handling
 * @param url - API endpoint
 * @param options - Fetch options
 * @returns Promise with API response
 */
async function fetchWithErrorHandling<T>(
  url: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    console.error('API request failed:', error);
    return {
      success: false,
      data: null as unknown as T,
      message: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}

/**
 * User API endpoints
 */
export const userApi = {
  /**
   * Get all users
   * @returns Promise with user list
   */
  getUsers: (): Promise<ApiResponse<User[]>> => {
    return fetchWithErrorHandling<User[]>(`${API_URL}/users`);
  },

  /**
   * Get user by ID
   * @param id - User ID
   * @returns Promise with user data
   */
  getUserById: (id: string): Promise<ApiResponse<User>> => {
    return fetchWithErrorHandling<User>(`${API_URL}/users/${id}`);
  },

  /**
   * Create a new user
   * @param userData - User data to create
   * @returns Promise with created user
   */
  createUser: (userData: Omit<User, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<User>> => {
    return fetchWithErrorHandling<User>(`${API_URL}/users`, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Update an existing user
   * @param id - User ID
   * @param userData - User data to update
   * @returns Promise with updated user
   */
  updateUser: (id: string, userData: Partial<User>): Promise<ApiResponse<User>> => {
    return fetchWithErrorHandling<User>(`${API_URL}/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Delete a user
   * @param id - User ID
   * @returns Promise with success indicator
   */
  deleteUser: (id: string): Promise<ApiResponse<boolean>> => {
    return fetchWithErrorHandling<boolean>(`${API_URL}/users/${id}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Post API endpoints
 */
export const postApi = {
  /**
   * Get all posts
   * @returns Promise with post list
   */
  getPosts: (): Promise<ApiResponse<Post[]>> => {
    return fetchWithErrorHandling<Post[]>(`${API_URL}/posts`);
  },

  /**
   * Get post by ID
   * @param id - Post ID
   * @returns Promise with post data
   */
  getPostById: (id: string): Promise<ApiResponse<Post>> => {
    return fetchWithErrorHandling<Post>(`${API_URL}/posts/${id}`);
  },

  /**
   * Get posts by user ID
   * @param userId - User ID
   * @returns Promise with posts by user
   */
  getPostsByUser: (userId: string): Promise<ApiResponse<Post[]>> => {
    return fetchWithErrorHandling<Post[]>(`${API_URL}/users/${userId}/posts`);
  },

  /**
   * Create a new post
   * @param postData - Post data to create
   * @returns Promise with created post
   */
  createPost: (postData: Omit<Post, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<Post>> => {
    return fetchWithErrorHandling<Post>(`${API_URL}/posts`, {
      method: 'POST',
      body: JSON.stringify(postData),
    });
  },

  /**
   * Update an existing post
   * @param id - Post ID
   * @param postData - Post data to update
   * @returns Promise with updated post
   */
  updatePost: (id: string, postData: Partial<Post>): Promise<ApiResponse<Post>> => {
    return fetchWithErrorHandling<Post>(`${API_URL}/posts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(postData),
    });
  },

  /**
   * Delete a post
   * @param id - Post ID
   * @returns Promise with success indicator
   */
  deletePost: (id: string): Promise<ApiResponse<boolean>> => {
    return fetchWithErrorHandling<boolean>(`${API_URL}/posts/${id}`, {
      method: 'DELETE',
    });
  },
}; 