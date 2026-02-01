/**
 * @fileoverview Type definitions for Toast notification system
 * @module components/common/Toast/types
 */

/**
 * Toast notification types
 */
export type ToastType = 'success' | 'error' | 'info' | 'warning';

/**
 * Position where toast appears on screen
 */
export type ToastPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';

/**
 * Individual toast notification
 */
export interface Toast {
  /** Unique identifier for the toast */
  id: string;

  /** Type of notification (success, error, info, warning) */
  type: ToastType;

  /** Message to display */
  message: string;

  /** Optional title */
  title?: string;

  /** Duration in milliseconds before auto-dismiss (0 = no auto-dismiss) */
  duration?: number;

  /** Whether toast can be dismissed by user */
  dismissible?: boolean;
}

/**
 * Options for creating a new toast
 */
export interface ToastOptions {
  /** Type of notification */
  type?: ToastType;

  /** Optional title */
  title?: string;

  /** Duration in milliseconds (default: 5000) */
  duration?: number;

  /** Whether toast can be dismissed (default: true) */
  dismissible?: boolean;

  /** Toast position (default: 'top-right') */
  position?: ToastPosition;
}
