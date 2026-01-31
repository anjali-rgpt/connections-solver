/**
 * @fileoverview Header component for application
 * @module components/layout/Header
 */

import React from 'react';
import { usePuzzle } from '@/hooks/api/usePuzzle';

/**
 * Header Component
 *
 * Displays application title and reset button.
 */
export const Header: React.FC = () => {
  const { reset } = usePuzzle();

  return (
    <header className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold">MakingConnectionsAI</h1>
        <button
          onClick={reset}
          className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-lg
            font-semibold transition-colors"
        >
          Reset
        </button>
      </div>
    </header>
  );
};
