# 🎯 API Endpoints: Usage Examples

**Version**: 1.0.0
**Last Updated**: 2025-01-05

---

## 🚀 Introduction

This document provides practical examples for using the Open-Instruct API endpoints. These examples will help you understand how to interact with the system once it's built.

---

## 📋 Available Endpoints

### 1. Generate Learning Objectives
- **Endpoint**: `POST /api/v1/objectives`
- **Purpose**: Generate Bloom's Taxonomy-aligned learning objectives
- **Authentication**: Not required for MVP

### 2. Generate Quiz Questions
- **Endpoint**: `POST /api/v1/quiz`
- **Purpose**: Create assessment questions for objectives
- **Authentication**: Not required for MVP

### 3. List Courses
- **Endpoint**: `GET /api/v1/courses`
- **Purpose**: Retrieve saved courses
- **Authentication**: Not required for MVP

### 4. Get Course Details
- **Endpoint**: `GET /api/v1/courses/{course_id}`
- **Purpose**: Retrieve specific course details
- **Authentication**: Not required for MVP

---

## 🛠️ Usage Examples

### Example 1: Generate Learning Objectives

```bash
# Generate objectives for "Introduction to Python"
curl -X POST "http://localhost:8000/api/v1/objectives" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Python",
    "level": "beginner",
    "subject": "Programming",
    "count": 5
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "topic": "Introduction to Python",
    "objectives": [
      {
        "id": 1,
        "verb": "identify",
        "level": "remember",
        "objective": "Identify the basic syntax and structure of Python programs",
        "keywords": ["syntax", "structure", "basic"]
      },
      {
        "id": 2,
        "verb": "explain",
        "level": "understand",
        "objective": "Explain the difference between variables, data types, and operators in Python",
        "keywords": ["variables", "data types", "operators"]
      }
    ],
    "generated_at": "2025-01-05T10:30:00Z"
  },
  "meta": {
    "request_id": "req_123456",
    "timing_ms": 1542,
    "model_used": "deepseek-r1:1.5b"
  }
}
```

### Example 2: Generate Quiz Questions

```bash
# Generate quiz questions for existing objectives
curl -X POST "http://localhost:8000/api/v1/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "objectives": [
      "Identify the basic syntax and structure of Python programs",
      "Explain the difference between variables, data types, and operators in Python"
    ],
    "question_types": ["multiple_choice", "short_answer"],
    "difficulty": "beginner"
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": 1,
        "type": "multiple_choice",
        "objective_id": 1,
        "question": "Which of the following is a valid Python variable name?",
        "options": ["2variable", "variable_name", "variable-name", "class"],
        "correct_answer": "variable_name",
        "explanation": "Python variable names must start with a letter or underscore and cannot contain special characters except underscore."
      },
      {
        "id": 2,
        "type": "short_answer",
        "objective_id": 2,
        "question": "Explain the difference between a list and a tuple in Python.",
        "correct_answer": "Lists are mutable (can be changed), tuples are immutable (cannot be changed). Lists use square brackets, tuples use parentheses.",
        "points": 5
      }
    ],
    "generated_at": "2025-01-05T10:32:00Z"
  },
  "meta": {
    "request_id": "req_123457",
    "timing_ms": 2156,
    "model_used": "deepseek-r1:1.5b"
  }
}
```

### Example 3: List Courses

```bash
# List all saved courses
curl -X GET "http://localhost:8000/api/v1/courses"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": 1,
        "title": "Introduction to Python",
        "description": "Learn Python programming basics",
        "objectives_count": 5,
        "questions_count": 10,
        "created_at": "2025-01-05T10:30:00Z",
        "updated_at": "2025-01-05T10:35:00Z"
      }
    ],
    "total": 1
  },
  "meta": {
    "request_id": "req_123458",
    "timing_ms": 45
  }
}
```

### Example 4: Get Course Details

```bash
# Get details for a specific course
curl -X GET "http://localhost:8000/api/v1/courses/1"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "course": {
      "id": 1,
      "title": "Introduction to Python",
      "description": "Learn Python programming basics",
      "objectives": [
        {
          "id": 1,
          "verb": "identify",
          "level": "remember",
          "objective": "Identify the basic syntax and structure of Python programs",
          "questions": [
            {
              "id": 1,
              "type": "multiple_choice",
              "question": "Which of the following is a valid Python variable name?",
              "options": ["variable_name", "2variable", "variable-name", "class"],
              "correct_answer": "variable_name"
            }
          ]
        }
      ],
      "created_at": "2025-01-05T10:30:00Z",
      "updated_at": "2025-01-05T10:35:00Z"
    }
  },
  "meta": {
    "request_id": "req_123459",
    "timing_ms": 120
  }
}
```

---

## 💡 Advanced Usage

### Batch Generation

```bash
# Generate multiple courses in one request
curl -X POST "http://localhost:8000/api/v1/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topics": [
      {"topic": "Introduction to Python", "level": "beginner"},
      {"topic": "Data Structures in Python", "level": "intermediate"},
      {"topic": "Web Development with Flask", "level": "advanced"}
    ],
    "count_per_topic": 5
  }'
```

### Export Options

```bash
# Export course as JSON
curl -X GET "http://localhost:8000/api/v1/courses/1/export?format=json" \
  -H "Accept: application/json"

# Export course as CSV
curl -X GET "http://localhost:8000/api/v1/courses/1/export?format=csv" \
  -H "Accept: text/csv"

# Export course as PDF (future feature)
curl -X GET "http://localhost:8000/api/v1/courses/1/export?format=pdf" \
  -H "Accept: application/pdf"
```

---

## 🧪 Testing with Postman

### Postman Collection Setup

1. **Create New Collection**: "Open-Instruct API"
2. **Add Request**: "Generate Objectives"
   - Method: POST
   - URL: `http://localhost:8000/api/v1/objectives`
   - Headers:
     - Key: `Content-Type`
     - Value: `application/json`
   - Body (raw JSON):
     ```json
     {
       "topic": "Introduction to Python",
       "level": "beginner",
       "subject": "Programming",
       "count": 5
     }
     ```

3. **Test Script** (Response Validation):
   ```javascript
   // Test response structure
   pm.test("Status code is 200", function () {
       pm.response.to.have.status(200);
   });

   pm.test("Response has success property", function () {
       const jsonData = pm.response.json();
       pm.expect(jsonData).to.have.property('success');
       pm.expect(jsonData.success).to.be.true;
   });

   pm.test("Response has data object", function () {
       const jsonData = pm.response.json();
       pm.expect(jsonData).to.have.property('data');
       pm.expect(jsonData.data).to.have.property('objectives');
   });

   // Extract request_id for debugging
   const requestId = pm.response.json().meta.request_id;
   pm.environment.set("last_request_id", requestId);
   ```

---

## 🔧 Troubleshooting API Issues

### Common Issues and Solutions

#### Issue 1: 422 Validation Error
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "topic": ["This field is required"]
    }
  }
}
```

**Solution**: Check that all required parameters are provided in the correct format.

#### Issue 2: 503 Service Unavailable
```json
{
  "success": false,
  "error": {
    "code": "OLLAMA_UNAVAILABLE",
    "message": "LLM service is currently unavailable",
    "details": {
      "suggestion": "Check Ollama service status"
    }
  }
}
```

**Solution**: Ensure Ollama is running with `ollama serve`.

#### Issue 3: 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "request_id": "req_123456",
      "log_id": "log_789012"
    }
  }
}
```

**Solution**: Check the server logs for detailed error information.

---

## 📝 API Best Practices

### 1. Use Request IDs
Always include the `request_id` from the response when reporting issues:
```bash
# Log request_id for debugging
echo "Request ID: $(curl -s ... | jq -r '.meta.request_id')"
```

### 2. Handle Timeouts
```bash
# Use timeout flag for long-running requests
curl -X POST "... \
  --max-time 30 \
  --connect-timeout 10
```

### 3. Retry Failed Requests
```bash
# Implement exponential backoff for retries
for i in {1..3}; do
    if curl -X POST "..."; then
        break
    else
        sleep $((i * 2))
    fi
done
```

### 4. Cache Responses
```bash
# Cache API responses for repeated requests
cache_file=$(echo "topic_beginner" | md5sum | cut -d' ' -f1)
if [ -f "cache/$cache_file" ]; then
    cat "cache/$cache_file"
else
    curl -X POST "..." | tee "cache/$cache_file"
fi
```

---

## 🎯 Future Enhancements

### Planned API Features

1. **Authentication**
   - API key authentication
   - User management

2. **Enhanced Export**
   - PDF export with formatting
   - PowerPoint presentations
   - Interactive HTML

3. **Real-time Features**
   - WebSocket for live updates
   - Progress tracking

4. **Collaboration**
   - Multi-user support
   - Course sharing
   - Version control

### Example: Authenticated Request
```bash
# Future authenticated request
curl -X POST "http://localhost:8000/api/v1/objectives" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Advanced Machine Learning",
    "level": "expert"
  }'
```

---

## 📞 API Support

### Getting Help
- **Documentation**: Always check the API documentation first
- **Issues**: Report issues with request_id and complete request details
- **Testing**: Use the provided Postman collection for testing

### Contributing to API
When adding new endpoints:
1. Update this documentation
2. Add examples
3. Include in Postman collection
4. Add tests

---

**Happy API integration! 🚀**