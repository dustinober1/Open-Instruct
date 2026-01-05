# Frequently Asked Questions (FAQ)

## General Project

**Q: Can I use this for a real production app?**
A: Yes, but you should upgrade from SQLite to PostgreSQL and likely use OpenAI/Anthropic instead of local models for reliability.

**Q: Why Python and not JavaScript/Node?**
A: Python is the native language of AI. Libraries like DSPy and Pydantic provide much better tooling for LLM orchestration than their JS counterparts (currently).

## Technical

**Q: My "Hello World" test keeps failing JSON validation!**
A: This is common with small 1.5B models.
1.  Try running it again (sometimes it's just bad luck).
2.  Add more "few-shot" examples to your DSPy signature.
3.  Switch to `gpt-4o-mini` to see if it's a model issue or a code issue.

**Q: Can I use Llama 3 instead of DeepSeek?**
A: Yes!
1.  Run `ollama pull llama3`.
2.  Update `src/core/config.py` or your `.env` file to use `llama3`.

**Q: Where is the frontend?**
A: We build the backend *first*. The frontend is Phase 4. We do this to ensure our API is solid before we worry about pixels.

## Process

**Q: Do I have to use TDD?**
A: For this project, yes. It is a learning requirement. Writing the test first forces you to think about the *interface* of your code before the *implementation*.

**Q: How do I share my course with others?**
A: Phase 5 covers "Export to JSON". You can send that JSON file to a friend, and they can import it into their instance.
