import apiClient from './apiClient';

export const executionService = {
  /**
   * Executes student code against sample/visible test cases.
   */
  async runCode({ learnerId = 1, problemId, code, language = 'java' }) {
    return await apiClient.post('/execution/run', {
      learner_id: learnerId,
      problem_id: problemId,
      code,
      language,
    });
  },

  /**
   * Submits code for official grading, logs Attempt & CodeSubmission,
   * updates BKT skill mastery probabilities and detects misconceptions.
   */
  async submitCode({ learnerId = 1, problemId, code, language = 'java' }) {
    return await apiClient.post('/execution/submit', {
      learner_id: learnerId,
      problem_id: problemId,
      code,
      language,
    });
  },

  /**
   * Retrieves past submission history for a student.
   */
  async getSubmissionHistory(studentId = 1) {
    return await apiClient.get(`/execution/history/${studentId}`);
  },
};
