/**
 * Utility functions for Open-Instruct Dashboard
 */

import type { BloomLevel, DifficultyLevel } from '../types';

/**
 * Get color for Bloom's level
 */
export const getBloomLevelColor = (level: BloomLevel): string => {
  const colors: Record<BloomLevel, string> = {
    Remember: '#8B5CF6', // Purple
    Understand: '#3B82F6', // Blue
    Apply: '#10B981', // Green
    Analyze: '#F59E0B', // Amber
    Evaluate: '#EF4444', // Red
    Create: '#EC4899', // Pink
  };
  return colors[level] || '#6B7280';
};

/**
 * Get color for difficulty level
 */
export const getDifficultyColor = (difficulty: DifficultyLevel): string => {
  const colors: Record<DifficultyLevel, string> = {
    easy: '#10B981', // Green
    medium: '#F59E0B', // Amber
    hard: '#EF4444', // Red
  };
  return colors[difficulty] || '#6B7280';
};

/**
 * Get Bloom's level order for sorting
 */
export const getBloomLevelOrder = (level: BloomLevel): number => {
  const order: Record<BloomLevel, number> = {
    Remember: 1,
    Understand: 2,
    Apply: 3,
    Analyze: 4,
    Evaluate: 5,
    Create: 6,
  };
  return order[level] || 0;
};

/**
 * Format milliseconds to human readable string
 */
export const formatDuration = (ms: number): string => {
  if (ms < 1000) {
    return `${ms}ms`;
  }
  if (ms < 60000) {
    return `${(ms / 1000).toFixed(1)}s`;
  }
  return `${(ms / 60000).toFixed(1)}m`;
};

/**
 * Format timestamp to readable date
 */
export const formatDate = (isoString: string): string => {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Validate topic input
 */
export const validateTopic = (topic: string): string | null => {
  const trimmed = topic.trim();
  if (!trimmed) {
    return 'Topic is required';
  }
  if (trimmed.length < 3) {
    return 'Topic must be at least 3 characters';
  }
  if (trimmed.length > 200) {
    return 'Topic must be less than 200 characters';
  }
  return null;
};

/**
 * Validate target audience input
 */
export const validateTargetAudience = (audience: string): string | null => {
  const trimmed = audience.trim();
  if (!trimmed) {
    return 'Target audience is required';
  }
  if (trimmed.length < 3) {
    return 'Target audience must be at least 3 characters';
  }
  if (trimmed.length > 200) {
    return 'Target audience must be less than 200 characters';
  }
  return null;
};

/**
 * Validate number of objectives
 */
export const validateNumObjectives = (num: number): string | null => {
  if (num < 1) {
    return 'At least 1 objective is required';
  }
  if (num > 12) {
    return 'Maximum 12 objectives allowed';
  }
  return null;
};

/**
 * Export data to JSON file
 */
export const exportToJson = (data: unknown, filename: string): void => {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Export data to CSV file
 */
export const exportToCsv = (data: Record<string, unknown>[], filename: string): void => {
  if (data.length === 0) {
    return;
  }

  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map((row) =>
      headers.map((header) => {
        const value = row[header];
        const stringValue = String(value ?? '');
        // Escape quotes and wrap in quotes if contains comma or quote
        if (stringValue.includes(',') || stringValue.includes('"')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    ),
  ].join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Debounce function
 */
export const debounce = <T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

/**
 * Calculate percentage
 */
export const calculatePercentage = (value: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
};
