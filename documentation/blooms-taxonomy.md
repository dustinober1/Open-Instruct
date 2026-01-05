# Bloom's Taxonomy Specification

**Audience**: Junior Developers
**Purpose**: Complete verb lists and validation rules for all 6 cognitive levels
**Status**: Implementation Requirement - MUST be implemented exactly as specified

---

## Table of Contents
1. [Overview](#overview)
2. [The 6 Cognitive Levels](#the-6-cognitive-levels)
3. [Complete Verb Lists](#complete-verb-lists)
4. [Implementation Specification](#implementation-specification)
5. [Validation Rules](#validation-rules)
6. [Usage Examples](#usage-examples)
7. [Common Mistakes](#common-mistakes)

---

## Overview

### What is Bloom's Taxonomy?

Bloom's Taxonomy is a hierarchical classification of cognitive learning objectives. It's used to design curricula and assess student learning.

### Why Use It in Open-Instruct?

1. **Structured Learning**: Ensures objectives progress from basic to advanced
2. **Assessment Alignment**: Quiz questions match the cognitive level
3. **Educational Quality**: Proven framework for effective instruction

### Our Implementation

- **6 Levels**: Remember, Understand, Apply, Analyze, Evaluate, Create
- **30 Verbs Per Level**: Curated list of appropriate action verbs
- **Strict Validation**: LLM must use verbs from approved lists
- **Manual Override**: Users can edit in frontend if needed

---

## The 6 Cognitive Levels

### Visual Hierarchy

```
┌─────────────────────────────────────────┐
│ Level 6: CREATE (Highest)               │
│ • Design, construct, formulate          │
└─────────────────────────────────────────┘
                ↑
┌─────────────────────────────────────────┐
│ Level 5: EVALUATE                       │
│ • Judge, assess, critique               │
└─────────────────────────────────────────┘
                ↑
┌─────────────────────────────────────────┐
│ Level 4: ANALYZE                        │
│ • Differentiate, examine, compare       │
└─────────────────────────────────────────┘
                ↑
┌─────────────────────────────────────────┐
│ Level 3: APPLY                          │
│ • Use, implement, execute               │
└─────────────────────────────────────────┘
                ↑
┌─────────────────────────────────────────┐
│ Level 2: UNDERSTAND                     │
│ • Explain, describe, summarize          │
└─────────────────────────────────────────┘
                ↑
┌─────────────────────────────────────────┐
│ Level 1: REMEMBER (Lowest)              │
│ • List, name, define, identify          │
└─────────────────────────────────────────┘
```

### Level Progression Rule

**Learning objectives should generally follow this order**:
1. Start with REMEMBER (basic facts)
2. Move to UNDERSTAND (comprehension)
3. Then APPLY (using knowledge)
4. Next ANALYZE (breaking down)
5. Then EVALUATE (judging)
6. Finally CREATE (producing something new)

**Example: Python Functions Course**
```
LO-001: [Remember] Define what a function is
LO-002: [Understand] Explain function parameters
LO-003: [Apply] Write a simple function
LO-004: [Analyze] Compare different parameter types
LO-005: [Evaluate] Assess when to use functions vs loops
LO-006: [Create] Design a modular program using functions
```

---

## Complete Verb Lists

### Level 1: REMEMBER

**Definition**: Retrieve, recall, and recognize relevant knowledge from long-term memory

**30 Approved Verbs**:

| # | Verb | Example Objective |
|---|------|------------------|
| 1 | **define** | Define what a variable is in Python |
| 2 | **list** | List three primitive data types in JavaScript |
| 3 | **name** | Name the four main parts of a HTTP request |
| 4 | **identify** | Identify the correct syntax for a for-loop |
| 5 | **recall** | Recall the default TCP port for HTTPS |
| 6 | **recognize** | Recognize valid JSON format |
| 7 | **label** | Label the components of a REST API URL |
| 8 | **match** | Match SQL commands to their purposes |
| 9 | **memorize** | Memorize the order of CSS specificity |
| 10 | **repeat** | Repeat the steps of the Git commit workflow |
| 11 | **state** | State the purpose of normalization in databases |
| 12 | **select** | Select the correct data structure for key-value pairs |
| 13 | **locate** | Locate the closing tag in an HTML fragment |
| 14 | **tell** | Tell the difference between GET and POST |
| 15 | **quote** | Quote the exact syntax for defining a class in Python |
| 16 | **enumerate** | Enumerate the three pillars of object-oriented programming |
| 17 | **outline** | Outline the main phases of the software development lifecycle |
| 18 | **describe** | Describe the role of a package manager |
| 19 | **who** | Who created the Git version control system? |
| 20 | **what** | What does the acronym API stand for? |
| 21 | **when** | When would you use a NoSQL database? |
| 22 | **where** | Where should error handling be placed in code? |
| 23 | **which** | Which HTTP status code indicates success? |
| 24 | **how** | How many bits are in a byte? |
| 25 | **show** | Show the correct indentation for Python code blocks |
| 26 | **mark** | Mark the correct answer in a multiple choice question |
| 27 | **spell** | Spell the keyword for declaring a constant in JavaScript |
| 28 | **find** | Find the syntax error in this code snippet |
| 29 | **cite** | Cite the year Python 3.0 was released |
| 30 | **tabulate** | Tabulate the main differences between SQL and NoSQL |

---

### Level 2: UNDERSTAND

**Definition**: Grasp the meaning of material, interpret, paraphrase, and explain ideas

**30 Approved Verbs**:

| # | Verb | Example Objective |
|---|------|------------------|
| 1 | **explain** | Explain the concept of recursion in programming |
| 2 | **describe** | Describe how client-server communication works |
| 3 | **summarize** | Summarize the software development lifecycle in 3 steps |
| 4 | **interpret** | Interpret the meaning of HTTP status code 404 |
| 5 | **paraphrase** | Paraphrase the purpose of encapsulation in OOP |
| 6 | **clarify** | Clarify the difference between == and === in JavaScript |
| 7 | **discuss** | Discuss the trade-offs between monolithic and microservices architectures |
| 8 | **illustrate** | Illustrate how DNS resolution works with a diagram |
| 9 | **demonstrate** | Demonstrate the use of list comprehensions in Python |
| 10 | **exemplify** | Exemplify when to use inheritance vs composition |
| 11 | **rephrase** | Rephrase the definition of Big O notation |
| 12 | **translate** | Translate pseudocode into valid Python syntax |
| 13 | **convert** | Convert a Fahrenheit temperature to Celsius in code |
| 14 | **estimate** | Estimate the time complexity of a nested loop |
| 15 | **infer** | Infer the purpose of a function from its name |
| 16 | **predict** | Predict the output of this code snippet |
| 17 | **conclude** | Conclude why this algorithm will fail with empty input |
| 18 | **differentiate** | Differentiate between shallow and deep copy |
| 19 | **distinguish** | Distinguish between syntax errors and runtime errors |
| 20 | **compare** | Compare arrays and linked lists in terms of access time |
| 21 | **contrast** | Contrast synchronous and asynchronous programming |
| 22 | **extend** | Extend the concept of variables to function parameters |
| 23 | **generalize** | Generalize the pattern from these three examples |
| 24 | **give examples** | Give examples of when to use NoSQL databases |
| 25 | **restate** | Restate the problem in your own words |
| 26 | **express** | Express the relationship between classes and objects |
| 27 | **indicate** | Indicate which line causes the memory leak |
| 28 | **reason** | Reason about why this function returns None |
| 29 | **derive** | Derive the formula for calculating array indices |
| 30 | **grasp** | Grasp the concept of callback hell in JavaScript |

---

### Level 3: APPLY

**Definition**: Use learned material in new and concrete situations, apply rules, methods, concepts

**30 Approved Verbs**:

| # | Verb | Example Objective |
|---|------|------------------|
| 1 | **apply** | Apply the DRY principle to refactor duplicate code |
| 2 | **use** | Use Git commands to create and switch branches |
| 3 | **implement** | Implement a binary search algorithm in Python |
| 4 | **execute** | Execute a SQL query to find duplicates in a table |
| 5 | **employ** | Employ exception handling to catch file access errors |
| 6 | **utilize** | Utilize list slicing to reverse an array |
| 7 | **practice** | Practice writing test cases for this function |
| 8 | **perform** | Perform a code review on this pull request |
| 9 | **operate** | Operate the Docker CLI to build and run containers |
| 10 | **manipulate** | Manipulate strings using regular expressions |
| 11 | **modify** | Modify this function to accept optional parameters |
| 12 | **change** | Change the CSS to center this div |
| 13 | **solve** | Solve this algorithm problem using dynamic programming |
| 4 | **calculate** | Calculate the space complexity of this algorithm |
| 15 | **compute** | Compute the sum of all even numbers in a list |
| 16 | **determine** | Determine if a number is prime using Python |
| 17 | **discover** | Discover bugs in this code using a debugger |
| 18 | **verify** | Verify that this function handles edge cases |
| 19 | **validate** | Validate user input before processing |
| 20 | **check** | Check if a string contains only alphanumeric characters |
| 21 | **test** | Test this API endpoint with various inputs |
| 22 | **debug** | Debug this failing test case |
| 23 | **trace** | Trace the execution flow of this recursive function |
| 24 | **run** | Run the linter to identify code quality issues |
| 25 | **build** | Build a simple REST API using Express.js |
| 26 | **construct** | Construct a valid JSON object from user input |
| 27 | **create** | Create a new Git repository and make initial commit |
| 28 | **generate** | Generate Fibonacci sequence up to n terms |
| 29 | **produce** | Produce a formatted date string from timestamp |
| 30 | **develop** | Develop a simple web scraper using BeautifulSoup |

---

### Level 4: ANALYZE

**Definition**: Break material into constituent parts, determine how parts relate, and understand structure

**30 Approved Verbs**:

| # | Verb | Example Objective |
|---|------|------------------|
| 1 | **analyze** | Analyze the time complexity of this algorithm |
| 2 | **differentiate** | Differentiate between breadth-first and depth-first search |
| 3 | **distinguish** | Distinguish between stack and heap memory |
| 4 | **examine** | Examine the code for potential security vulnerabilities |
| 5 | **investigate** | Investigate why this API call is slow |
| 6 | **inspect** | Inspect the HTTP headers of this request |
| 7 | **explore** | Explore the relationship between classes in this diagram |
| 8 | **compare** | Compare the performance of two sorting algorithms |
| 9 | **contrast** | Contrast functional and object-oriented programming paradigms |
| 10 | **categorize** | Categorize these data structures by access time |
| 11 | **classify** | Classify these bugs by type (syntax, runtime, logic) |
| 12 | **break down** | Break down this complex function into smaller steps |
| 3 | **deconstruct** | Deconstruct this monolithic function into pure functions |
| 14 | **separate** | Separate concerns between model, view, and controller |
| 15 | **discriminate** | Discriminate between essential and optional code features |
| 16 | **detect** | Detect code smells in this legacy codebase |
| 17 | **identify patterns** | Identify design patterns in this architecture |
| 18 | **recognize structure** | Recognize the MVC pattern in this framework |
| 19 | **find** | Find the root cause of this race condition |
| 20 | **diagnose** | Diagnose the memory leak in this application |
| 21 | **troubleshoot** | Troubleshoot the failing database connection |
| 22 | **audit** | Audit the code for SQL injection vulnerabilities |
| 23 | **review** | Review the architecture for scalability issues |
| 24 | **assess** | Assess the maintainability of this codebase |
| 25 | **evaluate** | Evaluate the trade-offs of different authentication methods |
| 26 | **organize** | Organize these requirements by priority |
| 27 | **outline** | Outline the component hierarchy of this React app |
| 28 | **structure** | Structure the database schema for this application |
| 29 | **map** | Map the dependencies between these modules |
| 30 | **profile** | Profile the code to identify performance bottlenecks |

---

### Level 5: EVALUATE

**Definition**: Make judgments based on criteria and standards, assess quality and effectiveness

**30 Approved Verbs**:

| # | Verb | Example Objective |
|---|------|------------------|
| 1 | **evaluate** | Evaluate the effectiveness of this caching strategy |
| 2 | **assess** | Assess the quality of this test suite |
| 3 | **judge** | Judge whether this algorithm is appropriate for the problem |
| 4 | **appraise** | Appraise the security of this authentication system |
| 5 | **estimate** | Estimate the development time for this feature |
| 6 | **measure** | Measure the performance improvement after optimization |
| 7 | **rate** | Rate the readability of this code on a scale of 1-10 |
| 8 | **score** | Score this pull request against the code review checklist |
| 9 | **value** | Value the importance of documentation in open-source projects |
| 10 | **critique** | Critique the design of this REST API |
| 11 | **criticize** | Criticize the choice of data structure for this use case |
| 12 | **recommend** | Recommend the best database for this application |
| 13 | **advise** | Advise on the best practices for error handling |
| 14 | **select** | Select the most appropriate design pattern for this problem |
| 15 | **choose** | Choose between REST and GraphQL for this API |
| 16 | **prefer** | Prefer functional or object-oriented approach for this task |
| 17 | **defend** | Defend the architectural decisions in this design document |
| 18 | **justify** | Justify the use of microservices over monolithic architecture |
| 19 | **validate** | Validate that the solution meets all requirements |
| 20 | **verify** | Verify the correctness of this proof |
| 21 | **confirm** | Confirm that all edge cases are handled |
| 22 | **corroborate** | Corroborate the benchmark results with independent testing |
| 23 | **support** | Support your choice of algorithm with evidence |
| 24 | **argue** | Argue for or against the use of TypeScript in this project |
| 25 | **debate** | Debate the merits of synchronous vs asynchronous error handling |
| 26 | **dispute** | Dispute the claim that this code is O(1) space complexity |
| 27 | **question** | Question the necessity of this abstraction layer |
| 28 | **challenge** | Challenge the assumption that this scaling approach will work |
| 29 | **weigh** | Weigh the pros and cons of using a third-party library |
| 30 | **prioritize** | Prioritize which bugs to fix first based on impact |

---

### Level 6: CREATE

**Definition**: Put elements together to form a coherent whole, reorganize into new patterns or structures

**30 Approved Verbs**:

| # | Verb | Example Objective |
|---|------|------------------|
| 1 | **create** | Create a RESTful API from scratch using Express.js |
| 2 | **design** | Design a database schema for an e-commerce platform |
| 3 | **construct** | Construct a binary search tree from an array |
| 4 | **build** | Build a responsive web page using HTML and CSS |
| 5 | **develop** | Develop a machine learning model for classification |
| 6 | **formulate** | Formulate a hypothesis for why the system fails under load |
| 7 | **generate** | Generate test data for unit testing |
| 8 | **produce** | Produce a technical documentation for this API |
| 9 | **manufacture** | Manufacture a reusable component library |
| 10 | **compose** | Compose a modular program using functions |
| 11 | **assemble** | Assemble a full-stack application from individual components |
| 12 | **combine** | Combine multiple algorithms to solve a complex problem |
| 13 | **integrate** | Integrate a third-party payment gateway into the app |
| 14 | **merge** | Merge two sorted arrays into one sorted array |
| 15 | **blend** | Blend object-oriented and functional programming paradigms |
| 16 | **synthesize** | Synthesize a solution from multiple design patterns |
| 17 | **originate** | Originate a new approach to solving the caching problem |
| 18 | **devise** | Devise a strategy for handling race conditions |
| 19 | **invent** | Invent a custom data structure optimized for this use case |
| 20 | **concoct** | Concoct a creative solution to the CAP theorem dilemma |
| 21 | **plan** | Plan the architecture for a scalable microservices system |
| 22 | **propose** | Propose an alternative to the existing authentication flow |
| 23 | **draft** | Draft a specification for the new API endpoint |
| 24 | **outline** | Outline a learning path for full-stack web development |
| 25 | **structure** | Structure the project files according to MVC pattern |
| 26 | **organize** | Organize the codebase into logical modules |
| 27 | **arrange** | Arrange the components in a React application |
| 28 | **author** | Author a reusable Python package for data validation |
| 29 | **fabricate** | Fabricate a custom middleware for Express.js |
| 30 | **derive** | Derive a new algorithm by combining two existing ones |

---

## Implementation Specification

### File Structure

```python
# src/core/models.py

from enum import Enum
from typing import Dict, List

class BloomLevel(str, Enum):
    """Bloom's Taxonomy cognitive levels."""
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


class BloomsTaxonomy:
    """Encapsulate Bloom's Taxonomy verb lists and validation logic."""

    # Complete verb lists (DO NOT MODIFY WITHOUT TEAM APPROVAL)
    VERBS: Dict[str, List[str]] = {
        "Remember": [
            "define", "list", "name", "identify", "recall", "recognize",
            "label", "match", "memorize", "repeat", "state", "select",
            "locate", "tell", "quote", "enumerate", "outline", "describe",
            "who", "what", "when", "where", "which", "how", "show",
            "mark", "spell", "find", "cite", "tabulate"
        ],
        "Understand": [
            "explain", "describe", "summarize", "interpret", "paraphrase",
            "clarify", "discuss", "illustrate", "demonstrate", "exemplify",
            "rephrase", "translate", "convert", "estimate", "infer",
            "predict", "conclude", "differentiate", "distinguish", "compare",
            "contrast", "extend", "generalize", "give examples", "restate",
            "express", "indicate", "reason", "derive", "grasp"
        ],
        "Apply": [
            "apply", "use", "implement", "execute", "employ",
            "utilize", "practice", "perform", "operate", "manipulate",
            "modify", "change", "solve", "calculate", "compute",
            "determine", "discover", "verify", "validate", "check",
            "test", "debug", "trace", "run", "build",
            "construct", "create", "generate", "produce", "develop"
        ],
        "Analyze": [
            "analyze", "differentiate", "distinguish", "examine", "investigate",
            "inspect", "explore", "compare", "contrast", "categorize",
            "classify", "break down", "deconstruct", "separate", "discriminate",
            "detect", "identify patterns", "recognize structure", "find", "diagnose",
            "troubleshoot", "audit", "review", "assess", "evaluate",
            "organize", "outline", "structure", "map", "profile"
        ],
        "Evaluate": [
            "evaluate", "assess", "judge", "appraise", "estimate",
            "measure", "rate", "score", "value", "critique",
            "criticize", "recommend", "advise", "select", "choose",
            "prefer", "defend", "justify", "validate", "verify",
            "confirm", "corroborate", "support", "argue", "debate",
            "dispute", "question", "challenge", "weigh", "prioritize"
        ],
        "Create": [
            "create", "design", "construct", "build", "develop",
            "formulate", "generate", "produce", "manufacture", "compose",
            "assemble", "combine", "integrate", "merge", "blend",
            "synthesize", "originate", "devise", "invent", "concoct",
            "plan", "propose", "draft", "outline", "structure",
            "organize", "arrange", "author", "fabricate", "derive"
        ]
    }

    @classmethod
    def validate_verb(cls, verb: str, level: str) -> bool:
        """
        Check if verb is valid for given Bloom's level.

        Args:
            verb: The action verb to check
            level: The Bloom's level (e.g., "Remember")

        Returns:
            True if verb is approved for this level, False otherwise
        """
        approved_verbs = cls.VERBS.get(level, [])
        return verb.lower() in [v.lower() for v in approved_verbs]

    @classmethod
    def get_random_verb(cls, level: str) -> str:
        """
        Get a random verb from the specified level.

        Useful for testing or fallback generation.
        """
        import random
        verbs = cls.VERBS.get(level, [])
        return random.choice(verbs) if verbs else "demonstrate"

    @classmethod
    def get_all_verbs(cls) -> Dict[str, List[str]]:
        """Return complete verb list for all levels."""
        return cls.VERBS.copy()
```

---

## Validation Rules

### Rule 1: Verb Must Match Level

```python
# ✅ VALID
LearningObjective(
    verb="define",  # "define" is in Remember list
    level=BloomLevel.REMEMBER
)

# ❌ INVALID
LearningObjective(
    verb="evaluate",  # "evaluate" is NOT in Remember list
    level=BloomLevel.REMEMBER
)
```

### Rule 2: Case-Insensitive Matching

```python
# All of these are VALID (case-insensitive)
validate_verb("Define", "Remember")  # True
validate_verb("DEFINE", "Remember")  # True
validate_verb("define", "Remember")  # True
```

### Rule 3: Multi-Word Verbs

Some verbs contain spaces - handle them correctly:

```python
# Special case: multi-word verbs
multi_word_verbs = [
    "give examples",  # Understand
    "identify patterns",  # Analyze
    "recognize structure"  # Analyze
]

# Implementation should strip and lowercase
def normalize_verb(verb: str) -> str:
    return verb.strip().lower()

def is_multi_word(verb: str) -> bool:
    return " " in verb
```

### Rule 4: LLM Output Validation

When parsing LLM output, enforce verb validation:

```python
# src/modules/architect.py

class Architect(dspy.Module):
    def forward(self, topic: str, target_audience: str) -> CourseStructure:
        # ... generate objectives from LLM ...

        # Validate each objective
        validated_objectives = []
        for obj in raw_objectives:
            # Check verb
            if not BloomsTaxonomy.validate_verb(obj["verb"], obj["level"]):
                # Try to find closest match OR fallback verb
                fallback = BloomsTaxonomy.get_random_verb(obj["level"])
                obj["verb"] = fallback

            validated_objectives.append(LearningObjective(**obj))

        return CourseStructure(
            topic=topic,
            objectives=validated_objectives
        )
```

---

## Usage Examples

### Example 1: Complete Course Structure

```python
from src.core.models import CourseStructure, LearningObjective, BloomLevel

course = CourseStructure(
    topic="Python Functions for Beginners",
    objectives=[
        # REMEMBER (basic facts)
        LearningObjective(
            id="LO-001",
            verb="define",
            content="what a function is and why we use them",
            level=BloomLevel.REMEMBER
        ),

        # UNDERSTAND (comprehension)
        LearningObjective(
            id="LO-002",
            verb="explain",
            content="the difference between parameters and arguments",
            level=BloomLevel.UNDERSTAND
        ),

        # APPLY (using knowledge)
        LearningObjective(
            id="LO-003",
            verb="write",
            content="a simple function that greets the user",
            level=BloomLevel.APPLY
        ),

        # ANALYZE (breaking down)
        LearningObjective(
            id="LO-004",
            verb="compare",
            content="positional vs keyword arguments",
            level=BloomLevel.ANALYZE
        ),

        # EVALUATE (judging)
        LearningObjective(
            id="LO-005",
            verb="assess",
            content="when to use default parameter values",
            level=BloomLevel.EVALUATE
        ),

        # CREATE (producing something new)
        LearningObjective(
            id="LO-006",
            verb="design",
            content="a modular program using multiple functions",
            level=BloomLevel.CREATE
        )
    ]
)
```

### Example 2: Validation in Action

```python
# Test invalid verb
obj = LearningObjective(
    id="LO-001",
    verb="create",  # This is CREATE level, not REMEMBER!
    content="a new variable",
    level=BloomLevel.REMEMBER
)

# Validation should FAIL
assert BloomsTaxonomy.validate_verb("create", "Remember") == False

# Fix: Use correct level
obj = LearningObjective(
    id="LO-001",
    verb="create",
    content="a new variable",
    level=BloomLevel.CREATE  # Correct level!
)

# Validation PASSES
assert BloomsTaxonomy.validate_verb("create", "Create") == True
```

### Example 3: DSPy Assertion

```python
import dspy

class GenerateObjectives(dspy.Signature):
    """Generate learning objectives using Bloom's Taxonomy."""

    topic = dspy.InputField(desc="The course topic")
    target_audience = dspy.InputField(desc="Who is learning")
    objectives = dspy.OutputField(desc="List of learning objectives")

# Add assertion to enforce verb validation
@dspy.assertion
def verbs_match_blooms_level(obj: LearningObjective) -> bool:
    """Ensure verb is valid for the given Bloom's level."""
    return BloomsTaxonomy.validate_verb(obj.verb, obj.level)
```

---

## Common Mistakes

### ❌ Mistake 1: Using Verbs from Wrong Level

```python
# WRONG: "create" is CREATE level, not REMEMBER
LearningObjective(
    verb="create",
    level=BloomLevel.REMEMBER  # Wrong level!
)

# CORRECT: Use "define" for REMEMBER
LearningObjective(
    verb="define",
    level=BloomLevel.REMEMBER
)
```

### ❌ Mistake 2: Skipping Levels

```python
# BAD: Jump from REMEMBER to EVALUATE
objectives = [
    LearningObjective(verb="define", level=Remember),
    LearningObjective(verb="assess", level=Evaluate)  # Too big jump!
]

# GOOD: Progressive difficulty
objectives = [
    LearningObjective(verb="define", level=Remember),
    LearningObjective(verb="explain", level=Understand),
    LearningObjective(verb="use", level=Apply),
    LearningObjective(verb="assess", level=Evaluate)
]
```

### ❌ Mistake 3: Allowing Custom Verbs

```python
# BAD: Let LLM use any verb
def validate_verb(verb, level):
    return True  # No validation!

# GOOD: Enforce approved verb list
def validate_verb(verb, level):
    approved = BloomsTaxonomy.VERBS.get(level, [])
    return verb.lower() in [v.lower() for v in approved]
```

### ❌ Mistake 4: Case-Sensitive Comparison

```python
# BAD: Case-sensitive (fails on "Define" vs "define")
if verb in approved_verbs:
    return True

# GOOD: Case-insensitive
if verb.lower() in [v.lower() for v in approved_verbs]:
    return True
```

### ❌ Mistake 5: Not Providing Fallback

```python
# BAD: Fail hard if LLM uses wrong verb
if not validate_verb(obj.verb, obj.level):
    raise ValueError(f"Invalid verb: {obj.verb}")

# GOOD: Fallback to approved verb
if not validate_verb(obj.verb, obj.level):
    obj.verb = BloomsTaxonomy.get_random_verb(obj.level)
    logger.warning(f"Replaced invalid verb with: {obj.verb}")
```

---

## Testing Your Implementation

### Unit Tests for Verb Validation

```python
# tests/unit/test_blooms_taxonomy.py

import pytest
from src.core.models import BloomsTaxonomy, BloomLevel

class TestBloomsTaxonomy:
    def test_all_remember_verbs_valid(self):
        """All verbs in Remember list should pass validation."""
        for verb in BloomsTaxonomy.VERBS["Remember"]:
            assert BloomsTaxonomy.validate_verb(verb, "Remember")

    def test_cross_level_verbs_fail(self):
        """Verbs from one level should NOT work for another."""
        # "create" is CREATE level, not REMEMBER
        assert not BloomsTaxonomy.validate_verb("create", "Remember")

    def test_case_insensitive(self):
        """Verb matching should be case-insensitive."""
        assert BloomsTaxonomy.validate_verb("DEFINE", "Remember")
        assert BloomsTaxonomy.validate_verb("Define", "Remember")
        assert BloomsTaxonomy.validate_verb("define", "Remember")

    def test_invalid_verb_fails(self):
        """Made-up verb should fail validation."""
        assert not BloomsTaxonomy.validate_verb("foobar", "Apply")

    def test_get_random_verb(self):
        """Random verb should be valid for its level."""
        for level in ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]:
            verb = BloomsTaxonomy.get_random_verb(level)
            assert BloomsTaxonomy.validate_verb(verb, level)
```

---

## Appendix: Quick Reference

### Verb Count by Level

| Level | Verb Count | Notes |
|-------|-----------|-------|
| Remember | 30 | Basic recall verbs |
| Understand | 30 | Comprehension verbs |
| Apply | 30 | Implementation verbs |
| Analyze | 30 | Analysis verbs |
| Evaluate | 30 | Judgment verbs |
| Create | 30 | Creative verbs |
| **TOTAL** | **180** | Curated verb database |

### Most Common Verbs (Top 10)

1. **define** (Remember)
2. **explain** (Understand)
3. **apply** (Apply)
4. **analyze** (Analyze)
5. **evaluate** (Evaluate)
6. **create** (Create)
7. **use** (Apply)
8. **compare** (Understand/Analyze)
9. **design** (Create)
10. **describe** (Understand)

---

## Next Steps

1. **Copy the complete verb lists** into `src/core/models.py`
2. **Implement validation logic** as specified
3. **Write unit tests** for all 180 verbs
4. **Add DSPy assertions** to enforce verb compliance
5. **Test with real LLM outputs** and adjust as needed

Remember: **Strict verb validation is critical for educational quality**. Do not skip or weaken this requirement without explicit approval from the technical lead.
