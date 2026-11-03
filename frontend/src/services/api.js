/**
 * API Service for communicating with the FastAPI backend.
 * Uses environment variable VITE_API_BASE_URL with localhost fallback.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Checks backend health and database connectivity.
 * @returns {Promise<{success: boolean, data?: any, error?: string}>}
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (err) {
    console.error('API Health check failed:', err);
    return {
      success: false,
      error: err.message || 'Unable to reach backend service',
    };
  }
}

export { API_BASE_URL };

