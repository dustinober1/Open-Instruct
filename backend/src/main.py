#!/usr/bin/env python3
"""
Open-Instruct CLI - AI-powered educational content generation engine.

This CLI provides commands to generate learning objectives and quiz questions
based on Bloom's Taxonomy using DSPy and multiple LLM providers.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.dspy_client import (
    OllamaConnectionError,
    setup_dspy_with_ollama,
    test_ollama_connection,
)
from src.core.models import BloomLevel, CourseStructure, LearningObjective, QuizQuestion
from src.modules.architect import Architect
from src.modules.assessor import Assessor

# Initialize Typer app
app = typer.Typer(
    name="open-instruct",
    help="Open-Instruct: AI-powered educational content generation",
    add_completion=False,
)

# Rich console for formatted output
console = Console()

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / f"openinstruct_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        RichHandler(rich_tracebacks=True, console=console)
    ]
)

logger = logging.getLogger(__name__)


def handle_keyboard_interrupt(func):
    """Decorator to handle keyboard interrupts gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user.[/yellow]")
            logger.info("Operation cancelled by user")
            sys.exit(130)
    return wrapper


def print_success(message: str):
    """Print a success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print an error message in red."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str):
    """Print a warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def display_course_structure(structure: CourseStructure):
    """Display course structure in a formatted table."""
    console.print()
    console.print(Panel.fit(f"[bold blue]{structure.topic}[/bold blue]", padding=(0, 1)))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Level", width=12)
    table.add_column("Verb", width=15)
    table.add_column("Learning Objective")

    for obj in structure.objectives:
        level_color = {
            "Remember": "green",
            "Understand": "blue",
            "Apply": "yellow",
            "Analyze": "orange",
            "Evaluate": "red",
            "Create": "purple",
        }.get(obj.level.value, "white")

        table.add_row(
            obj.id,
            f"[{level_color}]{obj.level.value}[/{level_color}]",
            obj.verb,
            obj.content
        )

    console.print(table)
    console.print()


def display_quiz_question(quiz: QuizQuestion, objective: str):
    """Display quiz question in formatted panels."""
    console.print()
    console.print(Panel.fit(f"[bold blue]Quiz Question[/bold blue]", padding=(0, 1)))
    console.print(f"[dim]Objective: {objective}[/dim]\n")

    # Question
    console.print(Panel(quiz.stem, title="[bold]Question[/bold]", border_style="blue"))

    # Choices
    all_choices = [quiz.correct_answer] + quiz.distractors
    choice_labels = ["a) ", "b) ", "c) ", "d) "]

    console.print("\n[bold]Choices:[/bold]")
    for label, choice in zip(choice_labels, all_choices):
        marker = "[green]✓[/green]" if choice == quiz.correct_answer else "  "
        console.print(f"  {marker} {label}{choice}")

    # Explanation
    console.print("\n" + "=" * 80)
    console.print(Panel(quiz.explanation, title="[bold]Explanation[/bold]", border_style="green"))
    console.print()


@app.command()
def generate_objectives(
    topic: str = typer.Option(..., "--topic", "-t", help="Course topic or title", prompt=True),
    target_audience: str = typer.Option(
        ...,
        "--target-audience",
        "-a",
        help="Target audience for the course",
        prompt=True
    ),
    num_objectives: int = typer.Option(
        6,
        "--num-objectives",
        "-n",
        help="Number of learning objectives to generate (1-12)",
        min=1,
        max=12,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output results as JSON instead of formatted text"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
):
    """
    Generate learning objectives using Bloom's Taxonomy.

    This command creates structured learning objectives based on the specified
    topic and target audience. Each objective uses an approved Bloom's verb
    appropriate for its cognitive level.

    Example:
        open-instruct generate-objectives --topic "Introduction to Python" \\
            --target-audience "Junior developers" --num-objectives 5
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"Generating {num_objectives} objectives for topic: {topic}")
    logger.info(f"Target audience: {target_audience}")

    try:
        # Test Ollama connection
        with console.status("[bold yellow]Testing Ollama connection...", spinner="dots"):
            result = test_ollama_connection()
            if result["status"] != "ok":
                print_error(f"Ollama connection failed: {result['error']}")
                logger.error(f"Ollama connection failed: {result['error']}")
                raise typer.Exit(1)
            print_success("Ollama connection established")

        # Configure DSPy
        with console.status("[bold yellow]Configuring DSPy...", spinner="dots"):
            lm = setup_dspy_with_ollama(auto_test=False)
            logger.info(f"DSPy configured with model: {lm.model}")

        # Initialize Architect module
        architect = Architect()
        logger.info("Architect module initialized")

        # Generate objectives with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[bold yellow]Generating learning objectives...",
                total=None
            )

            try:
                structure = architect.generate_objectives(
                    topic=topic,
                    target_audience=target_audience,
                    num_objectives=num_objectives,
                )
                progress.update(task, completed=True)
            except Exception as e:
                print_error(f"Failed to generate objectives: {e}")
                logger.error(f"Generation failed: {e}", exc_info=True)
                raise typer.Exit(1)

        # Output results
        if json_output:
            output = {
                "topic": structure.topic,
                "objectives": [
                    {
                        "id": obj.id,
                        "verb": obj.verb,
                        "content": obj.content,
                        "level": obj.level.value,
                    }
                    for obj in structure.objectives
                ],
                "generated_at": datetime.now().isoformat(),
            }
            console.print_json(json.dumps(output, indent=2))
        else:
            display_course_structure(structure)

        print_success(f"Generated {len(structure.objectives)} learning objectives")
        logger.info(f"Successfully generated {len(structure.objectives)} objectives")

    except OllamaConnectionError as e:
        print_error(f"Ollama connection error: {e}")
        logger.error(f"Ollama connection error: {e}", exc_info=True)
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise typer.Exit(1)


@app.command()
def generate_quiz(
    objective_id: str = typer.Option(
        ...,
        "--objective-id",
        "-i",
        help="Learning objective ID (e.g., LO-001)",
        prompt=True
    ),
    objective_text: str = typer.Option(
        ...,
        "--objective",
        "-o",
        help="Learning objective text (format: 'verb content')",
        prompt=True
    ),
    context: Optional[str] = typer.Option(
        None,
        "--context",
        "-c",
        help="Optional context about the course topic"
    ),
    level: str = typer.Option(
        "Understand",
        "--level",
        "-l",
        help="Bloom's cognitive level for the objective"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output results as JSON instead of formatted text"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
):
    """
    Generate a quiz question from a learning objective.

    This command creates a multiple-choice quiz question based on the specified
    learning objective. The question includes a stem, correct answer, 3 distractors,
    and an explanation.

    Example:
        open-instruct generate-quiz \\
            --objective-id "LO-001" \\
            --objective "explain the differences between supervised and unsupervised learning" \\
            --context "Introduction to Machine Learning"
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"Generating quiz for objective {objective_id}: {objective_text}")

    try:
        # Validate Bloom's level
        try:
            bloom_level = BloomLevel(level)
        except ValueError:
            print_error(f"Invalid Bloom's level: {level}")
            print_error(f"Valid levels: {', '.join([l.value for l in BloomLevel])}")
            logger.error(f"Invalid Bloom's level: {level}")
            raise typer.Exit(1)

        # Test Ollama connection
        with console.status("[bold yellow]Testing Ollama connection...", spinner="dots"):
            result = test_ollama_connection()
            if result["status"] != "ok":
                print_error(f"Ollama connection failed: {result['error']}")
                logger.error(f"Ollama connection failed: {result['error']}")
                raise typer.Exit(1)
            print_success("Ollama connection established")

        # Configure DSPy
        with console.status("[bold yellow]Configuring DSPy...", spinner="dots"):
            lm = setup_dspy_with_ollama(auto_test=False)
            logger.info(f"DSPy configured with model: {lm.model}")

        # Parse objective text into verb and content
        parts = objective_text.strip().split(maxsplit=1)
        if len(parts) < 2:
            print_error("Objective must be in format: 'verb content'")
            print_error("Example: 'explain the differences between supervised and unsupervised learning'")
            logger.error(f"Invalid objective format: {objective_text}")
            raise typer.Exit(1)

        verb, content = parts
        logger.info(f"Parsed objective - verb: {verb}, content: {content}")

        # Create LearningObjective instance
        learning_objective = LearningObjective(
            id=objective_id,
            verb=verb,
            content=content,
            level=bloom_level,
        )

        # Initialize Assessor module
        assessor = Assessor()
        logger.info("Assessor module initialized")

        # Generate quiz question with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[bold yellow]Generating quiz question...",
                total=None
            )

            try:
                quiz = assessor.generate_quiz(
                    objective=learning_objective,
                    context=context,
                )
                progress.update(task, completed=True)
            except Exception as e:
                print_error(f"Failed to generate quiz: {e}")
                logger.error(f"Quiz generation failed: {e}", exc_info=True)
                raise typer.Exit(1)

        # Output results
        if json_output:
            output = {
                "objective_id": objective_id,
                "objective_text": objective_text,
                "level": level,
                "question": {
                    "stem": quiz.stem,
                    "correct_answer": quiz.correct_answer,
                    "distractors": quiz.distractors,
                    "explanation": quiz.explanation,
                },
                "generated_at": datetime.now().isoformat(),
            }
            console.print_json(json.dumps(output, indent=2))
        else:
            display_quiz_question(quiz, objective_text)

        print_success("Quiz question generated successfully")
        logger.info("Successfully generated quiz question")

    except OllamaConnectionError as e:
        print_error(f"Ollama connection error: {e}")
        logger.error(f"Ollama connection error: {e}", exc_info=True)
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise typer.Exit(1)


@app.command()
def test_connection(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output"
    ),
):
    """
    Test the connection to Ollama server.

    This command verifies that the Ollama server is running and accessible,
    and checks if the configured model is available.

    Example:
        open-instruct test-connection
    """
    logger.info("Testing Ollama connection")

    with console.status("[bold yellow]Testing Ollama connection...", spinner="dots"):
        result = test_ollama_connection()

    if result["status"] == "ok":
        print_success(result["message"])
        console.print(f"[dim]Base URL: {result['base_url']}[/dim]")

        if verbose:
            from src.core.dspy_client import verify_model_availability, get_model_info
            model_info = get_model_info()
            console.print(f"\n[bold]Model Configuration:[/bold]")
            console.print(f"  Provider: {model_info['provider']}")
            console.print(f"  Model: {model_info['model']}")
            console.print(f"  Base URL: {model_info['base_url']}")
            console.print(f"  Configured: {model_info['configured']}")

        logger.info("Ollama connection test successful")
        raise typer.Exit(0)
    else:
        print_error(result["message"])
        console.print(f"[dim]Base URL: {result['base_url']}[/dim]")
        if result.get("error"):
            console.print(f"[red]Error: {result['error']}[/red]")
        logger.error(f"Ollama connection test failed: {result.get('error')}")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version and exit."""
    console.print("[bold blue]Open-Instruct[/bold blue] version [green]0.1.0[/green]")
    console.print("[dim]Bloom's Taxonomy-based educational content generation[/dim]")
    raise typer.Exit(0)


if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        logger.info("Operation cancelled by user")
        sys.exit(130)
