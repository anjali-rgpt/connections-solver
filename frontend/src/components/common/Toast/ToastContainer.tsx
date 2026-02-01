/**
 * @fileoverview Container for rendering all active toasts
 * @module components/common/Toast/ToastContainer
 */

import React from 'react';
import { useToast } from './ToastContext';
import { Toast } from './Toast';

/**
 * ToastContainer Component
 *
 * Renders all active toasts in a fixed position on the screen.
 * Automatically positions toasts based on the provider's position setting.
 *
 * **How it works:**
 * 1. Subscribes to the toast context
 * 2. Renders each active toast
 * 3. Positions the container based on settings
 * 4. Stacks toasts vertically with spacing
 *
 * **Usage:**
 * Place this component once in your App root, after the ToastProvider.
 * It will automatically render toasts as they're created.
 *
 * @example
 * <ToastProvider>
 *   <App />
 *   <ToastContainer />
 * </ToastProvider>
 */
export const ToastContainer: React.FC = () => {
  const { toasts, dismiss, position } = useToast();

  /**
   * Get positioning classes based on position setting
   */
  const getPositionClasses = (): string => {
    switch (position) {
      case 'top-left':
        return 'top-4 left-4 items-start';
      case 'top-center':
        return 'top-4 left-1/2 -translate-x-1/2 items-center';
      case 'top-right':
        return 'top-4 right-4 items-end';
      case 'bottom-left':
        return 'bottom-4 left-4 items-start';
      case 'bottom-center':
        return 'bottom-4 left-1/2 -translate-x-1/2 items-center';
      case 'bottom-right':
        return 'bottom-4 right-4 items-end';
      default:
        return 'top-4 right-4 items-end';
    }
  };

  // Don't render if no toasts
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      className={`
        fixed z-50 flex flex-col gap-3 pointer-events-none
        ${getPositionClasses()}
      `}
      aria-live="polite"
      aria-atomic="false"
    >
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onDismiss={dismiss} />
      ))}
    </div>
  );
};
