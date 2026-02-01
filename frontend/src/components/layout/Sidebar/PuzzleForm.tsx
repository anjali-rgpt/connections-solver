/**
 * @fileoverview Puzzle creation form component
 * @module components/layout/Sidebar/PuzzleForm
 */

import React, { useState } from 'react';
import { CategoryInput } from './CategoryInput';
import { usePuzzle } from '@/hooks/api/usePuzzle';
import { useSolvers } from '@/hooks/api/useSolvers';
import type { CategoryInput as CategoryInputType } from './types';

/**
 * PuzzleForm Component
 *
 * Form for creating new puzzles with 4 categories of 4 words each.
 * Handles input validation, state management, and submission.
 *
 * Features:
 * - 4 category inputs with color-coded borders
 * - Validation for complete categories
 * - Automatic solver execution on submission
 * - Reset functionality
 */
export const PuzzleForm: React.FC = () => {
  const { createPuzzle, solveWithAllSolvers } = usePuzzle();
  const { data: solversData } = useSolvers();

  // Initialize 4 empty categories
  const [categories, setCategories] = useState<CategoryInputType[]>(
    Array(4).fill(null).map(() => ({
      name: '',
      words: ['', '', '', ''],
    }))
  );

  const handleCategoryNameChange = (index: number, name: string) => {
    const updated = [...categories];
    updated[index] = { ...updated[index], name };
    setCategories(updated);
  };

  const handleWordChange = (
    categoryIndex: number,
    wordIndex: number,
    word: string
  ) => {
    const updated = [...categories];
    updated[categoryIndex].words[wordIndex] = word;
    setCategories(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation: Check all fields are filled
    const isValid = categories.every(
      (cat) =>
        cat.name.trim() !== '' &&
        cat.words.every((word) => word.trim() !== '')
    );

    if (!isValid) {
      alert('Please fill in all category names and words');
      return;
    }

    // Extract all words (flattened array of 16 words)
    const allWords = categories.flatMap((cat) => cat.words);

    // Build solution structure
    const solution = {
      categories: categories.map((cat) => ({
        name: cat.name,
        words: cat.words,
      })),
    };

    try {
      // Create puzzle
      const puzzle = await createPuzzle.mutateAsync({
        words: allWords,
        solution,
      });

      // Solve with all available solvers in parallel
      if (solversData?.solvers && puzzle) {
        await solveWithAllSolvers(puzzle.puzzle_id, solversData.solvers);
      }
    } catch (error) {
      console.error('Failed to create puzzle or solve:', error);
      alert('Failed to create puzzle. Please try again.');
    }
  };

  const handleReset = () => {
    setCategories(
      Array(4).fill(null).map(() => ({
        name: '',
        words: ['', '', '', ''],
      }))
    );
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4 text-xs text-gray-600 bg-blue-50 p-3 rounded-lg border border-blue-200">
        <p className="font-semibold text-blue-800 mb-1">💡 Tip: Multi-word phrases</p>
        <p>You can use multi-word phrases like "NEW YORK" or "HOT DOG". The solver will automatically handle them.</p>
      </div>

      {categories.map((category, index) => (
        <CategoryInput
          key={index}
          categoryIndex={index}
          categoryName={category.name}
          words={category.words}
          onCategoryNameChange={handleCategoryNameChange}
          onWordChange={handleWordChange}
        />
      ))}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={createPuzzle.isPending}
          className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold
            hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
            transition-colors"
        >
          {createPuzzle.isPending ? 'Creating...' : 'Create & Solve'}
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="px-4 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold
            hover:bg-gray-300 transition-colors"
        >
          Reset
        </button>
      </div>
    </form>
  );
};
