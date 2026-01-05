/**
 * Custom hook for health check operations
 * Checks Ollama connection status
 */

import { useState, useEffect, useCallback } from 'react';
import { ollamaService } from '../services/ollama';

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  ollamaConnected: boolean;
  ollamaModel?: string;
  timestamp: string;
}

interface UseHealthCheckResult {
  data: HealthResponse | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export const useHealthCheck = (): UseHealthCheckResult => {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await ollamaService.checkConnection();
      
      setData({
        status: result.connected ? 'healthy' : 'unhealthy',
        ollamaConnected: result.connected,
        ollamaModel: result.model,
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to check health');
      setError(error);
      setData({
        status: 'unhealthy',
        ollamaConnected: false,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();

    // Poll for health status every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  return { data, loading, error, refetch: fetchHealth };
};

export default useHealthCheck;
