/**
 * @fileoverview Toast context and provider for managing global toast notifications
 * @module components/common/Toast/ToastContext
 */

import React, { createContext, useContext, useState, useCallback, useEffect, useRef, ReactNode } from 'react';
import type { Toast, ToastOptions, ToastPosition } from './types';

/**
 * Context value shape
 */
interface ToastContextValue {
  /** Array of active toasts */
  toasts: Toast[];

  /** Show a success toast */
  success: (message: string, options?: Omit<ToastOptions, 'type'>) => string;

  /** Show an error toast */
  error: (message: string, options?: Omit<ToastOptions, 'type'>) => string;

  /** Show an info toast */
  info: (message: string, options?: Omit<ToastOptions, 'type'>) => string;

  /** Show a warning toast */
  warning: (message: string, options?: Omit<ToastOptions, 'type'>) => string;

  /** Dismiss a specific toast by ID */
  dismiss: (id: string) => void;

  /** Dismiss all toasts */
  dismissAll: () => void;

  /** Current position setting */
  position: ToastPosition;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

/**
 * Props for ToastProvider
 */
interface ToastProviderProps {
  /** Child components */
  children: ReactNode;

  /** Default position for toasts */
  position?: ToastPosition;

  /** Maximum number of toasts to show at once */
  maxToasts?: number;
}

/**
 * ToastProvider Component
 *
 * Provides toast notification functionality to the entire app.
 * Manages the state of all active toasts and provides methods to create/dismiss them.
 *
 * **How it works:**
 * 1. Maintains an array of active toast notifications in state
 * 2. Provides helper methods (success, error, info, warning) to create toasts
 * 3. Automatically dismisses toasts after their duration expires
 * 4. Limits the number of simultaneous toasts to prevent overwhelming the UI
 *
 * **Why we need this:**
 * - Centralized notification management
 * - Consistent UX across the app
 * - Better than browser alerts (non-blocking, customizable, looks professional)
 *
 * @example
 * // In your root App component
 * <ToastProvider>
 *   <App />
 * </ToastProvider>
 *
 * @example
 * // In any component
 * const { success, error } = useToast();
 * success('Puzzle created successfully!');
 * error('Failed to solve puzzle');
 */
export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  position = 'top-right',
  maxToasts = 5,
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  
  // Track timeout IDs for cleanup
  const toastTimersRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  /**
   * Generate a unique ID for a toast
   */
  const generateId = (): string => {
    return `toast-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  };

  /**
   * Dismiss a specific toast
   */
  const dismiss = useCallback((id: string): void => {
    // Clear the timer if it exists
    const timer = toastTimersRef.current.get(id);
    if (timer) {
      clearTimeout(timer);
      toastTimersRef.current.delete(id);
    }
    
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  /**
   * Add a new toast notification
   */
  const addToast = useCallback(
    (message: string, options: ToastOptions = {}): string => {
      const id = generateId();
      const duration = options.duration ?? 5000; // Default 5 seconds

      const newToast: Toast = {
        id,
        type: options.type ?? 'info',
        message,
        title: options.title,
        duration,
        dismissible: options.dismissible ?? true,
      };

      setToasts((prev) => {
        // Limit number of toasts
        const updated = [...prev, newToast];
        if (updated.length > maxToasts) {
          return updated.slice(updated.length - maxToasts);
        }
        return updated;
      });

      // Auto-dismiss after duration (if duration > 0)
      if (duration > 0) {
        const timer = setTimeout(() => {
          dismiss(id);
        }, duration);
        
        // Store timer for cleanup
        toastTimersRef.current.set(id, timer);
      }

      return id;
    },
    [maxToasts, dismiss]
  );

  /**
   * Dismiss all toasts
   */
  const dismissAll = useCallback((): void => {
    // Clear all timers
    toastTimersRef.current.forEach((timer) => clearTimeout(timer));
    toastTimersRef.current.clear();
    
    setToasts([]);
  }, []);

  /**
   * Cleanup effect - clear all timers on unmount
   */
  useEffect(() => {
    return () => {
      // Clear all timers when component unmounts
      toastTimersRef.current.forEach((timer) => clearTimeout(timer));
      toastTimersRef.current.clear();
    };
  }, []);

  /**
   * Helper methods for different toast types
   */
  const success = useCallback(
    (message: string, options?: Omit<ToastOptions, 'type'>): string => {
      return addToast(message, { ...options, type: 'success' });
    },
    [addToast]
  );

  const error = useCallback(
    (message: string, options?: Omit<ToastOptions, 'type'>): string => {
      return addToast(message, { ...options, type: 'error' });
    },
    [addToast]
  );

  const info = useCallback(
    (message: string, options?: Omit<ToastOptions, 'type'>): string => {
      return addToast(message, { ...options, type: 'info' });
    },
    [addToast]
  );

  const warning = useCallback(
    (message: string, options?: Omit<ToastOptions, 'type'>): string => {
      return addToast(message, { ...options, type: 'warning' });
    },
    [addToast]
  );

  const value: ToastContextValue = {
    toasts,
    success,
    error,
    info,
    warning,
    dismiss,
    dismissAll,
    position,
  };

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
};

/**
 * Hook to access toast functionality
 *
 * @returns Toast context methods
 *
 * @throws Error if used outside ToastProvider
 *
 * @example
 * const { success, error, info, warning } = useToast();
 * success('Operation completed!');
 * error('Something went wrong');
 */
export const useToast = (): ToastContextValue => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
