/**
 * frontend/src/hooks/useApiHealth.ts
 * Periodic health status polling hook for the FastAPI backend.
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { HealthStatus } from '../types/api';

export function useApiHealth(pollIntervalMs: number = 20000) {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isOnline, setIsOnline] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      const data = await api.healthCheck();
      setHealth(data);
      setIsOnline(data.status === 'healthy' && data.model_loaded && data.database_connected);
      setError(null);
    } catch (err: unknown) {
      setIsOnline(false);
      setHealth(null);
      setError(err instanceof Error ? err.message : 'Backend unreachable');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, pollIntervalMs);
    return () => clearInterval(interval);
  }, [checkHealth, pollIntervalMs]);

  return { health, isOnline, isLoading, error, refetch: checkHealth };
}
