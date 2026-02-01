/**
 * @fileoverview Loading spinner component
 * @module components/common/LoadingSpinner
 */

import React from 'react';

/**
 * LoadingSpinner Component
 *
 * Displays an animated spinning circle to indicate loading state.
 *
 * @example
 * {isLoading && <LoadingSpinner />}
 */
export const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex items-center justify-center p-8">
      <div
        className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  );
};
