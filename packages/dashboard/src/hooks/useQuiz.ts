/**
 * Custom hook for quiz generation
 */

import { useState, useCallback } from 'react';
import { generateQuiz, ApiError } from '../services/api';
import type { GenerateQuizRequest, QuizQuestionResponse } from '../types';

interface UseGenerateQuizResult {
  data: QuizQuestionResponse | null;
  loading: boolean;
  error: ApiError | null;
  generate: (request: GenerateQuizRequest) => Promise<void>;
  reset: () => void;
}

export const useGenerateQuiz = (): UseGenerateQuizResult => {
  const [data, setData] = useState<QuizQuestionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const generate = useCallback(async (request: GenerateQuizRequest) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const result = await generateQuiz(request);
      setData(result);
    } catch (err) {
      const apiError = err instanceof ApiError ? err : new ApiError(
        'Failed to generate quiz',
        'QUIZ_GENERATION_FAILED',
        0
      );
      setError(apiError);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
  }, []);

  return { data, loading, error, generate, reset };
};

export default useGenerateQuiz;
