/**
 * Custom hook for health check operations
 */

import { useState, useEffect, useCallback } from 'react';
import { healthCheck, ApiError } from '../services/api';
import type { HealthResponse } from '../types';

interface UseHealthCheckResult {
  data: HealthResponse | null;
  loading: boolean;
  error: ApiError | null;
  refetch: () => Promise<void>;
}

export const useHealthCheck = (): UseHealthCheckResult => {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await healthCheck();
      setData(result);
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError(
        'Failed to check health',
        'HEALTH_CHECK_FAILED',
        0
      ));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();

    // Optional: Poll for health status every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  return { data, loading, error, refetch: fetchHealth };
};

export default useHealthCheck;
