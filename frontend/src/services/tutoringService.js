import apiClient from './apiClient';

export const tutoringService = {
  /**
   * Requests progressive scaffolding hint (Tiers 1-4).
   */
  async requestScaffold({ learnerId = 1, problemId, currentCode, requestedLevel, compilerError, failingTestInput }) {
    return await apiClient.post('/tutoring/scaffold', {
      learner_id: learnerId,
      problem_id: problemId,
      current_code: currentCode,
      requested_level: requestedLevel,
      compiler_error: compilerError,
      failing_test_input: failingTestInput,
    });
  },

  /**
   * Diagnoses cognitive misconceptions from student code and errors.
   */
  async diagnoseMisconceptions({ code, problemId, compilerError, failingTestInput }) {
    return await apiClient.post('/tutoring/diagnose', {
      code,
      problem_id: problemId,
      compiler_error: compilerError,
      failing_test_input: failingTestInput,
    });
  },
};

