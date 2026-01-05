/**
 * Type definitions for Open-Instruct Dashboard
 */

// Bloom's Taxonomy Levels
export type BloomLevel =
  | 'Remember'
  | 'Understand'
  | 'Apply'
  | 'Analyze'
  | 'Evaluate'
  | 'Create';

// Difficulty Levels for Quiz
export type DifficultyLevel = 'easy' | 'medium' | 'hard';

// Request Options
export interface GenerateObjectivesRequestOptions {
  forceCacheBypass?: boolean;
  includeExplanations?: boolean;
}

// Request Schemas
export interface GenerateObjectivesRequest {
  topic: string;
  targetAudience: string;
  numObjectives: number;
  options?: GenerateObjectivesRequestOptions;
}

export interface GenerateQuizRequest {
  objectiveId: string;
  difficulty: DifficultyLevel;
  numOptions?: number;
}

// Response Schemas
export interface LearningObjectiveResponse {
  id: string;
  verb: string;
  content: string;
  level: BloomLevel;
  explanation?: string;
}

export interface CourseStructureResponse {
  topic: string;
  objectives: LearningObjectiveResponse[];
  generatedAt: string;
  modelVersion: string;
  cacheStatus: 'hit' | 'miss';
}

export interface QuizQuestionResponse {
  quizId: string;
  objectiveId: string;
  stem: string;
  correctAnswer: string;
  distractors: string[];
  explanation: string;
  difficulty: DifficultyLevel;
  generatedAt: string;
}

export interface MetaResponse {
  requestId: string;
  timestamp: string;
  processingTimeMs: number;
}

// Health Check
export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'error';
  ollamaConnected: boolean;
  modelVersion?: string;
  version: string;
  uptimeSeconds: number;
}

// API Response Wrappers
export interface SuccessResponse<T = Record<string, unknown>> {
  success: true;
  data: T;
  meta: MetaResponse;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ErrorResponse {
  success: false;
  error: ErrorDetail;
  meta: MetaResponse;
}

// Stats and Analytics
export interface UsageStats {
  totalCoursesGenerated: number;
  totalQuizzesGenerated: number;
  totalObjectivesGenerated: number;
  averageGenerationTimeMs: number;
  successRate: number;
}

export interface PerformanceStats {
  averageResponseTimeMs: number;
  errorRate: number;
  cacheHitRate: number;
  modelVersion: string;
}

export interface PopularTopic {
  topic: string;
  count: number;
}

export interface BloomLevelDistribution {
  level: BloomLevel;
  count: number;
  percentage: number;
}

// Generation Progress
export interface GenerationProgress {
  stage: 'idle' | 'configuring' | 'generating' | 'validating' | 'complete' | 'error';
  progress: number;
  message: string;
  error?: string;
}

// Component Props Types
export interface CourseGeneratorFormProps {
  onGenerate: (request: GenerateObjectivesRequest) => Promise<void>;
  loading?: boolean;
}

export interface ObjectivesDisplayProps {
  objectives: LearningObjectiveResponse[];
  onExport?: (format: 'json' | 'csv') => void;
  onQuizGenerate?: (objectiveId: string) => void;
}

export interface QuizPreviewProps {
  quiz: QuizQuestionResponse;
  showAnswer?: boolean;
  onRevealAnswer?: () => void;
  onNext?: () => void;
}

export interface AnalyticsDashboardProps {
  usageStats?: UsageStats;
  performanceStats?: PerformanceStats;
  popularTopics?: PopularTopic[];
  bloomDistribution?: BloomLevelDistribution[];
  loading?: boolean;
}

// Utility Types
export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;

export type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: ErrorDetail };

// Event Handlers
export type AsyncCallback = () => Promise<void>;
export type AsyncCallbackWithData<T> = (data: T) => Promise<void>;
