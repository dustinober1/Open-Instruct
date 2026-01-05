/**
 * Hooks Index
 * Export all custom hooks for easy importing
 */

// Settings and configuration
export { useSettings } from './useSettings';
export { useOllama } from './useOllama';

// Health and connection
export { useHealthCheck } from './useHealthCheck';

// Generation hooks
export { useGenerateObjectives, useGenerateObjectives as useObjectives } from './useOllama';
export { useGenerateQuiz, useGenerateQuiz as useQuiz } from './useOllamaQuiz';
