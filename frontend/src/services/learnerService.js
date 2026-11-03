import apiClient from './apiClient';

export const learnerService = {
  /**
   * Fetches learner profile, mastery percentage across all units, and attempt metrics.
   */
  async getProfile(learnerId = 1) {
    return await apiClient.get(`/learners/${learnerId}/profile`);
  },
};
