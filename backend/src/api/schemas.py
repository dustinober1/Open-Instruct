"""
Pydantic schemas for API request and response validation.

This module defines all request and response models used by the FastAPI endpoints,
ensuring type safety and validation for all API interactions.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class DifficultyLevel(str, Enum):
    """Quiz difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# Request Schemas
class GenerateObjectivesRequestOptions(BaseModel):
    """Options for objectives generation."""

    force_cache_bypass: bool = Field(
        default=False, description="Skip cache and regenerate"
    )
    include_explanations: bool = Field(
        default=False, description="Add verb explanations to objectives"
    )


class GenerateObjectivesRequest(BaseModel):
    """Request schema for generating learning objectives."""

    topic: str = Field(..., min_length=1, max_length=200, description="Course topic")
    target_audience: str = Field(
        ..., min_length=1, max_length=200, description="Target audience for the course"
    )
    num_objectives: int = Field(
        default=6, ge=1, le=12, description="Number of objectives to generate"
    )
    options: GenerateObjectivesRequestOptions = Field(
        default_factory=GenerateObjectivesRequestOptions
    )


class GenerateQuizRequest(BaseModel):
    """Request schema for generating quiz questions."""

    objective_id: str = Field(
        ..., pattern=r"^LO-\d{3}$", description="Learning objective ID (e.g., LO-001)"
    )
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM, description="Quiz difficulty level"
    )
    num_options: int = Field(
        default=4, ge=4, le=4, description="Total number of answer options"
    )


# Response Schemas
class LearningObjectiveResponse(BaseModel):
    """Response schema for a single learning objective."""

    id: str = Field(..., description="Objective identifier")
    verb: str = Field(..., description="Bloom's Taxonomy verb")
    content: str = Field(..., description="Objective content")
    level: str = Field(..., description="Bloom's cognitive level")
    explanation: Optional[str] = Field(None, description="Optional explanation")


class CourseStructureResponse(BaseModel):
    """Response schema for generated course structure."""

    topic: str = Field(..., description="Course topic")
    objectives: List[LearningObjectiveResponse] = Field(
        ..., description="List of learning objectives"
    )
    generated_at: datetime = Field(..., description="Generation timestamp")
    model_version: str = Field(..., description="LLM model used")
    cache_status: str = Field(..., description="Cache hit/miss status")


class QuizQuestionResponse(BaseModel):
    """Response schema for generated quiz question."""

    quiz_id: str = Field(..., description="Quiz question identifier")
    objective_id: str = Field(..., description="Associated learning objective ID")
    stem: str = Field(..., description="Question text")
    correct_answer: str = Field(..., description="Correct answer")
    distractors: List[str] = Field(
        ..., min_length=3, max_length=3, description="Incorrect answer choices"
    )
    explanation: str = Field(..., description="Answer explanation")
    difficulty: str = Field(..., description="Quiz difficulty")
    generated_at: datetime = Field(..., description="Generation timestamp")


class MetaResponse(BaseModel):
    """Metadata included in all API responses."""

    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(..., description="Response timestamp")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(..., description="Health status")
    ollama_connected: bool = Field(..., description="Ollama connection status")
    model_version: Optional[str] = Field(None, description="Configured model version")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Server uptime in seconds")


class SuccessResponse(BaseModel):
    """Standard success response wrapper."""

    success: bool = Field(default=True, description="Request success status")
    data: Dict = Field(..., description="Response data")
    meta: MetaResponse = Field(..., description="Response metadata")


class ErrorDetail(BaseModel):
    """Error detail information."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    success: bool = Field(default=False, description="Request success status")
    error: ErrorDetail = Field(..., description="Error information")
    meta: MetaResponse = Field(..., description="Response metadata")
