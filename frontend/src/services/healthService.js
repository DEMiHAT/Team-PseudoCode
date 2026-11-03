import apiClient from './apiClient';

export const healthService = {
  /**
   * Fetches health status of backend and external integrations.
   */
  async getSystemHealth() {
    return await apiClient.get('/health');
  },
};

