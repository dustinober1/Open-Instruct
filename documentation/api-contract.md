# API Contract: Open-Instruct Backend

**Audience**: Junior Developers, Frontend Developers
**Purpose**: Complete API specification with request/response schemas
**Version**: 1.0.0
**Base URL**: `http://localhost:8000`

---

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Response Formats](#common-response-formats)
4. [Endpoints](#endpoints)
5. [Request/Response Schemas](#requestresponse-schemas)
6. [Error Codes](#error-codes)
7. [Rate Limiting](#rate-limiting)
8. [WebSocket Events (Optional)](#websocket-events-optional)

---

## Overview

### API Architecture

```
┌─────────────────────────────────────────────┐
│ FastAPI Backend                             │
│                                             │
│ ┌──────────┐      ┌──────────┐            │
│ │   Ollama  │─────▶│   DSPy   │            │
│ │  (LLM)    │      │ Modules  │            │
│ └──────────┘      └──────────┘            │
│                                             │
│ ┌──────────────────────────────────────┐   │
│ │           REST API Endpoints         │   │
│ └──────────────────────────────────────┘   │
│                                             │
│ ┌──────────┐      ┌──────────┐            │
│ │  SQLite  │◀─────│   Cache  │            │
│ │ (DB)      │      │ Layer    │            │
│ └──────────┘      └──────────┘            │
└─────────────────────────────────────────────┘
```

### Design Principles

1. **RESTful**: Standard HTTP methods (GET, POST, PUT, DELETE)
2. **JSON First**: All requests/responses use JSON
3. **Versioned**: `/api/v1/` prefix for all endpoints
4. **Idempotent**: Safe operations can be retried
5. **HATEOAS**: Responses include links to related resources

---

## Authentication

### Current Status: No Authentication (MVP)

**For MVP**: API is open, no authentication required

**Future (Post-MVP)**:
```http
POST /api/v1/generate/objectives
Authorization: Bearer <token>
```

---

## Common Response Formats

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-05T10:30:00Z",
    "processing_time_ms": 1523
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "INVALID_JSON",
    "message": "Failed to parse LLM output as JSON after 3 attempts",
    "details": {
      "raw_output": "This is not valid JSON...",
      "attempts": 3
    }
  },
  "meta": {
    "request_id": "req_def456",
    "timestamp": "2025-01-05T10:31:00Z"
  }
}
```

---

## Endpoints

### 1. Health Check

Check if API and Ollama are running.

```http
GET /health
```

**Response 200**:
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "model_version": "deepseek-r1:1.5b",
  "version": "1.0.0",
  "uptime_seconds": 1234
}
```

**Response 503** (Ollama down):
```json
{
  "status": "degraded",
  "ollama_connected": false,
  "error": "Ollama service not running",
  "model_version": "deepseek-r1:1.5b",
  "version": "1.0.0"
}
```

---

### 2. Generate Learning Objectives

Generate learning objectives for a topic using Bloom's Taxonomy.

```http
POST /api/v1/generate/objectives
```

**Request Body**:
```json
{
  "topic": "Python functions and decorators",
  "target_audience": "Intermediate Python developers",
  "num_objectives": 6,
  "options": {
    "force_cache_bypass": false,
    "include_explanations": true
  }
}
```

**Request Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | ✅ Yes | Course topic (1-200 chars) |
| `target_audience` | string | ✅ Yes | Who is learning (1-200 chars) |
| `num_objectives` | integer | ❌ No | Number of objectives (5-10, default: 6) |
| `options.force_cache_bypass` | boolean | ❌ No | Skip cache and regenerate (default: false) |
| `options.include_explanations` | boolean | ❌ No | Add verb explanations (default: false) |

**Response 200**:
```json
{
  "success": true,
  "data": {
    "topic": "Python functions and decorators",
    "objectives": [
      {
        "id": "LO-001",
        "verb": "define",
        "content": "what a function is and why we use them",
        "level": "Remember",
        "explanation": "Functions are reusable blocks of code..."
      },
      {
        "id": "LO-002",
        "verb": "explain",
        "content": "the difference between parameters and arguments",
        "level": "Understand",
        "explanation": "Parameters are defined in function..."
      },
      {
        "id": "LO-003",
        "verb": "apply",
        "content": "decorators to add functionality to functions",
        "level": "Apply",
        "explanation": "Decorators modify function behavior..."
      }
    ],
    "generated_at": "2025-01-05T10:30:00Z",
    "model_version": "deepseek-r1:1.5b",
    "cache_status": "miss"
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-05T10:30:00Z",
    "processing_time_ms": 15234
  }
}
```

**Response 400** (Invalid input):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "errors": [
        {
          "field": "topic",
          "message": "Topic must be between 1 and 200 characters"
        }
      ]
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-05T10:30:00Z"
  }
}
```

**Response 503** (Ollama unavailable):
```json
{
  "success": false,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Ollama service not responding",
    "details": {
      "retry_after_seconds": 30,
      "cached_courses_available": true
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-05T10:30:00Z"
  }
}
```

---

### 3. Generate Quiz Question

Generate a multiple-choice quiz question for a learning objective.

```http
POST /api/v1/generate/quiz
```

**Request Body**:
```json
{
  "objective_id": "LO-003",
  "difficulty": "medium",
  "num_options": 4
}
```

**Request Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `objective_id` | string | ✅ Yes | ID of learning objective |
| `difficulty` | string | ❌ No | `easy`, `medium`, or `hard` (default: "medium") |
| `num_options` | integer | ❌ No | Total options (4 only supported for MVP) |

**Response 200**:
```json
{
  "success": true,
  "data": {
    "quiz_id": "quiz_abc123",
    "objective_id": "LO-003",
    "stem": "What is the primary purpose of a decorator in Python?",
    "correct_answer": "To modify the behavior of a function or class",
    "distractors": [
      "To improve code readability",
      "To increase execution speed",
      "To prevent memory leaks"
    ],
    "explanation": "Decorators wrap functions to add functionality before/after execution.",
    "difficulty": "medium",
    "generated_at": "2025-01-05T10:31:00Z"
  },
  "meta": {
    "request_id": "req_def456",
    "timestamp": "2025-01-05T10:31:00Z",
    "processing_time_ms": 8432
  }
}
```

**Response 404** (Objective not found):
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Learning objective LO-999 not found",
    "details": {
      "available_objectives": ["LO-001", "LO-002", "LO-003"]
    }
  },
  "meta": {
    "request_id": "req_def456",
    "timestamp": "2025-01-05T10:31:00Z"
  }
}
```

---

### 4. Get Course by ID

Retrieve a previously generated course from cache.

```http
GET /api/v1/courses/{course_id}
```

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `course_id` | string | Unique course identifier |

**Response 200**:
```json
{
  "success": true,
  "data": {
    "course_id": "course_xyz789",
    "topic": "Python functions and decorators",
    "objectives": [...],
    "created_at": "2025-01-05T10:30:00Z",
    "last_accessed": "2025-01-05T11:00:00Z"
  },
  "meta": {
    "request_id": "req_ghi789",
    "timestamp": "2025-01-05T11:00:00Z",
    "processing_time_ms": 45
  }
}
```

---

### 5. List All Courses

List all generated courses in the database.

```http
GET /api/v1/courses
```

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 20 | Max courses to return |
| `offset` | integer | No | 0 | Pagination offset |
| `search` | string | No | - | Filter by topic (partial match) |
| `sort_by` | string | No | `created_at` | Sort field: `created_at`, `topic` |
| `order` | string | No | `desc` | Sort order: `asc`, `desc` |

**Request Example**:
```http
GET /api/v1/courses?limit=10&search=python&sort_by=created_at&order=desc
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "course_id": "course_xyz789",
        "topic": "Python functions and decorators",
        "num_objectives": 6,
        "created_at": "2025-01-05T10:30:00Z"
      },
      {
        "course_id": "course_abc123",
        "topic": "Python lists and tuples",
        "num_objectives": 5,
        "created_at": "2025-01-04T15:20:00Z"
      }
    ],
    "pagination": {
      "total": 15,
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
  },
  "meta": {
    "request_id": "req_jkl012",
    "timestamp": "2025-01-05T11:00:00Z",
    "processing_time_ms": 67
  }
}
```

---

### 6. Delete Course

Delete a course from the database.

```http
DELETE /api/v1/courses/{course_id}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "message": "Course course_xyz789 deleted successfully",
    "deleted_at": "2025-01-05T11:05:00Z"
  },
  "meta": {
    "request_id": "req_mno345",
    "timestamp": "2025-01-05T11:05:00Z",
    "processing_time_ms": 123
  }
}
```

**Response 404**:
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Course course_xyz789 not found"
  },
  "meta": {
    "request_id": "req_mno345",
    "timestamp": "2025-01-05T11:05:00Z"
  }
}
```

---

### 7. Export Course

Export a course as JSON file.

```http
GET /api/v1/courses/{course_id}/export
```

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `format` | string | No | `json` | Export format: `json`, `csv` |
| `include_quizzes` | boolean | No | `true` | Include quiz questions |

**Response 200** (with `Content-Type: application/json`):
```json
{
  "course_id": "course_xyz789",
  "topic": "Python functions and decorators",
  "target_audience": "Intermediate Python developers",
  "objectives": [...],
  "quizzes": [...],
  "exported_at": "2025-01-05T11:10:00Z",
  "version": "1.0.0"
}
```

---

### 8. Import Course

Import a previously exported course.

```http
POST /api/v1/courses/import
```

**Request Body**:
```json
{
  "course_data": { ... },
  "options": {
    "overwrite": false,
    "validate_only": false
  }
}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "course_id": "course_import_abc123",
    "message": "Course imported successfully",
    "objectives_imported": 6,
    "quizzes_imported": 6,
    "warnings": []
  },
  "meta": {
    "request_id": "req_pqr678",
    "timestamp": "2025-01-05T11:15:00Z",
    "processing_time_ms": 234
  }
}
```

**Response 400** (Validation failed):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Import data contains invalid verbs",
    "details": {
      "invalid_objectives": [
        {
          "id": "LO-001",
          "verb": "create",
          "level": "Remember"
        }
      ]
    }
  },
  "meta": {
    "request_id": "req_pqr678",
    "timestamp": "2025-01-05T11:15:00Z"
  }
}
```

---

## Request/Response Schemas

### Pydantic Schemas

```python
# src/api/schemas.py

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# Request Schemas
class GenerateObjectivesRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    target_audience: str = Field(..., min_length=1, max_length=200)
    num_objectives: int = Field(default=6, ge=5, le=10)

    class Options(BaseModel):
        force_cache_bypass: bool = False
        include_explanations: bool = False

    options: Options = Field(default_factory=Options)

class GenerateQuizRequest(BaseModel):
    objective_id: str = Field(..., pattern=r"^LO-\d+$")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    num_options: int = Field(default=4, ge=4, le=4)

class ImportCourseRequest(BaseModel):
    course_data: Dict
    options: Dict = Field(default_factory=lambda: {
        "overwrite": False,
        "validate_only": False
    })

# Response Schemas
class LearningObjectiveResponse(BaseModel):
    id: str
    verb: str
    content: str
    level: str
    explanation: Optional[str] = None

class CourseStructureResponse(BaseModel):
    topic: str
    objectives: List[LearningObjectiveResponse]
    generated_at: datetime
    model_version: str
    cache_status: str

class QuizQuestionResponse(BaseModel):
    quiz_id: str
    objective_id: str
    stem: str
    correct_answer: str
    distractors: List[str]
    explanation: str
    difficulty: str
    generated_at: datetime

class MetaResponse(BaseModel):
    request_id: str
    timestamp: datetime
    processing_time_ms: int

class SuccessResponse(BaseModel):
    success: bool = True
    data: Dict
    meta: MetaResponse

class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict
    meta: MetaResponse
```

---

## Error Codes

### HTTP Status Codes

| Code | Name | Usage |
|------|------|-------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Ollama not running |
| 504 | Gateway Timeout | LLM generation timeout |

### Application Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `INVALID_JSON` | 422 | LLM output not valid JSON |
| `INVALID_VERB` | 422 | Verb not in approved Bloom's list |
| `SERVICE_UNAVAILABLE` | 503 | Ollama not responding |
| `GENERATION_TIMEOUT` | 504 | LLM generation took too long |
| `CACHE_MISS` | 404 | Course not in cache |
| `DUPLICATE_ID` | 409 | Course ID already exists |
| `RATE_LIMITED` | 429 | Too many requests |

### Error Response Examples

```json
{
  "success": false,
  "error": {
    "code": "INVALID_VERB",
    "message": "Verb 'create' is not valid for Remember level",
    "details": {
      "invalid_verb": "create",
      "level": "Remember",
      "approved_verbs": ["define", "list", "name", "identify"]
    }
  },
  "meta": {
    "request_id": "req_xyz789",
    "timestamp": "2025-01-05T10:30:00Z"
  }
}
```

---

## Rate Limiting

### Current Limits (MVP)

**No rate limiting** for MVP (local-first app)

### Future Implementation

```http
POST /api/v1/generate/objectives
```

**Response 429** (Rate limited):
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests",
    "details": {
      "retry_after_seconds": 60,
      "limit": 10,
      "window": "1 hour"
    }
  },
  "meta": {
    "request_id": "req_rate_limit_123",
    "timestamp": "2025-01-05T11:30:00Z"
  }
}
```

**Rate Limit Headers**:
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1704460800
```

---

## WebSocket Events (Optional)

### Purpose

Real-time updates for long-running LLM generations

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/generate/objectives');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.payload);
};
```

### Event Types

#### 1. Generation Started

```json
{
  "type": "generation.started",
  "request_id": "req_abc123",
  "payload": {
    "topic": "Python functions",
    "estimated_time_seconds": 15
  }
}
```

#### 2. Objective Generated

```json
{
  "type": "objective.generated",
  "request_id": "req_abc123",
  "payload": {
    "objective_number": 1,
    "total": 6,
    "objective": {
      "id": "LO-001",
      "verb": "define",
      "content": "what a function is",
      "level": "Remember"
    }
  }
}
```

#### 3. Generation Complete

```json
{
  "type": "generation.complete",
  "request_id": "req_abc123",
  "payload": {
    "course_id": "course_xyz789",
    "total_objectives": 6,
    "generation_time_ms": 15234
  }
}
```

#### 4. Generation Failed

```json
{
  "type": "generation.failed",
  "request_id": "req_abc123",
  "payload": {
    "error": "Invalid JSON after 3 attempts",
    "attempts": 3
  }
}
```

---

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Generate objectives
curl -X POST http://localhost:8000/api/v1/generate/objectives \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python functions",
    "target_audience": "Beginner developers",
    "num_objectives": 6
  }'

# Generate quiz
curl -X POST http://localhost:8000/api/v1/generate/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "objective_id": "LO-001",
    "difficulty": "medium"
  }'

# List courses
curl http://localhost:8000/api/v1/courses?limit=10

# Export course
curl http://localhost:8000/api/v1/courses/course_xyz789/export \
  -o course_export.json
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Generate objectives
response = requests.post(
    f"{BASE_URL}/api/v1/generate/objectives",
    json={
        "topic": "Python functions",
        "target_audience": "Beginner developers",
        "num_objectives": 6
    }
)

data = response.json()
if data["success"]:
    print(f"Generated {len(data['data']['objectives'])} objectives")
else:
    print(f"Error: {data['error']['message']}")
```

---

## API Documentation

### Interactive Documentation (Swagger UI)

Once FastAPI is running, access interactive docs at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Try-it-out functionality
- Request/response schemas
- Model validation
- Example requests

---

## Next Steps

1. **Implement FastAPI app** with these endpoints
2. **Add request validation** using Pydantic schemas
3. **Implement caching layer** for repeated requests
4. **Add error handlers** for all error codes
5. **Set up CORS** for frontend communication

Remember: **API contracts are commitments**. Once published, changes must be backward compatible or require a version bump.
