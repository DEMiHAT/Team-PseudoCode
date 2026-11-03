/**
 * Centralized Axios HTTP client configuration.
 * Handles base URLs, interceptors, timeout handling, and unified error normalization.
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${BASE_URL.replace(/\/$/, '')}/api/v1`,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    // You can attach authentication tokens (JWT) here in future auth phases
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Return standard response envelope
    return response.data;
  },
  (error) => {
    let normalizedError = {
      success: false,
      message: 'Network or server communication failure',
      status: error.response?.status || 500,
      details: null,
    };

    if (error.response?.data) {
      const data = error.response.data;
      normalizedError.message = data.message || data.detail || normalizedError.message;
      normalizedError.details = data.error || data.details || null;
    } else if (error.code === 'ECONNABORTED') {
      normalizedError.message = 'Request timed out waiting for backend server response.';
    } else if (error.message) {
      normalizedError.message = error.message;
    }

    return Promise.reject(normalizedError);
  }
);

export default apiClient;
