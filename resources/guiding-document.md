Project Charter: Open-Instruction
Goal: Build an open-source, local-first engine that uses AI (DSPy) to generate structured, pedagogically sound educational courseware (Objectives, Content, Quizzes) suitable for export to standard LMS formats.

Target User: Instructional Designers (IDs) and Developers building EdTech tools.

Core Philosophy: "Structure over Syntax." We don't just generate text; we generate valid JSON objects aligned with Bloom's Taxonomy.

1. System Requirements Specification (SRS)
1.1 Functional Requirements (FR)
FR-01 (Taxonomy Alignment): The system must accept a raw topic and output Learning Objectives tagged with Bloom’s Taxonomy levels, where each objective’s verb strictly matches the approved verb list for its assigned level (e.g., objectives tagged "Analyze" must use analytical verbs, not recall verbs).

FR-02 (Structured Output): All AI outputs must be returned as validated JSON objects, not raw strings.

FR-03 (Distractor Logic): The Quiz Module must generate one correct answer and three "distractors" (plausible incorrect answers).

FR-04 (Format Agnosticism): The internal data model must be convertible to standard educational formats (JSON, Markdown, and eventually SCORM/xAPI).

FR-05 (Local Execution): The system must be capable of running offline using local LLMs (e.g., Llama 3 via Ollama) to ensure data privacy.

1.2 Non-Functional Requirements (NFR)
NFR-01 (Modularity): The DSPy logic (Backend) must be decoupled from the UI (Frontend) via a REST API.

NFR-02 (Type Safety): All backend code must use Pydantic models for data validation.

NFR-03 (Documentation): All API endpoints must have auto-generated Swagger/Redoc documentation.

1.3 Tech Stack Constraints
Language: Python 3.10+

AI Framework: DSPy (latest version)

Backend Framework: FastAPI

Frontend Framework: Next.js (App Router) + React Flow

Local LLM Host: Ollama

2. Implementation Roadmap (Task List)
This list is intentionally high-level. The detailed execution plan, acceptance criteria, and risks live in `documentation/implementation-plan.md`.

Phase 1: Environment & Core Logic Setup
Focus: Establish the "contract" and confirm the local LLM connection.

[ ] Task 1.1: Project Skeleton + Dependencies

Action: Create `backend/` structure, set up a virtualenv, and install core dependencies (`dspy-ai`, `pydantic`, `pytest`, etc.).

Outcome: Running Python from `backend/` works, and dependencies import cleanly.

[ ] Task 1.2: Define Pydantic Models (The "Contract")

Action: Create `backend/src/core/models.py`. Define `BloomLevel`, `LearningObjective`, `CourseStructure`, and `QuizQuestion`.

Guidance: Bloom levels are enums; verbs are validated against approved lists.

[ ] Task 1.3: Configure DSPy Client

Action: Create `backend/src/core/dspy_client.py`. Connect DSPy to Ollama (`http://localhost:11434`) and set a default model (e.g., `deepseek-r1:1.5b`).

Note: Provide a mock/dummy LM for unit tests (no real LLM calls required).

Phase 2: DSPy Modules + CLI
Focus: Reliable structured generation before any UI.

[ ] Task 2.1: Build "The Architect" Module (Objectives)

Action: Implement a `dspy.Signature` + `dspy.Module` that generates objectives and returns a validated `CourseStructure`.

Acceptance Criteria: Input "Photosynthesis" -> Output objectives where each objective’s `level` is one of the 6 Bloom levels and each `verb` matches the approved list for that level.

[ ] Task 2.2: Build "The Assessor" Module (Quizzes)

Action: Implement a `dspy.Signature` that generates one MCQ per objective.

Acceptance Criteria: Output separates `correct_answer` from exactly 3 unique `distractors`.

[ ] Task 2.3: Create CLI Entry Point

Action: Create `backend/src/main.py` using Typer (or argparse).

Outcome: From `backend/`, running `python -m src.main "History of AI" --json` prints a full course structure to stdout.

Phase 3: The API Layer
Focus: Expose the engine via REST.

[ ] Task 3.1: FastAPI Skeleton

Action: Install `fastapi` and `uvicorn`. Create `backend/src/api/main.py`.

Outcome: `GET /health` returns 200 OK.

[ ] Task 3.2: Core Generation Endpoints

Action: Implement:
- `POST /api/v1/generate/objectives` (topic, target_audience, num_objectives)
- `POST /api/v1/generate/quiz` (objective_id, difficulty)

Logic: Wrap DSPy module calls and return validated JSON.

[ ] Task 3.3: Async Integration

Action: Ensure DSPy calls do not block the event loop (use `fastapi.concurrency.run_in_threadpool` if needed).

Phase 4: The Frontend (Course Builder)
Focus: Visualize and edit the curriculum.

[ ] Task 4.1: Next.js Setup

Action: `npx create-next-app@latest`. Install `shadcn/ui` components (Button, Input, Card).

[ ] Task 4.2: Curriculum Graph View

Action: Integrate React Flow and map API objectives to nodes.

[ ] Task 4.3: Module Editor View

Action: Clicking a node opens a side panel showing generated content with an "Edit" button.

Phase 5: Export & Import
Focus: Share generated courses.

[ ] Task 5.1: Export Button

Action: Add a button that downloads the current course state as versioned JSON.

3. Developer "Cheat Sheet"
Give this section to the junior dev to unblock them before they start.

1. How to run the local LLM:

"Before you start coding, make sure you have Ollama installed and running. Start the service with `ollama serve` and pull the default model with `ollama pull deepseek-r1:1.5b`. Our DSPy config talks to `http://localhost:11434`."

2. Key DSPy Concept:

"Don't write long prompts. Write Signatures. A Signature is just a Python class that defines Input fields and Output fields. DSPy figures out the prompt for you. If the output is wrong, don't change the prompt—add a DSPy Assertion."

3. Project Structure Reference:

Bash

open-instruction/
├── backend/
│   ├── src/
│   │   ├── api/          # FastAPI app + routers
│   │   ├── core/         # Config, DSPy client, Pydantic models
│   │   ├── modules/      # DSPy modules ("Brains")
│   │   └── main.py       # CLI entry point
│   ├── tests/            # pytest suite
│   ├── requirements.txt
│   └── .env
├── frontend/             # Next.js App
└── README.md
