# Glossary

Terms and acronyms used in the Open-Instruct project.

## A-M

### **Bloom's Taxonomy**
A hierarchical framework for categorizing educational goals. It organizes learning objectives into levels of complexity: Remember, Understand, Apply, Analyze, Evaluate, and Create.

### **DSPy**
(Declarative Self-Improving Language Programs). A framework from Stanford that treats using LLMs like writing code rather than prompting. It optimizes "prompts" automatically.

### **Distractor**
An incorrect option in a multiple-choice question. Good distractors are plausible but clearly wrong to someone who knows the material.

### **Endpoint**
A specific URL in our API (e.g., `/generate/quiz`) that performs a specific function.

### **FastAPI**
A modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.

### **Hallucination**
When an LLM generates false or non-existent information confidently. In our context, this often means generating JSON with made-up fields or invalid verbs.

### **LLM**
(Large Language Model). The AI "brain" behind our text generation (e.g., GPT-4, Llama 3).

## N-Z

### **Ollama**
A tool that allows you to run open-source LLMs locally on your machine.

### **Pydantic**
A data validation library for Python. We use it to ensure the JSON coming from the AI matches the exact shape we expect.

### **Stem**
The main text of a multiple-choice question (the actual question part).

### **TDD**
(Test-Driven Development). A software development process where you write the test *before* you write the code. Red -> Green -> Refactor.

### **TypedPredictor**
A specific module in DSPy that enforces strict output signatures (schemas) for LLM responses.
