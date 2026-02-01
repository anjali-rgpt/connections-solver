/**
 * @fileoverview Percentage formatting utilities
 * @module utils/formatting/percentage
 */

/**
 * Formats a decimal number as a percentage string.
 *
 * @param value - Decimal value between 0 and 1
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted percentage string
 *
 * @example
 * formatPercentage(0.756) // "75.6%"
 * formatPercentage(0.5, 0) // "50%"
 */
export const formatPercentage = (value: number, decimals = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};
