/**
 * @fileoverview Individual toast notification component
 * @module components/common/Toast/Toast
 */

import React, { useState } from 'react';
import type { Toast as ToastType } from './types';

interface ToastProps {
  /** Toast data */
  toast: ToastType;

  /** Callback when toast is dismissed */
  onDismiss: (id: string) => void;
}

/**
 * Toast Component
 *
 * Displays a single toast notification with appropriate styling and icon
 * based on the toast type (success, error, info, warning).
 *
 * **Features:**
 * - Auto-dismiss with progress bar
 * - Manual dismiss button
 * - Color-coded by type
 * - Slide-in animation
 * - Icon for each type
 *
 * **Styling by type:**
 * - Success: Green with checkmark icon
 * - Error: Red with X icon
 * - Warning: Yellow with exclamation icon
 * - Info: Blue with info icon
 */
export const Toast: React.FC<ToastProps> = ({ toast, onDismiss }) => {
  const [isExiting, setIsExiting] = useState(false);

  /**
   * Handle dismiss with exit animation
   */
  const handleDismiss = () => {
    setIsExiting(true);
    // Wait for animation to complete before removing
    setTimeout(() => {
      onDismiss(toast.id);
    }, 300);
  };

  /**
   * Get styling classes based on toast type
   */
  const getTypeStyles = () => {
    switch (toast.type) {
      case 'success':
        return {
          container: 'bg-green-50 border-green-400',
          icon: 'text-green-600',
          title: 'text-green-900',
          message: 'text-green-700',
        };
      case 'error':
        return {
          container: 'bg-red-50 border-red-400',
          icon: 'text-red-600',
          title: 'text-red-900',
          message: 'text-red-700',
        };
      case 'warning':
        return {
          container: 'bg-yellow-50 border-yellow-400',
          icon: 'text-yellow-600',
          title: 'text-yellow-900',
          message: 'text-yellow-700',
        };
      case 'info':
      default:
        return {
          container: 'bg-blue-50 border-blue-400',
          icon: 'text-blue-600',
          title: 'text-blue-900',
          message: 'text-blue-700',
        };
    }
  };

  /**
   * Get icon SVG based on toast type
   */
  const getIcon = () => {
    const styles = getTypeStyles();

    switch (toast.type) {
      case 'success':
        return (
          <svg
            className={`w-5 h-5 ${styles.icon}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'error':
        return (
          <svg
            className={`w-5 h-5 ${styles.icon}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'warning':
        return (
          <svg
            className={`w-5 h-5 ${styles.icon}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'info':
      default:
        return (
          <svg
            className={`w-5 h-5 ${styles.icon}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
        );
    }
  };

  const styles = getTypeStyles();

  return (
    <div
      className={`
        ${styles.container}
        ${isExiting ? 'animate-slide-out' : 'animate-slide-in'}
        flex items-start gap-3 p-4 rounded-lg border-2 shadow-lg
        max-w-md w-full pointer-events-auto
      `}
      role="alert"
    >
      {/* Icon */}
      <div className="flex-shrink-0 pt-0.5">{getIcon()}</div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {toast.title && (
          <p className={`${styles.title} font-semibold text-sm mb-1`}>
            {toast.title}
          </p>
        )}
        <p className={`${styles.message} text-sm`}>{toast.message}</p>
      </div>

      {/* Dismiss button */}
      {toast.dismissible && (
        <button
          onClick={handleDismiss}
          className={`${styles.icon} flex-shrink-0 hover:opacity-70 transition-opacity`}
          aria-label="Dismiss notification"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      )}
    </div>
  );
};
