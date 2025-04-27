/**
 * Core application interfaces
 */

export interface User {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Post {
  id: string;
  title: string;
  content: string;
  userId: string;
  author?: User;
  createdAt: Date;
  updatedAt: Date;
  tags: string[];
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface FormValues {
  [key: string]: string | number | boolean;
}

export interface FormErrors {
  [key: string]: string;
} 