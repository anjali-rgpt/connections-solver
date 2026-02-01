/**
 * @fileoverview Cluster visualization component
 * @module components/solver/ClusterVisualization
 */

import React, { useState, useMemo } from 'react';
import type { ClusterSolverMetadata } from '@/types/api';

export interface ClusterVisualizationProps {
  metadata: ClusterSolverMetadata;
}

/**
 * ClusterVisualization Component
 *
 * Renders a 2D scatter plot of word embeddings using t-SNE projection.
 * Shows:
 * - Word positions in 2D semantic space
 * - Color-coded clusters
 * - Outliers highlighted with red borders
 * - Legend for cluster colors
 *
 * @param metadata - Cluster solver metadata with visualization data
 *
 * @example
 * <ClusterVisualization metadata={solverResult.solver_metadata} />
 */
export const ClusterVisualization: React.FC<ClusterVisualizationProps> = ({
  metadata,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const { coordinates_2d, outliers } = metadata.visualization;

  // Calculate viewport bounds with padding
  const bounds = useMemo(() => {
    // Filter out null/invalid coordinates
    const validCoords = coordinates_2d.filter(p => p.x != null && p.y != null && isFinite(p.x) && isFinite(p.y));
    
    if (validCoords.length === 0) {
      // Return default bounds if no valid coordinates
      return { minX: -1, maxX: 1, minY: -1, maxY: 1, width: 2, height: 2 };
    }
    
    const xs = validCoords.map((p) => p.x);
    const ys = validCoords.map((p) => p.y);

    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    // Add 10% padding
    const paddingX = (maxX - minX) * 0.1 || 1;
    const paddingY = (maxY - minY) * 0.1 || 1;

    return {
      minX: minX - paddingX,
      maxX: maxX + paddingX,
      minY: minY - paddingY,
      maxY: maxY + paddingY,
      width: maxX - minX + 2 * paddingX,
      height: maxY - minY + 2 * paddingY,
    };
  }, [coordinates_2d]);

  // Cluster colors (matching Connections game colors)
  const clusterColors = ['#F59E0B', '#10B981', '#3B82F6', '#8B5CF6']; // yellow, green, blue, purple

  // Normalize coordinates to SVG viewport
  const normalizePoint = (x: number, y: number) => {
    const svgWidth = 600;
    const svgHeight = 400;

    const normalizedX =
      ((x - bounds.minX) / bounds.width) * svgWidth;
    const normalizedY =
      ((y - bounds.minY) / bounds.height) * svgHeight;

    return { x: normalizedX, y: normalizedY };
  };

  return (
    <div className="border-2 border-gray-200 rounded-lg overflow-hidden mb-4">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-gradient-to-r from-purple-50 to-pink-50
          hover:from-purple-100 hover:to-pink-100 transition-colors
          flex items-center justify-between group"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-gray-800">
            Embedding Visualization
          </span>
          <span className="text-xs font-medium text-purple-700 bg-white px-2 py-1 rounded border border-purple-200">
            {metadata.visualization.method.toUpperCase()}
          </span>
        </div>
        <svg
          className={`w-5 h-5 text-gray-600 transition-transform duration-200
            ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Collapsible Content */}
      {isOpen && (
        <div className="p-4 bg-gray-50">
          <p className="text-sm text-gray-600 mb-4">
            2D projection of word embeddings showing semantic relationships.
            Words are color-coded by cluster, outliers have red borders.
          </p>

          {/* SVG Visualization */}
          <div className="bg-white p-4 rounded border border-gray-200">
            <svg
              viewBox="0 0 600 400"
              className="w-full h-auto"
              style={{ maxHeight: '400px' }}
            >
              {/* Background */}
              <rect width="600" height="400" fill="#fafafa" />

              {/* Grid lines */}
              <g opacity="0.2">
                {[0, 150, 300, 450, 600].map((x) => (
                  <line
                    key={`v-${x}`}
                    x1={x}
                    y1="0"
                    x2={x}
                    y2="400"
                    stroke="#ccc"
                    strokeWidth="1"
                  />
                ))}
                {[0, 100, 200, 300, 400].map((y) => (
                  <line
                    key={`h-${y}`}
                    x1="0"
                    y1={y}
                    x2="600"
                    y2={y}
                    stroke="#ccc"
                    strokeWidth="1"
                  />
                ))}
              </g>

              {/* Data points */}
              {coordinates_2d
                .filter(point => point.x != null && point.y != null && isFinite(point.x) && isFinite(point.y))
                .map((point, idx) => {
                const { x, y } = normalizePoint(point.x, point.y);
                const color = clusterColors[point.cluster];
                const isOutlier = outliers.includes(idx);

                return (
                  <g key={idx}>
                    {/* Point circle */}
                    <circle
                      cx={x}
                      cy={y}
                      r="8"
                      fill={color}
                      stroke={isOutlier ? '#dc2626' : color}
                      strokeWidth={isOutlier ? '2' : '1'}
                      opacity="0.8"
                    />

                    {/* Word label */}
                    <text
                      x={x}
                      y={y - 12}
                      textAnchor="middle"
                      fontSize="10"
                      fontWeight="500"
                      fill="#374151"
                    >
                      {point.word}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-4 items-center justify-center text-sm">
            {clusterColors.map((color, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full border border-gray-300"
                  style={{ backgroundColor: color }}
                />
                <span className="text-gray-700">Cluster {idx + 1}</span>
              </div>
            ))}
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-gray-400 border-2 border-red-600" />
              <span className="text-gray-700">Outlier</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
