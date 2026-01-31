/**
 * @fileoverview Type definitions for SolverGrid module
 * @module components/solver/SolverGrid/types
 */

import type { SolverInfo } from '@/types/api';

/**
 * Props for SolverGrid component.
 */
export interface SolverGridProps {
  /** Solver information (name and description) */
  solver: SolverInfo;
}
