/**
 * Validation utility functions
 */

/**
 * Validates an email address format
 * @param email - The email address to validate
 * @returns Boolean indicating if the email is valid
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validates password complexity requirements
 * @param password - The password to validate
 * @returns Boolean indicating if the password meets complexity requirements
 */
export const isValidPassword = (password: string): boolean => {
  // At least 8 characters, one lowercase, one uppercase, one number
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
  return passwordRegex.test(password);
};

/**
 * Validates that a string is not empty
 * @param value - The string to check
 * @returns Boolean indicating if the string is not empty
 */
export const isNotEmpty = (value: string): boolean => {
  return value !== undefined && value !== null && value.trim() !== '';
};

/**
 * Validates form fields based on field type
 * @param fieldName - The name of the field
 * @param value - The value to validate
 * @returns Error message or empty string if valid
 */
export const validateField = (fieldName: string, value: string): string => {
  switch (fieldName) {
    case 'email':
      return !isValidEmail(value) ? 'Please enter a valid email address' : '';
    case 'password':
      return !isValidPassword(value) 
        ? 'Password must be at least 8 characters and contain lowercase, uppercase, and number' 
        : '';
    case 'username':
      return value.length < 3 ? 'Username must be at least 3 characters' : '';
    case 'title':
      return value.length < 5 ? 'Title must be at least 5 characters' : '';
    case 'content':
      return value.length < 10 ? 'Content must be at least 10 characters' : '';
    default:
      return !isNotEmpty(value) ? `${fieldName} is required` : '';
  }
}; 