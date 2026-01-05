/**
 * API Service for Open-Instruct Dashboard
 * Handles all HTTP communication with the backend API
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import type {
  ApiResponse,
  GenerateObjectivesRequest,
  GenerateQuizRequest,
  CourseStructureResponse,
  QuizQuestionResponse,
  HealthResponse,
  SuccessResponse,
  ErrorResponse,
} from '../types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 60000; // 60 seconds for long-running operations

// Custom error class for API errors
export class ApiError extends Error {
  public readonly code: string;
  public readonly details?: Record<string, unknown>;
  public readonly requestId?: string;
  public readonly statusCode: number;

  constructor(
    message: string,
    code: string,
    statusCode: number,
    details?: Record<string, unknown>,
    requestId?: string
  ) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
    this.requestId = requestId;
    this.statusCode = statusCode;
  }
}

// Create axios instance with default config
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor for adding request ID
  client.interceptors.request.use(
    (config) => {
      const requestId = `req_${Date.now().toString(36)}_${Math.random().toString(36).substr(2, 9)}`;
      config.headers['X-Request-ID'] = requestId;
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response) {
        const { status, data } = error.response;

        // Handle API error response format
        if (typeof data === 'object' && data !== null && 'error' in (data as object)) {
          const errorResponse = data as ErrorResponse;
          throw new ApiError(
            errorResponse.error.message,
            errorResponse.error.code || 'API_ERROR',
            status,
            errorResponse.error.details,
            errorResponse.meta?.requestId
          );
        }

        // Handle standard HTTP errors
        const message = (data as { message?: string })?.message || error.message;
        throw new ApiError(message, `HTTP_${status}`, status);
      }

      if (error.request) {
        throw new ApiError(
          'Network error: Unable to reach the server',
          'NETWORK_ERROR',
          0,
          { originalError: error.message }
        );
      }

      throw new ApiError(
        error.message || 'An unexpected error occurred',
        'UNKNOWN_ERROR',
        0
      );
    }
  );

  return client;
};

const apiClient = createApiClient();

/**
 * Make an API request with proper error handling
 */
async function apiRequest<T>(
  config: AxiosRequestConfig
): Promise<SuccessResponse<T>> {
  try {
    const response = await apiClient.request<SuccessResponse<T>>(config);

    if (!response.data.success) {
      throw new ApiError(
        'Request failed',
        'REQUEST_FAILED',
        response.status,
        response.data
      );
    }

    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      'An unexpected error occurred',
      'UNKNOWN_ERROR',
      0,
      { originalError: String(error) }
    );
  }
}

/**
 * Health Check API
 */
export const healthCheck = async (): Promise<HealthResponse> => {
  const response = await apiRequest<HealthResponse>({
    method: 'GET',
    url: '/health',
  });
  return response.data;
};

/**
 * Generate Learning Objectives
 */
export const generateObjectives = async (
  request: GenerateObjectivesRequest
): Promise<CourseStructureResponse> => {
  const response = await apiRequest<CourseStructureResponse>({
    method: 'POST',
    url: '/api/v1/generate/objectives',
    data: request,
  });
  return response.data;
};

/**
 * Generate Quiz Question
 */
export const generateQuiz = async (
  request: GenerateQuizRequest
): Promise<QuizQuestionResponse> => {
  const response = await apiRequest<QuizQuestionResponse>({
    method: 'POST',
    url: '/api/v1/generate/quiz',
    data: request,
  });
  return response.data;
};

/**
 * Get Usage Statistics (if endpoint exists)
 */
export const getUsageStats = async (): Promise<Record<string, unknown>> => {
  const response = await apiRequest<Record<string, unknown>>({
    method: 'GET',
    url: '/api/v1/stats/usage',
  });
  return response.data;
};

/**
 * Get Performance Statistics (if endpoint exists)
 */
export const getPerformanceStats = async (): Promise<Record<string, unknown>> => {
  const response = await apiRequest<Record<string, unknown>>({
    method: 'GET',
    url: '/api/v1/stats/performance',
  });
  return response.data;
};

/**
 * Get all courses (if endpoint exists)
 */
export const getCourses = async (): Promise<Record<string, unknown>[]> => {
  const response = await apiRequest<Record<string, unknown>[]>({
    method: 'GET',
    url: '/api/v1/courses',
  });
  return response.data;
};

/**
 * Delete a course (if endpoint exists)
 */
export const deleteCourse = async (courseId: string): Promise<void> => {
  await apiRequest<null>({
    method: 'DELETE',
    url: `/api/v1/courses/${courseId}`,
  });
};

/**
 * Export course to format (if endpoint exists)
 */
export const exportCourse = async (
  courseId: string,
  format: 'json' | 'csv'
): Promise<Blob> => {
  const response = await apiClient.get(`/api/v1/export/${format}`, {
    params: { courseId },
    responseType: 'blob',
  });
  return response.data;
};

// Export types for consumers
export type { ApiError };

// Export singleton instance for advanced use cases
export { apiClient };
