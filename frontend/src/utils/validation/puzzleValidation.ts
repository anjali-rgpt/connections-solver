/**
 * @fileoverview Validation utilities for puzzle input
 * @module utils/validation/puzzleValidation
 */

/**
 * Result of puzzle validation
 */
export interface PuzzleValidationResult {
  /** Whether the puzzle is valid */
  valid: boolean;

  /** Validation errors (if any) */
  errors: string[];
}

/**
 * Validates puzzle input before submission.
 *
 * **Validation Rules:**
 * 1. Must have exactly 4 categories
 * 2. Each category must have a non-empty name
 * 3. Each category must have exactly 4 words
 * 4. All words must be non-empty strings
 * 5. No duplicate words across all categories
 * 6. Words cannot contain only whitespace
 *
 * **Why validation is important:**
 * - Prevents invalid data from reaching the backend
 * - Provides clear feedback to users about what's wrong
 * - Catches errors early (better UX than backend errors)
 * - Reduces unnecessary API calls
 *
 * @param categories - Array of category objects with name and words
 * @returns Validation result with errors list
 *
 * @example
 * const result = validatePuzzleInput([
 *   { name: 'Animals', words: ['dog', 'cat', 'bird', 'fish'] },
 *   { name: 'Colors', words: ['red', 'blue', 'green', 'yellow'] },
 *   // ... 2 more categories
 * ]);
 *
 * if (!result.valid) {
 *   console.error('Validation errors:', result.errors);
 * }
 */
export const validatePuzzleInput = (
  categories: Array<{ name: string; words: string[] }>
): PuzzleValidationResult => {
  const errors: string[] = [];

  // Rule 1: Must have exactly 4 categories
  if (categories.length !== 4) {
    errors.push('Puzzle must have exactly 4 categories');
    return { valid: false, errors };
  }

  // Track all words for duplicate checking
  const allWords: string[] = [];

  // Validate each category
  categories.forEach((category, catIndex) => {
    const catNum = catIndex + 1;

    // Rule 2: Category name cannot be empty
    if (!category.name || category.name.trim() === '') {
      errors.push(`Category ${catNum}: Name cannot be empty`);
    }

    // Rule 3: Must have exactly 4 words
    if (category.words.length !== 4) {
      errors.push(`Category ${catNum}: Must have exactly 4 words`);
      return; // Skip word validation for this category
    }

    // Rule 4 & 6: Validate each word
    category.words.forEach((word, wordIndex) => {
      const wordNum = wordIndex + 1;

      if (!word || word.trim() === '') {
        errors.push(
          `Category ${catNum}, Word ${wordNum}: Cannot be empty or whitespace`
        );
      } else {
        // Store trimmed word for duplicate checking
        allWords.push(word.trim().toLowerCase());
      }
    });
  });

  // Rule 5: Check for duplicate words
  const wordSet = new Set<string>();
  const duplicates = new Set<string>();

  allWords.forEach((word) => {
    if (wordSet.has(word)) {
      duplicates.add(word);
    } else {
      wordSet.add(word);
    }
  });

  if (duplicates.size > 0) {
    errors.push(
      `Duplicate words found: ${Array.from(duplicates).join(', ')}`
    );
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Validates a single category input.
 *
 * **Validation Rules:**
 * - Category name must not be empty
 * - Must have exactly 4 words
 * - Words must not be empty
 * - Words must not be only whitespace
 *
 * @param categoryName - Name of the category
 * @param words - Array of 4 words
 * @returns Validation result
 *
 * @example
 * const result = validateCategory('Animals', ['dog', 'cat', 'bird', 'fish']);
 * if (!result.valid) {
 *   console.error('Category errors:', result.errors);
 * }
 */
export const validateCategory = (
  categoryName: string,
  words: string[]
): PuzzleValidationResult => {
  const errors: string[] = [];

  // Validate category name
  if (!categoryName || categoryName.trim() === '') {
    errors.push('Category name cannot be empty');
  }

  // Validate word count
  if (words.length !== 4) {
    errors.push('Category must have exactly 4 words');
  }

  // Validate each word
  words.forEach((word, index) => {
    if (!word || word.trim() === '') {
      errors.push(`Word ${index + 1} cannot be empty`);
    }
  });

  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Checks if a word already exists in the puzzle.
 *
 * **Use case:**
 * Real-time validation as user types to prevent duplicate words.
 *
 * @param word - Word to check
 * @param categories - Existing categories
 * @param excludeCategory - Optional category index to exclude from check
 * @param excludeWord - Optional word index to exclude from check
 * @returns True if word is duplicate, false otherwise
 *
 * @example
 * // Check if 'dog' is already used
 * const isDupe = isDuplicateWord('dog', categories);
 * if (isDupe) {
 *   showError('This word is already used');
 * }
 */
export const isDuplicateWord = (
  word: string,
  categories: Array<{ name: string; words: string[] }>,
  excludeCategory?: number,
  excludeWord?: number
): boolean => {
  if (!word || word.trim() === '') {
    return false;
  }

  const normalizedWord = word.trim().toLowerCase();

  for (let catIndex = 0; catIndex < categories.length; catIndex++) {
    for (let wordIndex = 0; wordIndex < categories[catIndex].words.length; wordIndex++) {
      // Skip if this is the word we're editing
      if (catIndex === excludeCategory && wordIndex === excludeWord) {
        continue;
      }

      const existingWord = categories[catIndex].words[wordIndex];
      if (existingWord && existingWord.trim().toLowerCase() === normalizedWord) {
        return true;
      }
    }
  }

  return false;
};

/**
 * Sanitizes a word by trimming whitespace and normalizing case.
 *
 * **Use case:**
 * Clean user input before saving or submission.
 *
 * @param word - Word to sanitize
 * @returns Sanitized word
 *
 * @example
 * const clean = sanitizeWord('  DOG  '); // Returns 'DOG'
 */
export const sanitizeWord = (word: string): string => {
  return word.trim().toUpperCase();
};

/**
 * Formats a list of validation errors into a user-friendly message.
 *
 * @param errors - Array of error messages
 * @returns Formatted error message
 *
 * @example
 * const message = formatValidationErrors(['Error 1', 'Error 2']);
 * // Returns: "Validation errors:\n• Error 1\n• Error 2"
 */
export const formatValidationErrors = (errors: string[]): string => {
  if (errors.length === 0) {
    return '';
  }

  if (errors.length === 1) {
    return errors[0];
  }

  return 'Validation errors:\n' + errors.map((err) => `• ${err}`).join('\n');
};
