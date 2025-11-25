/**
 * Utility functions for formatting numbers and values.
 */

/**
 * Format a decimal value as a percentage.
 * @param value - Decimal value (e.g., 0.85 for 85%)
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted percentage string (e.g., "85.0%")
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a number with a fixed number of decimal places.
 * @param value - Number to format
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted number string
 */
export function formatNumber(value: number, decimals: number = 2): string {
  return value.toFixed(decimals);
}

/**
 * Format a confidence interval as a string.
 * @param lower - Lower bound
 * @param upper - Upper bound
 * @param decimals - Number of decimal places (default: 3)
 * @returns Formatted CI string (e.g., "[0.123, 0.456]")
 */
export function formatCI(
  lower: number,
  upper: number,
  decimals: number = 3
): string {
  return `[${formatNumber(lower, decimals)}, ${formatNumber(upper, decimals)}]`;
}
