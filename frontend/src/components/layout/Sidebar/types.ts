/**
 * @fileoverview Type definitions for Sidebar component
 * @module components/layout/Sidebar/types
 */

/**
 * Props for Sidebar component.
 */
export interface SidebarProps {
  /** Controls whether sidebar is visible */
  isOpen: boolean;

  /** Callback invoked when toggle button is clicked */
  onToggle: () => void;
}

/**
 * Represents a category being edited in the form.
 */
export interface CategoryInput {
  /** Category name */
  name: string;

  /** Array of 4 words for this category */
  words: string[];
}
