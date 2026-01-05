# OpenAI API Setup Guide

This guide describes how to configure the Open-Instruct engine to use OpenAI's models (e.g., GPT-4o, GPT-3.5-Turbo) instead of the local Ollama models.

## Why Use OpenAI?
- **High Reliability**: Extremely consistent JSON output.
- **Speed**: Faster than local CPU inference for large batches.
- **Knowledge**: Broader general knowledge base.

## Prerequisites
- A credit card (OpenAI API is a paid service).
- An OpenAI account.

## Step-by-Step Setup

### 1. Get Your API Key
1.  Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
2.  Click **"Create new secret key"**.
3.  Name it `open-instruct-key` (or similar).
4.  **COPY IT IMMEDIATELY**. You won't see it again.

### 2. Configure Environment
Create or edit your `.env` file in the `backend/` directory:

```bash
# backend/.env
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-..."  # Paste your key here
OPENAI_MODEL_NAME="gpt-4o-mini" # Recommended for cost/performance
```

### 3. Verify Connection
We will use a simple script to test the connection.

```bash
# From backend/ directory
python src/scripts/test_provider.py --provider openai
```

*(Note: If this script doesn't exist yet, you can test by running the main module and checking logs).*

## Cost Management
- **GPT-4o-mini**: Very cheap (~$0.15 / 1M input tokens). Great for development.
- **GPT-4o**: Expensive (~$5.00 / 1M input tokens). Use only for final production if needed.
- **Set Limits**: Go to [Billing Limits](https://platform.openai.com/account/billing/limits) and set a hard cap (e.g., $10) to avoid surprises.

## Troubleshooting
- **Error 401 (Unauthorized)**: Your API key is wrong. Re-copy it.
- **Error 429 (Rate Limit)**: You ran out of credits. Check your billing status.
