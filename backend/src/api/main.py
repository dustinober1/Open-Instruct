"""
FastAPI application for Open-Instruct educational content generation.

This module provides REST API endpoints for generating learning objectives
and quiz questions using DSPy modules and Ollama LLM integration.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

from src.api.schemas import (
    CourseStructureResponse,
    ErrorDetail,
    ErrorResponse,
    GenerateObjectivesRequest,
    HealthResponse,
    LearningObjectiveResponse,
    MetaResponse,
    SuccessResponse,
)
from src.core.dspy_client import configure_dspy, get_model_info, test_ollama_connection
from src.core.models import CourseStructure, LearningObjective
from src.modules.architect import Architect

# Initialize FastAPI app
app = FastAPI(
    title="Open-Instruct API",
    description="AI-powered educational content generation using Bloom's Taxonomy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track server start time for uptime calculation
_start_time = time.time()


def get_request_id() -> str:
    """Generate a unique request ID."""
    return f"req_{uuid.uuid4().hex[:12]}"


def create_meta_response(request_id: str, start_time: float) -> MetaResponse:
    """Create metadata response with processing time."""
    return MetaResponse(
        request_id=request_id,
        timestamp=datetime.utcnow(),
        processing_time_ms=int((time.time() - start_time) * 1000),
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Check API and Ollama connection status.

    Returns:
        Health status including Ollama connectivity and model information
    """
    try:
        # Test Ollama connection
        ollama_status = test_ollama_connection()
        ollama_connected = ollama_status["status"] == "ok"

        # Get model info
        model_info = get_model_info()

        return HealthResponse(
            status="healthy" if ollama_connected else "degraded",
            ollama_connected=ollama_connected,
            model_version=model_info.get("model"),
            version="1.0.0",
            uptime_seconds=time.time() - _start_time,
        )

    except Exception as e:
        return HealthResponse(
            status="error",
            ollama_connected=False,
            model_version=None,
            version="1.0.0",
            uptime_seconds=time.time() - _start_time,
        )


@app.post(
    "/api/v1/generate/objectives",
    response_model=SuccessResponse,
    tags=["Objectives"],
)
async def generate_objectives(request: Request, body: GenerateObjectivesRequest):
    """
    Generate learning objectives using Bloom's Taxonomy.

    Args:
        body: Request containing topic, target audience, and number of objectives

    Returns:
        Generated course structure with learning objectives

    Raises:
        HTTPException: If generation fails or validation errors occur
    """
    request_id = get_request_id()
    start_time = time.time()

    try:
        # Configure DSPy if not already configured
        try:
            configure_dspy()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Failed to configure LLM connection",
                    "details": {"error": str(e)},
                },
            )

        # Initialize Architect module
        architect = Architect()

        # Generate objectives
        try:
            course_structure: CourseStructure = architect.generate_objectives(
                topic=body.topic,
                target_audience=body.target_audience,
                num_objectives=body.num_objectives,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "GENERATION_FAILED",
                    "message": str(e),
                    "details": {"topic": body.topic, "target_audience": body.target_audience},
                },
            )

        # Convert to response format
        objectives_response = [
            LearningObjectiveResponse(
                id=obj.id,
                verb=obj.verb,
                content=obj.content,
                level=obj.level.value,
                explanation=None,  # Can be added later if options.include_explanations
            )
            for obj in course_structure.objectives
        ]

        course_response = CourseStructureResponse(
            topic=course_structure.topic,
            objectives=objectives_response,
            generated_at=datetime.utcnow(),
            model_version=get_model_info().get("model", "unknown"),
            cache_status="miss",  # TODO: Implement caching
        )

        # Create success response
        success_response = SuccessResponse(
            success=True,
            data=course_response.model_dump(),
            meta=create_meta_response(request_id, start_time),
        )

        # Convert datetime objects to ISO format strings
        return json.loads(json.dumps(success_response.model_dump(), cls=CustomJSONEncoder))

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except ValidationError as e:
        # Pydantic validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": {"errors": e.errors()},
            },
        )

    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(e)},
            },
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom exception handler for HTTP exceptions."""
    request_id = get_request_id()

    # Extract error detail
    if isinstance(exc.detail, dict):
        error_detail = exc.detail
    else:
        error_detail = {
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "details": None,
        }

    error_response = ErrorResponse(
        success=False,
        error=ErrorDetail(**error_detail),
        meta=MetaResponse(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            processing_time_ms=0,
        ),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=json.loads(json.dumps(error_response.model_dump(), cls=CustomJSONEncoder)),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Custom exception handler for general exceptions."""
    request_id = get_request_id()

    error_response = ErrorResponse(
        success=False,
        error=ErrorDetail(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"error_type": type(exc).__name__, "error": str(exc)},
        ),
        meta=MetaResponse(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            processing_time_ms=0,
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=json.loads(json.dumps(error_response.model_dump(), cls=CustomJSONEncoder)),
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Open-Instruct API",
        "version": "1.0.0",
        "description": "AI-powered educational content generation",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
