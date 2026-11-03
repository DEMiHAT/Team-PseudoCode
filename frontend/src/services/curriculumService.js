import apiClient from './apiClient';

export const curriculumService = {
  /**
   * Fetches all IT22301 syllabus concepts with problem count and student mastery.
   */
  async getConcepts(learnerId = 1) {
    return await apiClient.get('/concepts', { params: { learner_id: learnerId } });
  },

  /**
   * Fetches problems, optionally filtered by concept ID.
   */
  async getProblems(conceptId = null) {
    const params = conceptId ? { concept_id: conceptId } : {};
    return await apiClient.get('/problems', { params });
  },

  /**
   * Fetches full workspace problem details including starter code and test cases.
   */
  async getProblemDetail(problemId) {
    return await apiClient.get(`/problems/${problemId}`);
  },
};

