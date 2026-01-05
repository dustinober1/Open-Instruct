"""
FastAPI application for Open-Instruct educational content generation.

This module provides REST API endpoints for generating learning objectives
and quiz questions using DSPy modules and Ollama LLM integration.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

from src.api.objective_store import get_objective_store
from src.api.schemas import (
    CourseStructureResponse,
    ErrorDetail,
    ErrorResponse,
    GenerateObjectivesRequest,
    GenerateQuizRequest,
    HealthResponse,
    LearningObjectiveResponse,
    MetaResponse,
    QuizQuestionResponse,
    SuccessResponse,
)
from src.core.dspy_client import configure_dspy, get_model_info, test_ollama_connection
from src.core.models import CourseStructure, LearningObjective
from src.modules.assessor import Assessor
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

    logger.info(
        f"[{request_id}] Generating objectives",
        extra={
            "request_id": request_id,
            "topic": body.topic,
            "target_audience": body.target_audience,
            "num_objectives": body.num_objectives
        }
    )

    try:
        # Configure DSPy if not already configured
        try:
            configure_dspy()
        except Exception as e:
            logger.error(f"[{request_id}] Failed to configure DSPy: {e}")
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

            # Store objectives in the objective store for quiz generation later
            objective_store = get_objective_store()
            objective_store.add_objectives(course_structure.objectives)

            logger.info(
                f"[{request_id}] Successfully generated {len(course_structure.objectives)} objectives",
                extra={"request_id": request_id, "objective_count": len(course_structure.objectives)}
            )

        except ValueError as e:
            logger.error(f"[{request_id}] Objective generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "GENERATION_FAILED",
                    "message": str(e),
                    "details": {
                        "topic": body.topic,
                        "target_audience": body.target_audience,
                        "suggestion": "Try rephrasing your topic or target audience with more specific details"
                    },
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
        logger.error(f"[{request_id}] Validation error: {e}")
        # Pydantic validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": {
                    "errors": e.errors(),
                    "suggestion": "Check that all required fields are present and correctly formatted"
                },
            },
        )

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {
                    "error": str(e),
                    "suggestion": "Please try again. If the problem persists, contact support with the request ID"
                },
            },
        )


@app.post(
    "/api/v1/generate/quiz",
    response_model=SuccessResponse,
    tags=["Quizzes"],
)
async def generate_quiz(request: Request, body: GenerateQuizRequest):
    """
    Generate a quiz question for a learning objective.

    Args:
        body: Request containing objective_id and difficulty level

    Returns:
        Generated quiz question with stem, correct answer, distractors, and explanation

    Raises:
        HTTPException: If generation fails or objective not found
    """
    request_id = get_request_id()
    start_time = time.time()

    logger.info(
        f"[{request_id}] Generating quiz",
        extra={
            "request_id": request_id,
            "objective_id": body.objective_id,
            "difficulty": body.difficulty.value
        }
    )

    try:
        # Retrieve objective from store
        objective_store = get_objective_store()
        objective = objective_store.get_objective(body.objective_id)

        if not objective:
            logger.warning(
                f"[{request_id}] Objective not found: {body.objective_id}",
                extra={"request_id": request_id, "objective_id": body.objective_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "OBJECTIVE_NOT_FOUND",
                    "message": f"Learning objective '{body.objective_id}' not found",
                    "details": {
                        "objective_id": body.objective_id,
                        "suggestion": "First generate learning objectives using /api/v1/generate/objectives endpoint"
                    },
                },
            )

        # Configure DSPy if not already configured
        try:
            configure_dspy()
        except Exception as e:
            logger.error(f"[{request_id}] Failed to configure DSPy: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Failed to configure LLM connection",
                    "details": {
                        "error": str(e),
                        "suggestion": "Check that Ollama is running and accessible"
                    },
                },
            )

        # Initialize Assessor module
        assessor = Assessor()

        # Generate quiz with timeout handling
        import concurrent.futures

        try:
            # Use ThreadPoolExecutor to enforce timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    assessor.generate_quiz,
                    objective=objective,
                    context=None,  # Could be extended to include course context
                )

                try:
                    # Wait for completion with 30 second timeout
                    quiz_question = future.result(timeout=30)

                except concurrent.futures.TimeoutError:
                    # Cancel the future if it's still running
                    future.cancel()
                    raise TimeoutError("Quiz generation exceeded 30 second timeout")

        except TimeoutError as e:
            logger.error(f"[{request_id}] Quiz generation timeout: {e}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "code": "GENERATION_TIMEOUT",
                    "message": "Quiz generation exceeded 30 second timeout",
                    "details": {
                        "objective_id": body.objective_id,
                        "timeout_seconds": 30,
                        "suggestion": "The LLM took too long to respond. Try again or consider using a faster model"
                    },
                },
            )
        except ValueError as e:
            logger.error(f"[{request_id}] Quiz generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "GENERATION_FAILED",
                    "message": str(e),
                    "details": {
                        "objective_id": body.objective_id,
                        "objective_text": f"{objective.verb} {objective.content}",
                        "suggestion": "Try generating a quiz for a different objective, or rephrase the objective"
                    },
                },
            )

        logger.info(
            f"[{request_id}] Successfully generated quiz",
            extra={
                "request_id": request_id,
                "quiz_stem_length": len(quiz_question.stem),
                "distractor_count": len(quiz_question.distractors)
            }
        )

        # Convert to response format
        quiz_response = QuizQuestionResponse(
            quiz_id=f"quiz_{uuid.uuid4().hex[:12]}",
            objective_id=body.objective_id,
            stem=quiz_question.stem,
            correct_answer=quiz_question.correct_answer,
            distractors=quiz_question.distractors,
            explanation=quiz_question.explanation,
            difficulty=body.difficulty.value,
            generated_at=datetime.utcnow(),
        )

        # Create success response
        success_response = SuccessResponse(
            success=True,
            data=quiz_response.model_dump(),
            meta=create_meta_response(request_id, start_time),
        )

        # Convert datetime objects to ISO format strings
        return json.loads(json.dumps(success_response.model_dump(), cls=CustomJSONEncoder))

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except ValidationError as e:
        logger.error(f"[{request_id}] Validation error: {e}")
        # Pydantic validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": {
                    "errors": e.errors(),
                    "suggestion": "Check that objective_id format is LO-XXX (e.g., LO-001)"
                },
            },
        )

    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {
                    "error": str(e),
                    "suggestion": "Please try again. If the problem persists, contact support with the request ID"
                },
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
