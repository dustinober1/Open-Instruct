# Anthropic API Setup Guide

This guide describes how to configure the Open-Instruct engine to use Anthropic's Claude models.

## Why Use Anthropic?
- **Safety**: Designed with "Constitutional AI" to be helpful and harmless.
- **Context Window**: Excellent at handling large amounts of context.
- **Reasoning**: Claude 3.5 Sonnet is exceptional at logic and coding tasks.

## Prerequisites
- A credit card (Anthropic API is a paid service).
- An Anthropic Console account.

## Step-by-Step Setup

### 1. Get Your API Key
1.  Go to [console.anthropic.com](https://console.anthropic.com/).
2.  Click **"Get API Keys"**.
3.  Click **"Create Key"**.
4.  Name it `open-instruct-claude`.
5.  **COPY IT IMMEDIATELY**.

### 2. Configure Environment
Edit your `.env` file in the `backend/` directory:

```bash
# backend/.env
LLM_PROVIDER="anthropic"
ANTHROPIC_API_KEY="sk-ant-..."  # Paste your key here
ANTHROPIC_MODEL_NAME="claude-3-haiku-20240307" # Fast & cheap
# OR for better quality:
# ANTHROPIC_MODEL_NAME="claude-3-5-sonnet-20240620"
```

### 3. Verify Connection
Run the provider test:

```bash
# From backend/ directory
python src/scripts/test_provider.py --provider anthropic
```

*(Note: If this script doesn't exist yet, you can test by running the main module and checking logs).*

## Cost Expectations
- **Claude 3 Haiku**: Very affordable, similar to GPT-4o-mini.
- **Claude 3.5 Sonnet**: Moderate cost, best balance of intelligence.
- **Claude 3 Opus**: Expensive, overkill for this project.

## Troubleshooting
- **"Credit Balance is 0"**: You must add $5 minimum credit to start using the API, even for the free tier sometimes.
- **Timeout**: The API might be slow. Increase timeout settings in `src/core/config.py`.
