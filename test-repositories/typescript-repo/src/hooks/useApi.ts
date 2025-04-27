/**
 * Custom hook for API calls with loading and error states
 */
import { useState, useEffect, useCallback } from 'react';
import { ApiResponse } from '../types';

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: string) => void;
  initialData?: T;
}

/**
 * Generic hook for API requests with loading and error handling
 * @param apiCall - The API call function
 * @param options - Hook options
 * @returns Object with data, loading, error, and execute function
 */
export function useApi<T, P extends any[]>(
  apiCall: (...params: P) => Promise<ApiResponse<T>>,
  options?: UseApiOptions<T>
) {
  const [data, setData] = useState<T | undefined>(options?.initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Execute the API call with parameters
   * @param params - Parameters for the API call
   * @returns Promise with the API response
   */
  const execute = useCallback(
    async (...params: P): Promise<ApiResponse<T>> => {
      setLoading(true);
      setError(null);

      try {
        const response = await apiCall(...params);
        
        if (response.success) {
          setData(response.data);
          options?.onSuccess?.(response.data);
        } else {
          setError(response.message || 'An error occurred');
          options?.onError?.(response.message || 'An error occurred');
        }
        
        setLoading(false);
        return response;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
        setError(errorMessage);
        options?.onError?.(errorMessage);
        setLoading(false);
        
        return {
          success: false,
          data: null as unknown as T,
          message: errorMessage,
        };
      }
    },
    [apiCall, options]
  );

  return {
    data,
    loading,
    error,
    execute,
  };
}

/**
 * Hook for API requests that run automatically on component mount
 * @param apiCall - The API call function
 * @param params - Parameters for the API call
 * @param options - Hook options
 * @returns Object with data, loading, and error
 */
export function useApiOnMount<T, P extends any[]>(
  apiCall: (...params: P) => Promise<ApiResponse<T>>,
  params: P,
  options?: UseApiOptions<T>
) {
  const { data, loading, error, execute } = useApi(apiCall, options);

  useEffect(() => {
    execute(...params);
  }, [execute, ...params]);

  return { data, loading, error, refetch: execute };
} 