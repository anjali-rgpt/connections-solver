/**
 * @fileoverview React Query hook for fetching available puzzles
 * @module hooks/api/usePuzzles
 */

import { useQuery } from '@tanstack/react-query';
import { listPuzzles } from '@/api/puzzles';

/**
 * Custom hook for fetching all available puzzles.
 *
 * Uses React Query for automatic caching and background updates.
 * Data is cached for 30 seconds and refetches when window regains focus.
 *
 * @returns React Query result with puzzles array
 *
 * @example
 * const { data: puzzles, isLoading, error, refetch } = usePuzzles();
 *
 * if (isLoading) return <Spinner />;
 * if (error) return <Error message={error.message} />;
 *
 * return puzzles?.map(puzzle => (
 *   <PuzzleItem key={puzzle.puzzle_id} puzzle={puzzle} />
 * ));
 */
export const usePuzzles = () => {
  return useQuery({
    queryKey: ['puzzles'],
    queryFn: async () => {
      const response = await listPuzzles();
      return response.data.puzzles; // Extract puzzles array from paginated response
    },
    staleTime: 30 * 1000, // Cache for 30 seconds
    refetchOnWindowFocus: true, // Refetch when window regains focus
  });
};
