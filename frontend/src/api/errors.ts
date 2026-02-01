/**
 * @fileoverview API error types and handling utilities
 * @module api/errors
 */

import { AxiosError } from 'axios';

/**
 * Types of API errors
 */
export enum ApiErrorType {
  /** Network error (no response from server) */
  NETWORK_ERROR = 'NETWORK_ERROR',

  /** Request timeout */
  TIMEOUT = 'TIMEOUT',

  /** Bad request (400) */
  BAD_REQUEST = 'BAD_REQUEST',

  /** Unauthorized (401) */
  UNAUTHORIZED = 'UNAUTHORIZED',

  /** Forbidden (403) */
  FORBIDDEN = 'FORBIDDEN',

  /** Not found (404) */
  NOT_FOUND = 'NOT_FOUND',

  /** Server error (500+) */
  SERVER_ERROR = 'SERVER_ERROR',

  /** Unknown error */
  UNKNOWN = 'UNKNOWN',
}

/**
 * Normalized API Error
 *
 * **Why we need this:**
 * - Axios errors have inconsistent shapes
 * - Network errors vs HTTP errors are different
 * - We want a consistent error interface throughout the app
 * - Makes error handling easier and more predictable
 */
export class ApiError extends Error {
  /** Type of error */
  type: ApiErrorType;

  /** HTTP status code (if applicable) */
  statusCode?: number;

  /** Original axios error */
  originalError?: AxiosError;

  /** Server error message (if provided) */
  serverMessage?: string;

  /** Whether this error is retryable */
  retryable: boolean;

  constructor(
    message: string,
    type: ApiErrorType,
    statusCode?: number,
    originalError?: AxiosError,
    serverMessage?: string
  ) {
    super(message);
    this.name = 'ApiError';
    this.type = type;
    this.statusCode = statusCode;
    this.originalError = originalError;
    this.serverMessage = serverMessage;

    // Determine if error is retryable
    this.retryable =
      type === ApiErrorType.NETWORK_ERROR ||
      type === ApiErrorType.TIMEOUT ||
      type === ApiErrorType.SERVER_ERROR;
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage(): string {
    // Use server message if available
    if (this.serverMessage) {
      return this.serverMessage;
    }

    // Fallback to default messages
    switch (this.type) {
      case ApiErrorType.NETWORK_ERROR:
        return 'Unable to connect to the server. Please check your internet connection.';
      case ApiErrorType.TIMEOUT:
        return 'Request timed out. Please try again.';
      case ApiErrorType.BAD_REQUEST:
        return 'Invalid request. Please check your input.';
      case ApiErrorType.UNAUTHORIZED:
        return 'You are not authorized to perform this action.';
      case ApiErrorType.FORBIDDEN:
        return 'Access denied.';
      case ApiErrorType.NOT_FOUND:
        return 'The requested resource was not found.';
      case ApiErrorType.SERVER_ERROR:
        return 'Server error. Please try again later.';
      default:
        return this.message || 'An unexpected error occurred.';
    }
  }
}

/**
 * Normalizes an Axios error into our ApiError type.
 *
 * **How it works:**
 * 1. Checks if there's a response (HTTP error) or not (network error)
 * 2. Determines error type based on status code or error code
 * 3. Extracts server error message if available
 * 4. Returns normalized ApiError
 *
 * **Why we need this:**
 * - Axios errors have different shapes based on the error type
 * - We want consistent error handling throughout the app
 * - Makes it easy to determine if an error is retryable
 * - Provides user-friendly error messages
 *
 * @param error - Axios error or unknown error
 * @returns Normalized ApiError
 *
 * @example
 * try {
 *   await apiClient.get('/endpoint');
 * } catch (error) {
 *   const apiError = normalizeError(error);
 *   if (apiError.retryable) {
 *     // Retry the request
 *   }
 *   toast.error(apiError.getUserMessage());
 * }
 */
export const normalizeError = (error: unknown): ApiError => {
  // Handle AxiosError
  if (error instanceof AxiosError) {
    const axiosError = error as AxiosError;

    // Network error (no response)
    if (!axiosError.response) {
      // Timeout error
      if (axiosError.code === 'ECONNABORTED' || axiosError.code === 'ETIMEDOUT') {
        return new ApiError(
          'Request timeout',
          ApiErrorType.TIMEOUT,
          undefined,
          axiosError,
          'The request took too long to complete.'
        );
      }

      // Network error
      return new ApiError(
        'Network error',
        ApiErrorType.NETWORK_ERROR,
        undefined,
        axiosError,
        'Unable to reach the server. Please check your connection.'
      );
    }

    // HTTP error (with response)
    const status = axiosError.response.status;
    const serverMessage =
      axiosError.response.data?.message ||
      axiosError.response.data?.detail ||
      axiosError.response.statusText;

    // Determine error type from status code
    let type: ApiErrorType;
    switch (status) {
      case 400:
        type = ApiErrorType.BAD_REQUEST;
        break;
      case 401:
        type = ApiErrorType.UNAUTHORIZED;
        break;
      case 403:
        type = ApiErrorType.FORBIDDEN;
        break;
      case 404:
        type = ApiErrorType.NOT_FOUND;
        break;
      case 500:
      case 502:
      case 503:
      case 504:
        type = ApiErrorType.SERVER_ERROR;
        break;
      default:
        type = ApiErrorType.UNKNOWN;
    }

    return new ApiError(
      `HTTP ${status} error`,
      type,
      status,
      axiosError,
      serverMessage
    );
  }

  // Handle native Error
  if (error instanceof Error) {
    return new ApiError(error.message, ApiErrorType.UNKNOWN);
  }

  // Handle unknown error
  return new ApiError(
    'An unknown error occurred',
    ApiErrorType.UNKNOWN,
    undefined,
    undefined,
    String(error)
  );
};

/**
 * Checks if an error is a network error.
 *
 * @param error - Error to check
 * @returns True if network error
 */
export const isNetworkError = (error: unknown): boolean => {
  const apiError = normalizeError(error);
  return apiError.type === ApiErrorType.NETWORK_ERROR;
};

/**
 * Checks if an error is retryable.
 *
 * @param error - Error to check
 * @returns True if retryable
 */
export const isRetryableError = (error: unknown): boolean => {
  const apiError = normalizeError(error);
  return apiError.retryable;
};

/**
 * Gets a user-friendly error message from any error.
 *
 * @param error - Error to format
 * @returns User-friendly message
 */
export const getUserErrorMessage = (error: unknown): string => {
  const apiError = normalizeError(error);
  return apiError.getUserMessage();
};
