/**
 * @fileoverview Error Boundary component for catching React errors
 * @module components/common/ErrorBoundary
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  /** Child components to render */
  children: ReactNode;

  /** Optional fallback UI to show when error occurs */
  fallback?: ReactNode;

  /** Optional callback when error occurs */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  /** Whether an error has been caught */
  hasError: boolean;

  /** The caught error */
  error: Error | null;

  /** Additional error information */
  errorInfo: ErrorInfo | null;
}

/**
 * ErrorBoundary Component
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 *
 * **Why we need this:**
 * Without an error boundary, a single error in any component will
 * crash the entire React app, showing a blank page. This provides
 * a safety net to keep the app running even when errors occur.
 *
 * **How it works:**
 * - Wraps around components that might throw errors
 * - Catches errors during rendering, lifecycle methods, and constructors
 * - Shows a user-friendly error message instead of crashing
 * - Allows users to reset and try again
 *
 * **What it doesn't catch:**
 * - Event handlers (use try-catch for those)
 * - Asynchronous code (setTimeout, promises)
 * - Server-side rendering errors
 * - Errors in the error boundary itself
 *
 * @example
 * <ErrorBoundary>
 *   <App />
 * </ErrorBoundary>
 *
 * @example
 * // With custom fallback
 * <ErrorBoundary fallback={<CustomErrorUI />}>
 *   <SomeComponent />
 * </ErrorBoundary>
 *
 * @example
 * // With error callback
 * <ErrorBoundary onError={(error, info) => logToService(error, info)}>
 *   <App />
 * </ErrorBoundary>
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  /**
   * Static method called when an error is thrown.
   * Updates state to trigger fallback UI.
   */
  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Lifecycle method called after an error is caught.
   * Used for logging and side effects.
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log to console in development
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Call optional error callback (for logging to external services)
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  /**
   * Resets the error boundary state, allowing the app to try rendering again.
   */
  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
          <div className="max-w-lg w-full bg-white rounded-lg shadow-xl p-8">
            {/* Error icon */}
            <div className="flex justify-center mb-4">
              <div className="bg-red-100 rounded-full p-4">
                <svg
                  className="w-12 h-12 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
            </div>

            {/* Error message */}
            <h1 className="text-2xl font-bold text-gray-900 text-center mb-2">
              Oops! Something went wrong
            </h1>
            <p className="text-gray-600 text-center mb-6">
              The application encountered an unexpected error. Don't worry, your
              data is safe.
            </p>

            {/* Error details (only in development) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
                <h3 className="text-sm font-semibold text-red-800 mb-2">
                  Error Details (Development Only):
                </h3>
                <pre className="text-xs text-red-700 overflow-auto max-h-40">
                  {this.state.error.toString()}
                  {this.state.errorInfo && (
                    <div className="mt-2">
                      {this.state.errorInfo.componentStack}
                    </div>
                  )}
                </pre>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={this.handleReset}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-md transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-3 px-4 rounded-md transition-colors"
              >
                Go to Home
              </button>
            </div>

            {/* Help text */}
            <p className="text-center text-sm text-gray-500 mt-6">
              If this problem persists, please refresh the page or contact support.
            </p>
          </div>
        </div>
      );
    }

    // No error, render children normally
    return this.props.children;
  }
}
