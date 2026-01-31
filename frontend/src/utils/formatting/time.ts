/**
 * @fileoverview Time formatting utilities
 * @module utils/formatting/time
 */

/**
 * Formats execution time in milliseconds to a human-readable string.
 *
 * @param ms - Time in milliseconds
 * @returns Formatted time string
 *
 * @example
 * formatExecutionTime(1234) // "1234ms"
 * formatExecutionTime(5678) // "5.68s"
 */
export const formatExecutionTime = (ms: number): string => {
  if (ms < 1000) {
    return `${ms}ms`;
  }
  return `${(ms / 1000).toFixed(2)}s`;
};
