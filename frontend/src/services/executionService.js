import apiClient from './apiClient';

export const executionService = {
  /**
   * Executes student code via Judge0, runs test cases, and updates BKT mastery state.
   */
  async runCode({ learnerId = 1, problemId, code, language = 'java' }) {
    return await apiClient.post('/execution/run', {
      learner_id: learnerId,
      problem_id: problemId,
      code,
      language,
    });
  },
};

