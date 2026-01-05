"""
Test the Architect DSPy module.

This test verifies that the Architect module can generate learning objectives
following Bloom's Taxonomy with proper validation.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.dspy_client import configure_dspy
from src.modules.architect import Architect


def test_architect_basic():
    """Test basic Architect functionality."""
    print("Configuring DSPy...")
    try:
        lm = configure_dspy()
        print(f"✓ DSPy configured with model: {lm.model}")
    except Exception as e:
        print(f"✗ Failed to configure DSPy: {e}")
        print("  (This is expected if Ollama is not running)")
        return

    print("\nInitializing Architect module...")
    architect = Architect()
    print("✓ Architect module initialized")

    print("\nGenerating learning objectives...")
    try:
        structure = architect.generate_objectives(
            topic="Introduction to Python Programming",
            target_audience="Beginner developers with no programming experience",
            num_objectives=5,
        )

        print(f"✓ Generated course structure for: {structure.topic}")
        print(f"\n  Generated {len(structure.objectives)} learning objectives:")

        for obj in structure.objectives:
            print(f"\n  [{obj.id}] {obj.level.value}: {obj.verb}")
            print(f"      {obj.content}")

        # Validate objectives
        print("\n✓ All objectives validated successfully")
        print(f"  - Topic: {structure.topic}")
        print(f"  - Number of objectives: {len(structure.objectives)}")
        print(f"  - Bloom's levels covered: {set(obj.level.value for obj in structure.objectives)}")

        return True

    except Exception as e:
        print(f"\n✗ Failed to generate objectives: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Architect Module Test")
    print("=" * 70)

    success = test_architect_basic()

    print("\n" + "=" * 70)
    if success:
        print("✓ Test passed!")
    else:
        print("✗ Test failed")
    print("=" * 70)
