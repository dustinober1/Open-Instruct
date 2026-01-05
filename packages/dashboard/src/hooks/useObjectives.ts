/**
 * Custom hook for objectives generation
 */

import { useState, useCallback } from 'react';
import { generateObjectives, ApiError } from '../services/api';
import type {
  GenerateObjectivesRequest,
  CourseStructureResponse,
  GenerationProgress,
} from '../types';

interface UseGenerateObjectivesResult {
  data: CourseStructureResponse | null;
  loading: boolean;
  error: ApiError | null;
  progress: GenerationProgress;
  generate: (request: GenerateObjectivesRequest) => Promise<void>;
  reset: () => void;
}

const initialProgress: GenerationProgress = {
  stage: 'idle',
  progress: 0,
  message: '',
};

export const useGenerateObjectives = (): UseGenerateObjectivesResult => {
  const [data, setData] = useState<CourseStructureResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [progress, setProgress] = useState<GenerationProgress>(initialProgress);

  const updateProgress = useCallback(
    (stage: GenerationProgress['stage'], message: string, progressPercent?: number) => {
      setProgress({
        stage,
        progress: progressPercent ?? progress.progress,
        message,
      });
    },
    []
  );

  const generate = useCallback(
    async (request: GenerateObjectivesRequest) => {
      setLoading(true);
      setError(null);
      setData(null);
      setProgress({ stage: 'configuring', progress: 10, message: 'Configuring generation parameters...' });

      try {
        updateProgress('generating', 'Generating learning objectives...', 30);

        // Simulate progress for better UX (actual progress comes from backend)
        const progressInterval = setInterval(() => {
          setProgress((prev) => {
            if (prev.progress < 80) {
              return { ...prev, progress: prev.progress + 5 };
            }
            return prev;
          });
        }, 500);

        const result = await generateObjectives(request);

        clearInterval(progressInterval);
        updateProgress('validating', 'Validating generated objectives...', 90);

        // Simulate validation time
        await new Promise((resolve) => setTimeout(resolve, 500));

        setData(result);
        updateProgress('complete', 'Objectives generated successfully!', 100);
      } catch (err) {
        const apiError = err instanceof ApiError ? err : new ApiError(
          'Failed to generate objectives',
          'GENERATION_FAILED',
          0
        );
        setError(apiError);
        setProgress({
          stage: 'error',
          progress: 0,
          message: apiError.message,
          error: apiError.details?.suggestion as string | undefined,
        });
      } finally {
        setLoading(false);
      }
    },
    [updateProgress]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setProgress(initialProgress);
  }, []);

  return { data, loading, error, progress, generate, reset };
};

export default useGenerateObjectives;
