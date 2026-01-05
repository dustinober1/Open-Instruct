# Troubleshooting Guide

This document covers common issues you might encounter while building Open-Instruct.

## Top 3 Issues

### 1. "Connection Refused" (Ollama)
**Symptom**: `httpx.ConnectError: [Errno 61] Connection refused`
**Cause**: Ollama is not running in the background.
**Fix**:
1.  Open a new terminal window.
2.  Run `ollama serve`.
3.  Keep that window open!

### 2. "Model not found"
**Symptom**: `dspy.dsp.modules.lm.OllamaError: model 'deepseek-r1:1.5b' not found`
**Cause**: You haven't pulled the specific model yet.
**Fix**:
Run `ollama pull deepseek-r1:1.5b`

### 3. "JSONDecodeError"
**Symptom**: `pydantic.ValidationError` or `json.decoder.JSONDecodeError`
**Cause**: The LLM outputted text like "Here is your JSON:" instead of just the JSON.
**Fix**:
-   **Immediate**: Retry the command. It might work the second time.
-   **Permenant**: Switch to a more powerful model (e.g., OpenAI) or check `DSPy_Prompt_Strategy.md` to improve your prompt assertions.

---

## Environment Issues

### Python "Module Not Found"
**Error**: `ModuleNotFoundError: No module named 'src'`
**Fix**: You are likely running python from the wrong directory.
-   **Wrong**: `python src/main.py` (while inside `src/`)
-   **Correct**: `python -m src.modules.architect` (while inside `backend/`)
-   Always run commands from the project root or `backend/` root as specified in the docs.

### Virtual Environment (venv) Not Activating
**Symptom**: `pip install` installs to the global python, not your project.
**Fix**:
-   Mac/Linux: `source venv/bin/activate` (Prompt should show `(venv)`)
-   Windows: `venv\Scripts\activate`

---

## "It's too slow!"
**Symptom**: Generating one objective takes 60 seconds.
**Cause**: You are running a large model on a CPU.
**Fixes**:
1.  **Switch Model**: Use `deepseek-r1:1.5b` (Smallest) instead of Llama3 (8B).
2.  **Use Cloud**: Switch to OpenAI (`gpt-4o-mini`) which is instant.
3.  **Close Chrome Tabs**: Free up RAM for Ollama.
