"""
Shared pytest fixtures and configuration for Open-Instruct tests.

This module provides common fixtures used across unit, mocked, and integration tests.
It includes fixtures for Pydantic models, mock DSPy clients, and test data.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, MagicMock, patch

import pytest
from pydantic import ValidationError

from src.core.models import (
    BloomLevel,
    BloomsTaxonomy,
    CourseStructure,
    LearningObjective,
    QuizQuestion,
)
from src.api.schemas import (
    DifficultyLevel,
    GenerateObjectivesRequest,
    GenerateQuizRequest,
)


# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def tests_dir(project_root: Path) -> Path:
    """Get the tests directory."""
    return project_root / "tests"


@pytest.fixture
def golden_set_path(tests_dir: Path) -> Path:
    """Get the golden set JSON file path."""
    return tests_dir / "golden_set.json"


# =============================================================================
# Bloom's Taxonomy Fixtures
# =============================================================================

@pytest.fixture
def valid_bloom_levels() -> List[str]:
    """Get all valid Bloom's cognitive levels."""
    return ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]


@pytest.fixture
def sample_verbs_by_level() -> Dict[str, List[str]]:
    """Sample approved verbs for each Bloom's level."""
    return {
        "Remember": ["define", "list", "name", "identify", "recall"],
        "Understand": ["explain", "describe", "summarize", "interpret", "paraphrase"],
        "Apply": ["apply", "use", "implement", "execute", "employ"],
        "Analyze": ["analyze", "differentiate", "distinguish", "examine", "investigate"],
        "Evaluate": ["evaluate", "assess", "judge", "appraise", "estimate"],
        "Create": ["create", "design", "construct", "build", "develop"],
    }


# =============================================================================
# Learning Objective Fixtures
# =============================================================================

@pytest.fixture
def valid_learning_objective_data() -> Dict:
    """Valid learning objective data for testing."""
    return {
        "id": "LO-001",
        "verb": "explain",
        "content": "the core concepts of machine learning",
        "level": BloomLevel.UNDERSTAND,
    }


@pytest.fixture
def valid_learning_objective(valid_learning_objective_data: Dict) -> LearningObjective:
    """A valid LearningObjective instance."""
    return LearningObjective(**valid_learning_objective_data)


@pytest.fixture
def sample_learning_objectives() -> List[LearningObjective]:
    """Sample learning objectives covering all Bloom's levels."""
    return [
        LearningObjective(
            id="LO-001",
            verb="define",
            content="machine learning and its core components",
            level=BloomLevel.REMEMBER,
        ),
        LearningObjective(
            id="LO-002",
            verb="explain",
            content="the differences between supervised and unsupervised learning",
            level=BloomLevel.UNDERSTAND,
        ),
        LearningObjective(
            id="LO-003",
            verb="apply",
            content="scikit-learn to train a basic classification model",
            level=BloomLevel.APPLY,
        ),
        LearningObjective(
            id="LO-004",
            verb="analyze",
            content="model performance using accuracy, precision, and recall metrics",
            level=BloomLevel.ANALYZE,
        ),
        LearningObjective(
            id="LO-005",
            verb="evaluate",
            content="the strengths and weaknesses of different ML algorithms",
            level=BloomLevel.EVALUATE,
        ),
        LearningObjective(
            id="LO-006",
            verb="design",
            content="a comprehensive machine learning pipeline for a given problem",
            level=BloomLevel.CREATE,
        ),
    ]


# =============================================================================
# Course Structure Fixtures
# =============================================================================

@pytest.fixture
def valid_course_structure_data(sample_learning_objectives: List[LearningObjective]) -> Dict:
    """Valid course structure data for testing."""
    return {
        "topic": "Introduction to Machine Learning",
        "objectives": [obj.model_dump() for obj in sample_learning_objectives[:3]],
    }


@pytest.fixture
def valid_course_structure(valid_course_structure_data: Dict) -> CourseStructure:
    """A valid CourseStructure instance."""
    return CourseStructure(**valid_course_structure_data)


# =============================================================================
# Quiz Question Fixtures
# =============================================================================

@pytest.fixture
def valid_quiz_question_data() -> Dict:
    """Valid quiz question data for testing."""
    return {
        "stem": "What is the primary purpose of machine learning?",
        "correct_answer": "To enable systems to learn and improve from experience without being explicitly programmed",
        "distractors": [
            "To store and retrieve large datasets",
            "To create user interfaces for data visualization",
            "To manage database connections and transactions",
        ],
        "explanation": "Machine learning focuses on building systems that can learn from data, rather than being explicitly programmed for every scenario.",
    }


@pytest.fixture
def valid_quiz_question(valid_quiz_question_data: Dict) -> QuizQuestion:
    """A valid QuizQuestion instance."""
    return QuizQuestion(**valid_quiz_question_data)


@pytest.fixture
def sample_quiz_questions() -> List[QuizQuestion]:
    """Sample quiz questions for testing."""
    return [
        QuizQuestion(
            stem="What is machine learning?",
            correct_answer="A subset of AI that enables systems to learn from data",
            distractors=[
                "A programming language for data analysis",
                "A database management system",
                "A hardware component",
            ],
            explanation="ML is a branch of AI focused on learning from data.",
        ),
        QuizQuestion(
            stem="Which type of learning uses labeled data?",
            correct_answer="Supervised learning",
            distractors=[
                "Unsupervised learning",
                "Reinforcement learning",
                "Deep learning",
            ],
            explanation="Supervised learning requires labeled input-output pairs.",
        ),
    ]


# =============================================================================
# API Request Schema Fixtures
# =============================================================================

@pytest.fixture
def valid_generate_objectives_request_data() -> Dict:
    """Valid data for GenerateObjectivesRequest."""
    return {
        "topic": "Introduction to Python Programming",
        "target_audience": "Beginner developers",
        "num_objectives": 6,
    }


@pytest.fixture
def valid_generate_objectives_request(valid_generate_objectives_request_data: Dict) -> GenerateObjectivesRequest:
    """A valid GenerateObjectivesRequest instance."""
    return GenerateObjectivesRequest(**valid_generate_objectives_request_data)


@pytest.fixture
def valid_generate_quiz_request_data() -> Dict:
    """Valid data for GenerateQuizRequest."""
    return {
        "objective_id": "LO-001",
        "difficulty": DifficultyLevel.MEDIUM,
        "num_options": 4,
    }


@pytest.fixture
def valid_generate_quiz_request(valid_generate_quiz_request_data: Dict) -> GenerateQuizRequest:
    """A valid GenerateQuizRequest instance."""
    return GenerateQuizRequest(**valid_generate_quiz_request_data)


# =============================================================================
# Mock DSPy Fixtures
# =============================================================================

@pytest.fixture
def mock_dspy_lm():
    """Mock DSPy LanguageModel for testing."""
    mock_lm = Mock()
    mock_lm.model_name = "mock-model"
    mock_lm.provider = "mock"
    return mock_lm


@pytest.fixture
def mock_dspy_prediction():
    """Mock DSPy Prediction with course_structure."""
    prediction = Mock()
    prediction.course_structure = {
        "topic": "Test Topic",
        "objectives": [
            {
                "id": "LO-001",
                "verb": "explain",
                "content": "test content",
                "level": "Understand",
            }
        ],
    }
    return prediction


@pytest.fixture
def mock_dspy_quiz_prediction():
    """Mock DSPy Prediction with quiz_question."""
    prediction = Mock()
    prediction.quiz_question = {
        "stem": "What is test?",
        "correct_answer": "Test answer",
        "distractors": ["Wrong 1", "Wrong 2", "Wrong 3"],
        "explanation": "Test explanation",
    }
    return prediction


# =============================================================================
# Mock Ollama Client Fixtures
# =============================================================================

@pytest.fixture
def mock_ollama_response():
    """Mock successful Ollama API response."""
    return {
        "model": "llama3.1",
        "response": json.dumps({
            "topic": "Test Topic",
            "objectives": [
                {
                    "id": "LO-001",
                    "verb": "explain",
                    "content": "test content",
                    "level": "Understand",
                }
            ],
        }),
        "done": True,
    }


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing."""
    client = Mock()
    client.generate.return_value = {
        "response": '{"test": "data"}',
        "done": True,
    }
    client.chat.return_value = {
        "message": {"content": '{"test": "data"}'},
        "done": True,
    }
    return client


# =============================================================================
# Golden Set Fixtures
# =============================================================================

@pytest.fixture
def golden_set_data() -> List[Dict]:
    """Golden dataset with 10 diverse topics for regression testing."""
    return [
        {
            "topic": "Introduction to Machine Learning",
            "target_audience": "Junior developers with basic Python knowledge",
            "num_objectives": 6,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
        },
        {
            "topic": "RESTful API Design with FastAPI",
            "target_audience": "Backend developers familiar with Python",
            "num_objectives": 5,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Create"],
        },
        {
            "topic": "Docker Containerization Fundamentals",
            "target_audience": "DevOps engineers and developers",
            "num_objectives": 6,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
        },
        {
            "topic": "React Hooks and State Management",
            "target_audience": "Frontend developers with React experience",
            "num_objectives": 5,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate"],
        },
        {
            "topic": "SQL Database Design and Optimization",
            "target_audience": "Backend developers and data analysts",
            "num_objectives": 6,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
        },
        {
            "topic": "Git Version Control Best Practices",
            "target_audience": "Software developers of all levels",
            "num_objectives": 5,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate"],
        },
        {
            "topic": "Cloud Computing with AWS",
            "target_audience": "Solutions architects and developers",
            "num_objectives": 6,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
        },
        {
            "topic": "Cybersecurity Fundamentals",
            "target_audience": "IT professionals and developers",
            "num_objectives": 5,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate"],
        },
        {
            "topic": "Data Structures and Algorithms",
            "target_audience": "Computer science students",
            "num_objectives": 6,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
        },
        {
            "topic": "Natural Language Processing with Transformers",
            "target_audience": "AI/ML engineers",
            "num_objectives": 6,
            "expected_levels": ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
        },
    ]


@pytest.fixture
def load_golden_set(golden_set_path: Path) -> List[Dict]:
    """Load golden set from JSON file."""
    if golden_set_path.exists():
        with open(golden_set_path, "r") as f:
            return json.load(f)
    return []


# =============================================================================
# Test Client Fixtures
# =============================================================================

@pytest.fixture
def mock_test_client():
    """Mock FastAPI test client fixture."""
    from fastapi.testclient import TestClient
    from src.api.main import app

    return TestClient(app)


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.1")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("CACHE_ENABLED", "false")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "mocked: marks tests as mocked tests (use mocked LLM responses)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (slower, requires services)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (skip with -m 'not slow')"
    )
    config.addinivalue_line(
        "markers", "golden: marks tests as golden set tests (regression testing)"
    )
