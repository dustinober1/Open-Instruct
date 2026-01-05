Project Charter: Open-Instruction
Goal: Build an open-source, local-first engine that uses AI (DSPy) to generate structured, pedagogically sound educational courseware (Objectives, Content, Quizzes) suitable for export to standard LMS formats.

Target User: Instructional Designers (IDs) and Developers building EdTech tools.

Core Philosophy: "Structure over Syntax." We don't just generate text; we generate valid JSON objects aligned with Bloom's Taxonomy.

1. System Requirements Specification (SRS)
1.1 Functional Requirements (FR)
FR-01 (Taxonomy Alignment): The system must accept a raw topic and output Learning Objectives that strictly adhere to a specified Bloom’s Taxonomy level (e.g., if "Analyze" is selected, verbs must be analytical, not recall-based).

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
This list is broken down into logical "Sprints" or Phases.

Phase 1: Core Logic & CLI (The Engine)
Focus: Getting the "Brain" working without a UI.

[ ] Task 1.1: Repo Initialization

Action: Initialize Git repo. Create virtualenv. Create requirements.txt containing dspy, pydantic, pytest.

Outcome: A clean environment ready for code.

[ ] Task 1.2: Define Pydantic Models (The "Contract")

Action: Create src/models.py. Define classes for LearningObjective, LessonContent, and QuizItem.

Guidance: Ensure strict typing (e.g., bloom_level should be an Enum, not a string).

[ ] Task 1.3: Configure DSPy Client

Action: Create src/llm_config.py. Set up the connection to Ollama (base_url usually http://localhost:11434).

Note: Add a fallback to a dummy/mock model for testing without a GPU.

[ ] Task 1.4: Build "The Architect" Module (Objectives)

Action: Implement dspy.Signature and dspy.Module for generating objectives.

Acceptance Criteria: Input "Photosynthesis" + Level "Recall" -> Output list of objectives using verbs like "Define", "List", "State".

[ ] Task 1.5: Build "The Assessor" Module (Quizzes)

Action: Implement dspy.Signature for generating a Multiple Choice Question (MCQ) from a given Objective.

Acceptance Criteria: Output must separate correct_answer from distractors list.

[ ] Task 1.6: Create CLI Entry Point

Action: Create main.py using typer or argparse.

Outcome: Running python main.py "History of AI" --json prints a full course structure to stdout.

Phase 2: The API Layer
Focus: Exposing the engine to the web.

[ ] Task 2.1: FastAPI Skeleton

Action: Install fastapi and uvicorn. Create app/main.py.

Outcome: GET /health returns 200 OK.

[ ] Task 2.2: Endpoint - Generate Syllabus

Action: Create POST /api/v1/generate/objectives. Accepts { topic: str, level: str }.

Logic: Calls the DSPy module from Task 1.4. Returns JSON.

[ ] Task 2.3: Endpoint - Expand Module

Action: Create POST /api/v1/generate/content. Accepts { objective_id: str }.

Logic: Generates the actual lesson text and quiz for a specific node.

[ ] Task 2.4: Async Integration

Action: Ensure DSPy calls do not block the main thread (use fastapi.concurrency.run_in_threadpool if DSPy methods aren't natively async yet).

Phase 3: The Frontend (Course Builder)
Focus: Visualizing the curriculum.

[ ] Task 3.1: Next.js Setup

Action: npx create-next-app@latest. Install shadcn/ui components (Button, Input, Card).

[ ] Task 3.2: Store Setup (Zustand)

Action: Set up a global store to hold the "Course State" (the list of modules and their content).

Why: We need to persist the course data as the user navigates between different views.

[ ] Task 3.3: The "Curriculum Graph" View

Action: Integrate reactflow.

Logic: Map the JSON response from the API to React Flow nodes.

Outcome: User types a topic -> A tree graph appears on screen.

[ ] Task 3.4: Module Editor View

Action: Clicking a node opens a side panel (Sheet/Drawer) showing the generated content.

Feature: Add an "Edit" button to manually tweak the AI generation.

[ ] Task 3.5: Export Button

Action: specific button that downloads the current state as course.json.

3. Developer "Cheat Sheet"
Give this section to the junior dev to unblock them before they start.

1. How to run the local LLM:

"Before you start coding, make sure you have Ollama installed. Run ollama run llama3. This will open a server on port 11434. Our DSPy config will talk to this port."

2. Key DSPy Concept:

"Don't write long prompts. Write Signatures. A Signature is just a Python class that defines Input fields and Output fields. DSPy figures out the prompt for you. If the output is wrong, don't change the prompt—add a DSPy Assertion."

3. Project Structure Reference:

Bash

open-instruction/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI Routes
│   │   └── main.py       # Server entry
│   ├── core/
│   │   ├── dspy_modules/ # The "Brains" (Signatures)
│   │   └── models.py     # Pydantic Schemas
│   └── requirements.txt
├── frontend/             # Next.js App
└── README.md