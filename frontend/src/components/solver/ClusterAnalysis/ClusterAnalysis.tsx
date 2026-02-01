/**
 * @fileoverview Cluster analysis display component
 * @module components/solver/ClusterAnalysis
 */

import React, { useState } from 'react';
import { formatPercentage } from '@/utils/formatting';
import type { ClusterSolverMetadata } from '@/types/api';

export interface ClusterAnalysisProps {
  metadata: ClusterSolverMetadata;
}

/**
 * ClusterAnalysis Component
 *
 * Displays algorithm selection reasoning and cluster quality metrics
 * for the cluster solver. Shows:
 * - Algorithm chosen and why
 * - Key metrics that informed the decision
 * - Cluster quality scores
 *
 * @param metadata - Cluster solver metadata from solve result
 *
 * @example
 * <ClusterAnalysis metadata={solverResult.solver_metadata} />
 */
export const ClusterAnalysis: React.FC<ClusterAnalysisProps> = ({ metadata }) => {
  const [isOpen, setIsOpen] = useState(true);

  const { algorithm_selection, cluster_quality } = metadata;

  // Format algorithm name for display
  const algorithmName = {
    kmeans: 'K-Means',
    agglomerative: 'Agglomerative',
    dbscan: 'DBSCAN',
  }[algorithm_selection.chosen] || algorithm_selection.chosen;

  return (
    <div className="border-2 border-gray-200 rounded-lg overflow-hidden mb-4">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-gradient-to-r from-blue-50 to-cyan-50
          hover:from-blue-100 hover:to-cyan-100 transition-colors
          flex items-center justify-between group"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-gray-800">
            Cluster Analysis
          </span>
          <span className="text-xs font-medium text-blue-700 bg-white px-2 py-1 rounded border border-blue-200">
            {algorithmName}
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
          {/* Algorithm Selection Section */}
          <div className="mb-6">
            <h3 className="text-sm font-bold text-gray-700 mb-2">
              Algorithm Selection
            </h3>
            <p className="text-sm text-gray-600 mb-3">
              {algorithm_selection.reason}
            </p>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-3">
              <MetricCard
                label="Distance CV"
                value={algorithm_selection.metrics.distance_cv.toFixed(3)}
                tooltip="Coefficient of variation in word distances"
              />
              <MetricCard
                label="PCA Variance"
                value={formatPercentage(algorithm_selection.metrics.pca_variance_2d)}
                tooltip="Variance explained by top 2 components"
              />
              {algorithm_selection.metrics.separation_ratio !== undefined && (
                <>
                  <MetricCard
                    label="Separation Ratio"
                    value={algorithm_selection.metrics.separation_ratio.toFixed(2)}
                    tooltip="Ratio of between-cluster to within-cluster distance"
                  />
                </>
              )}
            </div>
          </div>

          {/* Cluster Quality Section */}
          <div>
            <h3 className="text-sm font-bold text-gray-700 mb-2">
              Cluster Quality
            </h3>

            {/* Average Confidence */}
            <div className="mb-3">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Average Confidence</span>
                <span className="font-semibold text-gray-800">
                  {formatPercentage(cluster_quality.avg_confidence)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${cluster_quality.avg_confidence * 100}%` }}
                />
              </div>
            </div>

            {/* Per-Cluster Confidence */}
            <div className="grid grid-cols-2 gap-2">
              {cluster_quality.confidence_per_cluster.map((conf, idx) => (
                <div
                  key={idx}
                  className="bg-white p-2 rounded border border-gray-200"
                >
                  <div className="text-xs text-gray-600 mb-1">
                    Cluster {idx + 1}
                  </div>
                  <div className="text-sm font-semibold text-gray-800">
                    {formatPercentage(conf)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * MetricCard Component
 * Displays a single metric with label and optional tooltip
 */
const MetricCard: React.FC<{
  label: string;
  value: string;
  tooltip?: string;
}> = ({ label, value, tooltip }) => {
  return (
    <div
      className="bg-white p-3 rounded border border-gray-200"
      title={tooltip}
    >
      <div className="text-xs text-gray-600 mb-1">{label}</div>
      <div className="text-lg font-bold text-gray-800">{value}</div>
    </div>
  );
};
