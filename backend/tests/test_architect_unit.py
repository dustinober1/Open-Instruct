"""
Unit tests for the Architect DSPy module structure.

These tests validate the module structure without requiring Ollama to be running.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.models import BloomsTaxonomy, CourseStructure, LearningObjective


def test_blooms_verb_validation():
    """Test that Bloom's verb validation works correctly."""
    print("\n" + "=" * 70)
    print("Test: Bloom's Verb Validation")
    print("=" * 70)

    # Test valid verbs
    assert BloomsTaxonomy.validate_verb("define", "Remember"), "define should be valid for Remember"
    assert BloomsTaxonomy.validate_verb("explain", "Understand"), "explain should be valid for Understand"
    assert BloomsTaxonomy.validate_verb("apply", "Apply"), "apply should be valid for Apply"
    assert BloomsTaxonomy.validate_verb("analyze", "Analyze"), "analyze should be valid for Analyze"
    assert BloomsTaxonomy.validate_verb("evaluate", "Evaluate"), "evaluate should be valid for Evaluate"
    assert BloomsTaxonomy.validate_verb("create", "Create"), "create should be valid for Create"

    print("✓ Valid verbs accepted")

    # Test invalid verbs
    assert not BloomsTaxonomy.validate_verb("create", "Remember"), "create should NOT be valid for Remember"
    assert not BloomsTaxonomy.validate_verb("define", "Create"), "define should NOT be valid for Create"

    print("✓ Invalid verbs rejected")


def test_learning_objective_model():
    """Test LearningObjective Pydantic model."""
    print("\n" + "=" * 70)
    print("Test: LearningObjective Model")
    print("=" * 70)

    obj = LearningObjective(
        id="LO-001",
        verb="define",
        content="machine learning concepts",
        level="Remember"
    )

    assert obj.id == "LO-001"
    assert obj.verb == "define"
    assert obj.content == "machine learning concepts"
    assert obj.level.value == "Remember"

    print("✓ LearningObjective model validates correctly")


def test_course_structure_model():
    """Test CourseStructure Pydantic model."""
    print("\n" + "=" * 70)
    print("Test: CourseStructure Model")
    print("=" * 70)

    structure = CourseStructure(
        topic="Introduction to Python",
        objectives=[
            LearningObjective(
                id="LO-001",
                verb="define",
                content="Python variables and data types",
                level="Remember"
            ),
            LearningObjective(
                id="LO-002",
                verb="apply",
                content="control flow statements in Python programs",
                level="Apply"
            ),
        ]
    )

    assert structure.topic == "Introduction to Python"
    assert len(structure.objectives) == 2
    assert structure.objectives[0].verb == "define"

    print("✓ CourseStructure model validates correctly")


def test_architect_module_imports():
    """Test that Architect module can be imported."""
    print("\n" + "=" * 70)
    print("Test: Architect Module Imports")
    print("=" * 70)

    try:
        from src.modules.architect import Architect, GenerateObjectives, ARCHITECT_EXAMPLES
        print("✓ Architect module imports successfully")
        print("✓ GenerateObjectives signature available")
        print("✓ Few-shot examples defined")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_architect_signature():
    """Test GenerateObjectives signature structure."""
    print("\n" + "=" * 70)
    print("Test: GenerateObjectives Signature")
    print("=" * 70)

    from src.modules.architect import GenerateObjectives
    import dspy

    # Verify it's a DSPy Signature
    assert issubclass(GenerateObjectives, dspy.Signature), "GenerateObjectives must be a DSPy Signature"

    print("✓ GenerateObjectives is a valid DSPy Signature")


def test_few_shot_examples():
    """Test that few-shot examples are properly structured."""
    print("\n" + "=" * 70)
    print("Test: Few-Shot Examples")
    print("=" * 70)

    from src.modules.architect import ARCHITECT_EXAMPLES

    assert len(ARCHITECT_EXAMPLES) > 0, "Should have at least one example"

    for example in ARCHITECT_EXAMPLES:
        assert "topic" in example
        assert "target_audience" in example
        assert "num_objectives" in example
        assert "expected_output" in example
        assert "objectives" in example["expected_output"]

        # Validate objectives structure
        for obj in example["expected_output"]["objectives"]:
            assert "id" in obj
            assert "verb" in obj
            assert "content" in obj
            assert "level" in obj

    print(f"✓ All {len(ARCHITECT_EXAMPLES)} few-shot examples properly structured")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Architect Module Unit Tests")
    print("=" * 70)

    tests = [
        test_blooms_verb_validation,
        test_learning_objective_model,
        test_course_structure_model,
        test_architect_module_imports,
        test_architect_signature,
        test_few_shot_examples,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)

    if failed == 0:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {failed} test(s) failed")
        sys.exit(1)
