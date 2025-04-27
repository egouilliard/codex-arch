/**
 * Custom hook for form handling
 */
import { useState, useCallback, ChangeEvent, FormEvent } from 'react';
import { FormValues, FormErrors } from '../types';
import { validateField } from '../utils/validators';

interface UseFormOptions {
  initialValues: FormValues;
  onSubmit: (values: FormValues) => void | Promise<void>;
  validate?: (values: FormValues) => FormErrors;
}

/**
 * Hook for form state management and validation
 * @param options - Form options
 * @returns Form state and handlers
 */
export function useForm({
  initialValues,
  onSubmit,
  validate,
}: UseFormOptions) {
  const [values, setValues] = useState<FormValues>(initialValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  /**
   * Handle input change
   * @param e - Change event
   */
  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target;
      const fieldValue = type === 'checkbox' 
        ? (e.target as HTMLInputElement).checked
        : value;
      
      setValues((prev) => ({ ...prev, [name]: fieldValue }));
      
      // Validate field as user types
      if (touched[name]) {
        setErrors((prev) => ({
          ...prev,
          [name]: validateField(name, String(fieldValue)),
        }));
      }
    },
    [touched]
  );

  /**
   * Handle field blur for validation
   * @param e - Blur event
   */
  const handleBlur = useCallback((e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Mark field as touched
    setTouched((prev) => ({ ...prev, [name]: true }));
    
    // Validate on blur
    setErrors((prev) => ({
      ...prev,
      [name]: validateField(name, String(value)),
    }));
  }, []);

  /**
   * Reset form to initial state
   */
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  /**
   * Set a specific field value
   * @param name - Field name
   * @param value - Field value
   */
  const setFieldValue = useCallback((name: string, value: any) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  }, []);

  /**
   * Validate all form fields
   * @returns Boolean indicating form validity
   */
  const validateForm = useCallback((): boolean => {
    let formErrors: FormErrors = {};
    
    // Use custom validate function if provided
    if (validate) {
      formErrors = validate(values);
    } else {
      // Default validation
      Object.keys(values).forEach((key) => {
        const error = validateField(key, String(values[key]));
        if (error) {
          formErrors[key] = error;
        }
      });
    }
    
    setErrors(formErrors);
    
    // Form is valid if there are no errors
    return Object.keys(formErrors).length === 0;
  }, [validate, values]);

  /**
   * Handle form submission
   * @param e - Submit event
   */
  const handleSubmit = useCallback(
    async (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      setIsSubmitting(true);
      
      // Mark all fields as touched
      const allTouched = Object.keys(values).reduce(
        (acc, key) => ({ ...acc, [key]: true }),
        {}
      );
      setTouched(allTouched);
      
      // Validate all fields
      const isValid = validateForm();
      
      if (isValid) {
        try {
          await onSubmit(values);
        } catch (error) {
          console.error('Form submission error:', error);
        }
      }
      
      setIsSubmitting(false);
    },
    [onSubmit, validateForm, values]
  );

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setFieldValue,
    setValues,
  };
} 