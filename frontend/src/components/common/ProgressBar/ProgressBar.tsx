/**
 * @fileoverview Progress bar component for solver execution
 * @module components/common/ProgressBar
 */

import React, { useEffect, useState } from 'react';

interface ProgressBarProps {
  /** Current status message */
  status?: string;
}

/**
 * ProgressBar Component
 *
 * Displays an animated progress bar with status message.
 * Shows indeterminate progress (animated bar moving back and forth).
 *
 * @param status - Status message to display (e.g., "Solving puzzle...")
 *
 * @example
 * <ProgressBar status="Analyzing word relationships..." />
 */
export const ProgressBar: React.FC<ProgressBarProps> = ({
  status = 'Processing...'
}) => {
  const [dots, setDots] = useState('');

  // Animate the dots after the status message
  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="py-8 px-4">
      <div className="mb-4">
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-full bg-blue-600 rounded-full animate-progress-bar w-1/3"></div>
        </div>
      </div>
      <p className="text-center text-gray-700 font-medium">
        {status}{dots}
      </p>
    </div>
  );
};
