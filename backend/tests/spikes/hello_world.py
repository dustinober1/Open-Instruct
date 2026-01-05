#!/usr/bin/env python3
"""
Hello World Test for JSON Generation with DSPy and Ollama.

This script tests the ability to generate structured JSON output using DSPy with Ollama.
It generates 2 learning objectives about 'Python functions' and validates the output
against the CourseStructure schema.

Features:
- Uses DSPy with Ollama for LLM inference
- Generates 2 learning objectives about 'Python functions'
- Validates output is valid JSON matching CourseStructure schema
- Saves successful outputs to logs/spikes/
- Runs 5 iterations to measure JSON validity rate (target: 60%+)
- Detailed logging and results summary
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import dspy
from pydantic import ValidationError

from src.core.dspy_client import (
    configure_dspy,
    test_ollama_connection,
    OllamaConnectionError,
    OllamaConfigError,
)
from src.core.models import CourseStructure, LearningObjective, BloomLevel


# DSPy Signature for learning objective generation
class GenerateObjectives(dspy.Signature):
    """Generate learning objectives for a given topic following Bloom's Taxonomy.

    You must generate learning objectives and return ONLY valid JSON with this structure:
    {
        "topic": "...",
        "objectives": [
            {"id": "LO-001", "verb": "...", "content": "...", "level": "..."}
        ]
    }
    """

    topic = dspy.InputField(desc="The topic to generate learning objectives for")
    response = dspy.OutputField(desc="Complete JSON response with topic and objectives array")


# DSPy Module for generation
class ObjectiveGenerator(dspy.Module):
    """DSPy module for generating learning objectives."""

    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(GenerateObjectives)

    def forward(self, topic: str, num_objectives: int = 2):
        """Generate learning objectives for the given topic."""
        result = self.generate(topic=topic)
        return result


def validate_json_output(output: str) -> Dict:
    """
    Validate that output is valid JSON matching CourseStructure schema.

    Args:
        output: Raw string output from LLM

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "course_structure": Optional[CourseStructure],
            "error": Optional[str],
            "json_extracted": bool
        }
    """
    result = {
        "valid": False,
        "course_structure": None,
        "error": None,
        "json_extracted": False,
    }

    try:
        # Try to parse as JSON directly
        try:
            data = json.loads(output)
            result["json_extracted"] = True
        except json.JSONDecodeError:
            # Try to extract JSON from output
            output_stripped = output.strip()
            if "```json" in output_stripped:
                # Extract from markdown code block
                start = output_stripped.find("```json") + 7
                end = output_stripped.find("```", start)
                if end != -1:
                    json_str = output_stripped[start:end].strip()
                    data = json.loads(json_str)
                    result["json_extracted"] = True
                else:
                    result["error"] = "Could not find closing ``` in markdown block"
                    return result
            elif "```" in output_stripped:
                # Extract from code block without language tag
                start = output_stripped.find("```") + 3
                end = output_stripped.find("```", start)
                if end != -1:
                    json_str = output_stripped[start:end].strip()
                    data = json.loads(json_str)
                    result["json_extracted"] = True
                else:
                    result["error"] = "Could not find closing ``` in code block"
                    return result
            else:
                result["error"] = f"Invalid JSON: {output[:200]}..."
                return result

        # Validate against CourseStructure schema
        course = CourseStructure(**data)
        result["valid"] = True
        result["course_structure"] = course

    except ValidationError as e:
        result["error"] = f"Validation error: {str(e)}"
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"

    return result


def save_successful_output(iteration: int, output: str, course: CourseStructure):
    """Save successful output to logs/spikes/ directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hello_world_iter{iteration}_{timestamp}.json"

    log_dir = Path(__file__).parent.parent.parent / "logs" / "spikes"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / filename

    # Save the validated course structure
    with open(log_file, "w") as f:
        json.dump(
            {
                "iteration": iteration,
                "timestamp": timestamp,
                "raw_output": output,
                "course_structure": course.model_dump(),
            },
            f,
            indent=2,
        )

    return log_file


def run_single_iteration(iteration: int, topic: str = "Python functions") -> Dict:
    """
    Run a single iteration of the Hello World test.

    Args:
        iteration: Iteration number
        topic: Topic to generate objectives for

    Returns:
        Dictionary with iteration results
    """
    print(f"\n{'='*60}")
    print(f"Iteration {iteration}")
    print(f"{'='*60}")

    result = {
        "iteration": iteration,
        "topic": topic,
        "success": False,
        "valid_json": False,
        "output": None,
        "course_structure": None,
        "error": None,
        "duration_seconds": 0,
    }

    start_time = time.time()

    try:
        # Generate objectives using DSPy
        generator = ObjectiveGenerator()
        output = generator(topic=topic, num_objectives=2)

        # Get the actual output text
        if hasattr(output, 'response'):
            output_text = output.response
        elif isinstance(output, dict):
            output_text = output.get('response', str(output))
        else:
            output_text = str(output)

        print(f"\n📤 Raw Output (first 500 chars):")
        print(output_text[:500] + ("..." if len(output_text) > 500 else ""))

        # Validate JSON output
        validation = validate_json_output(output_text)

        result["duration_seconds"] = time.time() - start_time

        if validation["valid"]:
            print(f"\n✅ Valid JSON!")
            print(f"   Topic: {validation['course_structure'].topic}")
            print(f"   Objectives: {len(validation['course_structure'].objectives)}")

            for idx, obj in enumerate(validation['course_structure'].objectives, 1):
                print(f"   {idx}. [{obj.level}] {obj.verb}: {obj.content}")

            # Save successful output
            log_file = save_successful_output(
                iteration, output_text, validation["course_structure"]
            )
            print(f"\n💾 Saved to: {log_file}")

            result["success"] = True
            result["valid_json"] = True
            result["output"] = output_text
            result["course_structure"] = validation["course_structure"].model_dump()

        else:
            print(f"\n❌ Invalid JSON")
            print(f"   Error: {validation['error']}")

            result["valid_json"] = False
            result["error"] = validation["error"]
            result["output"] = output_text

    except Exception as e:
        result["duration_seconds"] = time.time() - start_time
        result["error"] = f"Exception during generation: {str(e)}"
        print(f"\n❌ Exception: {result['error']}")

    return result


def print_summary(results: List[Dict]):
    """Print summary statistics for all iterations."""
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    valid_json = sum(1 for r in results if r["valid_json"])
    success_rate = (successful / total * 100) if total > 0 else 0
    json_validity_rate = (valid_json / total * 100) if total > 0 else 0

    avg_duration = sum(r["duration_seconds"] for r in results) / total if total > 0 else 0

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total iterations: {total}")
    print(f"Successful generations: {successful}/{total} ({success_rate:.1f}%)")
    print(f"Valid JSON outputs: {valid_json}/{total} ({json_validity_rate:.1f}%)")
    print(f"Target validity rate: 60%+")
    print(f"Target achieved: {'✅ YES' if json_validity_rate >= 60 else '❌ NO'}")
    print(f"Average duration: {avg_duration:.2f}s")

    if successful > 0:
        print(f"\n📁 Successful outputs saved to: logs/spikes/")


def main():
    """Main function to run the Hello World test."""
    print("=" * 60)
    print("Hello World Test: JSON Generation with DSPy + Ollama")
    print("=" * 60)
    print(f"Topic: Python functions")
    print(f"Objectives to generate: 2")
    print(f"Iterations: 5")
    print(f"Target JSON validity rate: 60%+")
    print("=" * 60)

    # Test Ollama connection
    print("\n🔍 Testing Ollama connection...")
    connection_result = test_ollama_connection()

    if connection_result["status"] != "ok":
        print(f"❌ Ollama connection failed: {connection_result['error']}")
        print("\nPlease ensure Ollama is running:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Verify model is installed: ollama list")
        print("  3. Install model if needed: ollama pull deepseek-r1:1.5b")
        sys.exit(1)

    print(f"✅ Ollama connection OK: {connection_result['base_url']}")

    # Configure DSPy
    print("\n⚙️  Configuring DSPy with Ollama...")
    try:
        lm = configure_dspy()
        model_info = lm.model if hasattr(lm, 'model') else "unknown"
        print(f"✅ DSPy configured with model: {model_info}")
    except (OllamaConnectionError, OllamaConfigError) as e:
        print(f"❌ Failed to configure DSPy: {e}")
        sys.exit(1)

    # Run iterations
    results = []
    num_iterations = 5

    for i in range(1, num_iterations + 1):
        result = run_single_iteration(i, topic="Python functions")
        results.append(result)

        # Small delay between iterations
        if i < num_iterations:
            time.sleep(1)

    # Print summary
    print_summary(results)

    # Exit with appropriate code
    validity_rate = sum(1 for r in results if r["valid_json"]) / len(results) * 100
    sys.exit(0 if validity_rate >= 60 else 1)


if __name__ == "__main__":
    main()
