/**
 * @fileoverview Main application component
 * @module App
 */

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header, Sidebar } from '@/components/layout';
import { SolverGrid } from '@/components/solver';
import { useSolvers } from '@/hooks/api/useSolvers';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

/**
 * AppContent Component
 *
 * Main application content (wrapped by QueryClientProvider).
 */
const AppContent: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { data: solversData, isLoading, error } = useSolvers();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <Header />

      {/* Main content */}
      <main className="container mx-auto px-6 py-8">
        {/* Loading state */}
        {isLoading && (
          <div className="text-center text-gray-600 py-12">
            Loading solvers...
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800 font-semibold">Failed to load solvers</p>
            <p className="text-red-600 text-sm mt-2">{error.message}</p>
          </div>
        )}

        {/* Solver grids */}
        {solversData?.solvers && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {solversData.solvers.map((solver) => (
              <SolverGrid key={solver.name} solver={solver} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!isLoading && !error && !solversData?.solvers?.length && (
          <div className="text-center text-gray-500 py-12">
            No solvers available
          </div>
        )}
      </main>

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
    </div>
  );
};

/**
 * App Component
 *
 * Root application component with providers.
 */
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
};

export default App;
