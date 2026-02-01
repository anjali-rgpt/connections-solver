/**
 * @fileoverview React Query hook for fetching available solvers
 * @module hooks/api/useSolvers
 */

import { useQuery } from '@tanstack/react-query';
import { listSolvers } from '@/api/solvers';

/**
 * Custom hook for fetching available solver types.
 *
 * Uses React Query for automatic caching and background updates.
 * Data is cached for 5 minutes to reduce API calls.
 *
 * @returns React Query result with solvers array
 *
 * @example
 * const { data, isLoading, error } = useSolvers();
 *
 * if (isLoading) return <Spinner />;
 * if (error) return <Error message={error.message} />;
 *
 * return data?.solvers.map(solver => (
 *   <div key={solver.name}>{solver.description}</div>
 * ));
 */
export const useSolvers = () => {
  return useQuery({
    queryKey: ['solvers'],
    queryFn: async () => {
      const response = await listSolvers();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    refetchOnWindowFocus: false,
  });
};
