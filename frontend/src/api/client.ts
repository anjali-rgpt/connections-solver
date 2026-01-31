/**
 * @fileoverview Core API client configuration
 * @module api/client
 */

import axios from 'axios';

/**
 * Axios instance configured for MakingConnectionsAI API.
 * All API requests should use this instance for consistent config.
 *
 * Features:
 * - Base URL set to /api/v1 (proxied to backend in dev)
 * - JSON content type headers
 * - 10 second timeout
 * - Error logging interceptor
 */
export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// Request/response interceptors for logging, auth, etc.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.message);
    return Promise.reject(error);
  }
);
