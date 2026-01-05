# LLM Provider Comparison

Choosing the right "brain" for your Open-Instruct engine is critical. Here is a breakdown of the three supported options.

## At a Glance

| Feature | **Ollama (DeepSeek)** | **OpenAI (GPT-4o)** | **Anthropic (Claude)** |
| :--- | :--- | :--- | :--- |
| **Cost** | 🆓 **Free** | 💰 Paid (Usage based) | 💰 Paid (Usage based) |
| **Privacy** | 🔒 **100% Private** | ☁️ Cloud (Data sent to OpenAI) | ☁️ Cloud (Data sent to Anthropic) |
| **Setup** | 🛠️ Complex (Install app) | ⚡ Easy (API Key) | ⚡ Easy (API Key) |
| **Offline** | ✅ Yes | ❌ No | ❌ No |
| **JSON Quality** | ⭐ Fair (Requires retries) | ⭐⭐⭐ Excellent | ⭐⭐⭐ Very Good |
| **Speed** | 🐢 Depends on your hardware | 🐇 Fast | 🐇 Fast |

---

## Detailed Breakdown

### 1. Ollama (DeepSeek-R1 1.5B / Llama 3)
*The default for this project.*

*   **Best For**: Learning, offline development, zero cost.
*   **The Catch**: 
    *   It runs on *your* computer. If you have an old laptop, it will be slow.
    *   Smaller models (1.5B) struggle to follow strict JSON formatting sometimes. You will see more "Retry" logs.
*   **Recommendation**: Start here. If your computer struggles, switch to OpenAI.

### 2. OpenAI (GPT-4o-mini)
*The industry standard.*

*   **Best For**: Getting things working quickly.
*   **The Catch**:
    *   You need to put in a credit card.
    *   Costs money (though "mini" models are very cheap, likely <$1/month for this course).
*   **Recommendation**: Use this if you get frustrated with Ollama's local performance or JSON errors.

### 3. Anthropic (Claude 3.5 Sonnet)
*The smart alternative.*

*   **Best For**: Complex reasoning. If you want the engine to generate really *good* quizzes, Claude often writes better questions than GPT.
*   **The Catch**:
    *   Slightly more strict safety filters.
*   **Recommendation**: Good for the "Assessor" module (Quiz generation) if you want high-quality distractors.

## How to Switch
You don't need to change code! Just change your `.env` file:

**To use OpenAI:**
```bash
LLM_PROVIDER="openai"
OPENAI_API_KEY="..."
```

**To use Ollama:**
```bash
LLM_PROVIDER="ollama"
# No API key needed
OLLAMA_MODEL="deepseek-r1:1.5b"
```
