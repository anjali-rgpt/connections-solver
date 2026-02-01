/**
 * @fileoverview Array shuffling utilities
 * @module utils/array/shuffle
 */

/**
 * Shuffles an array using the Fisher-Yates algorithm.
 * Returns a new array without mutating the original.
 *
 * @param array - The array to shuffle
 * @returns A new shuffled array
 *
 * @example
 * const shuffled = shuffleArray([1, 2, 3, 4]);
 * // shuffled might be [3, 1, 4, 2]
 */
export const shuffleArray = <T>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};
