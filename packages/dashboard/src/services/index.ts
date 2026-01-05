/**
 * Services Index
 * Export all API services for easy importing
 */

// Ollama service for direct LLM integration
export { ollamaService, default as ollama } from './ollama';

// Export API client for any remaining backend API needs
export { apiClient, ApiError } from './api';
