/**
 * @fileoverview Category input component for puzzle form
 * @module components/layout/Sidebar/CategoryInput
 */

import React from 'react';

interface CategoryInputProps {
  categoryIndex: number;
  categoryName: string;
  words: string[];
  onCategoryNameChange: (index: number, name: string) => void;
  onWordChange: (categoryIndex: number, wordIndex: number, word: string) => void;
}

/**
 * CategoryInput Component
 *
 * Renders input fields for a single category (name + 4 words).
 *
 * @param categoryIndex - Index of this category (0-3)
 * @param categoryName - Current category name
 * @param words - Array of 4 words for this category
 * @param onCategoryNameChange - Callback when category name changes
 * @param onWordChange - Callback when a word changes
 */
export const CategoryInput: React.FC<CategoryInputProps> = ({
  categoryIndex,
  categoryName,
  words,
  onCategoryNameChange,
  onWordChange,
}) => {
  const colors = [
    'border-yellow-400 focus:border-yellow-500',
    'border-green-400 focus:border-green-500',
    'border-blue-400 focus:border-blue-500',
    'border-purple-400 focus:border-purple-500',
  ];

  const colorClass = colors[categoryIndex];

  return (
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Category {categoryIndex + 1}
      </label>

      {/* Category name input */}
      <input
        type="text"
        value={categoryName}
        onChange={(e) => onCategoryNameChange(categoryIndex, e.target.value)}
        placeholder="Category name"
        className={`w-full px-3 py-2 border-2 ${colorClass} rounded-lg
          focus:outline-none focus:ring-2 focus:ring-offset-1 mb-2`}
      />

      {/* Word inputs */}
      <div className="grid grid-cols-2 gap-2">
        {words.map((word, wordIndex) => (
          <input
            key={wordIndex}
            type="text"
            value={word}
            onChange={(e) =>
              onWordChange(categoryIndex, wordIndex, e.target.value)
            }
            placeholder={`Word ${wordIndex + 1}`}
            className={`px-3 py-2 border-2 ${colorClass} rounded-lg
              focus:outline-none focus:ring-2 focus:ring-offset-1 text-sm`}
          />
        ))}
      </div>
    </div>
  );
};
