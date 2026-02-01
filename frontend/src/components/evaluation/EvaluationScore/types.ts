/**
 * @fileoverview Type definitions for EvaluationScore module
 * @module components/evaluation/EvaluationScore/types
 */

import type { EvaluationMetrics } from '@/types/api';

/**
 * Props for EvaluationScore component.
 */
export interface EvaluationScoreProps {
  /** Evaluation metrics to display */
  metrics: EvaluationMetrics;
}

/**
 * Props for MetricCard component.
 */
export interface MetricCardProps {
  /** Label for the metric */
  label: string;

  /** Value to display (formatted string) */
  value: string;

  /** Optional color scheme */
  color?: 'default' | 'success' | 'warning' | 'error';
}
