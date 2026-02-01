/**
 * @fileoverview Core API client configuration with enhanced error handling
 * @module api/client
 */

import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import { normalizeError, isRetryableError } from './errors';

/**
 * Retry configuration
 */
const RETRY_CONFIG = {
  /** Maximum number of retry attempts */
  maxRetries: 3,

  /** Initial delay in milliseconds */
  initialDelay: 1000,

  /** Maximum delay in milliseconds */
  maxDelay: 10000,

  /** Multiplier for exponential backoff */
  backoffMultiplier: 2,
};

/**
 * Axios instance configured for MakingConnectionsAI API.
 * All API requests should use this instance for consistent config.
 *
 * **Features:**
 * - Base URL set to /api/v1 (proxied to backend in dev)
 * - JSON content type headers
 * - 30 second timeout (increased for Word2Vec model loading)
 * - Enhanced error handling with normalization
 * - Automatic retry logic for transient failures
 * - Request cancellation support
 */
export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000, // 30 seconds to allow Word2Vec model to load
});

/**
 * Calculates exponential backoff delay with jitter.
 *
 * **Why exponential backoff:**
 * - Gives the server time to recover
 * - Prevents thundering herd problem
 * - Jitter prevents all clients from retrying at the same time
 *
 * @param retryCount - Current retry attempt (0-indexed)
 * @returns Delay in milliseconds
 */
const calculateBackoff = (retryCount: number): number => {
  const delay = Math.min(
    RETRY_CONFIG.initialDelay * Math.pow(RETRY_CONFIG.backoffMultiplier, retryCount),
    RETRY_CONFIG.maxDelay
  );

  // Add jitter (random 0-100ms) to prevent synchronized retries
  const jitter = Math.random() * 100;

  return delay + jitter;
};

/**
 * Waits for a specified duration.
 *
 * @param ms - Milliseconds to wait
 * @returns Promise that resolves after delay
 */
const wait = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Retry interceptor for handling transient failures.
 *
 * **How it works:**
 * 1. Intercepts failed requests
 * 2. Checks if error is retryable (network, timeout, 5xx)
 * 3. Retries with exponential backoff
 * 4. Gives up after max retries
 *
 * **Why we need this:**
 * - Handles temporary network issues automatically
 * - Improves reliability without user intervention
 * - Better UX (user doesn't see every transient error)
 */
apiClient.interceptors.response.use(
  // Success response - pass through
  (response) => response,

  // Error response - retry logic
  async (error: AxiosError) => {
    const config = error.config as AxiosRequestConfig & {
      __retryCount?: number;
    };

    // Initialize retry count
    if (!config.__retryCount) {
      config.__retryCount = 0;
    }

    // Check if we should retry
    const shouldRetry =
      config.__retryCount < RETRY_CONFIG.maxRetries &&
      isRetryableError(error);

    if (shouldRetry) {
      config.__retryCount++;

      // Calculate backoff delay
      const delay = calculateBackoff(config.__retryCount - 1);

      console.warn(
        `API request failed, retrying in ${delay}ms (attempt ${config.__retryCount}/${RETRY_CONFIG.maxRetries})`,
        error.message
      );

      // Wait before retrying
      await wait(delay);

      // Retry the request
      return apiClient(config);
    }

    // Normalize error before rejecting
    const normalizedError = normalizeError(error);

    console.error('API Error:', {
      type: normalizedError.type,
      message: normalizedError.message,
      statusCode: normalizedError.statusCode,
      userMessage: normalizedError.getUserMessage(),
      retryable: normalizedError.retryable,
    });

    return Promise.reject(normalizedError);
  }
);

/**
 * Request interceptor for logging (development only).
 */
if (process.env.NODE_ENV === 'development') {
  apiClient.interceptors.request.use(
    (config) => {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('API Request Error:', error);
      return Promise.reject(error);
    }
  );
}

/**
 * Creates an AbortController for request cancellation.
 *
 * **How to use:**
 * ```typescript
 * const controller = createAbortController();
 *
 * // Make request with cancellation support
 * apiClient.get('/endpoint', {
 *   signal: controller.signal
 * });
 *
 * // Cancel the request
 * controller.abort();
 * ```
 *
 * @returns AbortController instance
 */
export const createAbortController = (): AbortController => {
  return new AbortController();
};
