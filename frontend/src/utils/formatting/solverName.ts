/**
 * @fileoverview Solver name formatting utilities
 * @module utils/formatting/solverName
 */

/**
 * Formats a solver name for display.
 * Capitalizes first letter and converts underscores/hyphens to spaces.
 *
 * @param name - Raw solver name from API (e.g., "random", "embedding_based")
 * @returns Formatted solver name (e.g., "Random", "Embedding Based")
 *
 * @example
 * formatSolverName("random") // "Random"
 * formatSolverName("embedding_based") // "Embedding Based"
 * formatSolverName("llm-solver") // "LLM Solver"
 */
export const formatSolverName = (name: string): string => {
  return name
    .split(/[-_]/)
    .map(word => {
      // Special case for common acronyms
      const upper = word.toUpperCase();
      if (['LLM', 'AI', 'ML', 'NLP'].includes(upper)) {
        return upper;
      }
      // Capitalize first letter
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(' ');
};
