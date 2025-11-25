/**
 * Custom React hooks for common patterns.
 */

import { useState, useCallback } from 'react';

/**
 * Hook for managing async operations with loading and error states.
 *
 * @param operation - Async function to execute
 * @returns Tuple of [isLoading, execute, error]
 *   - isLoading: Boolean indicating if operation is in progress
 *   - execute: Function to execute the operation
 *   - error: Error object if operation failed, null otherwise
 *
 * @example
 * ```typescript
 * const [isLoading, runMetaAnalysis, error] = useAsyncOperation(performMetaAnalysis);
 *
 * const handleRun = async () => {
 *   const result = await runMetaAnalysis(paperIds);
 *   if (result) {
 *     setResult(result);
 *   } else if (error) {
 *     showError('Error', error.message);
 *   }
 * };
 * ```
 */
export function useAsyncOperation<T, Args extends unknown[]>(
  operation: (...args: Args) => Promise<T>
): [boolean, (...args: Args) => Promise<T | undefined>, Error | null] {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(
    async (...args: Args): Promise<T | undefined> => {
      setIsLoading(true);
      setError(null);
      try {
        const result = await operation(...args);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        return undefined;
      } finally {
        setIsLoading(false);
      }
    },
    [operation]
  );

  return [isLoading, execute, error];
}
