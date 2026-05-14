# 🔄 Switch LLM: Google Gemini → Groq API

Please update the project to replace **Google Gemini** with **Groq** as the
LLM provider. Apply all changes listed below across the relevant files.
Do NOT change the LangGraph architecture, tools.py, or prompts.py content.

---

## ⚠️ API Key Setup (Do This First)

### 1. Get Your Free Groq API Key
- Go to [console.groq.com](https://console.groq.com)
- Sign up / Log in
- Click **"API Keys"** in the left sidebar
- Click **"Create API Key"**
- Copy the key (starts with `gsk_`)

### 2. Update Your `.env` File
Open `.env` and replace the old Gemini key with the Groq key:

```env
# ❌ Remove this line:
GOOGLE_API_KEY=your_google_gemini_api_key_here

# ✅ Add this line instead:
GROQ_API_KEY=your_groq_api_key_here

# ✅ Keep this line as-is:
TAVILY_API_KEY=your_tavily_api_key_here
```

> ⛔ Never hardcode the API key in any `.py` file. Always load from `.env`.

---

## 📦 Step 1 — Install Groq LangChain Package

Run this in the terminal (with `.venv` activated):

```bash
pip install langchain-groq
```

Then update `requirements.txt` — replace:
```txt
# ❌ Remove:
langchain-google-genai

# ✅ Add:
langchain-groq
```

---

## 📄 Step 2 — Update `agent.py`

### 2a — Replace the Import
```python
# ❌ Remove:
from langchain_google_genai import ChatGoogleGenerativeAI

# ✅ Add:
from langchain_groq import ChatGroq
```

### 2b — Replace the LLM Singleton Function
Replace the entire `_get_llm()` function with this:

```python
_llm: ChatGroq | None = None


def _get_llm() -> ChatGroq:
    """
    Construct a Groq chat model client using the GROQ_API_KEY env variable.
    Client is created once and reused (singleton pattern).

    Raises:
        RuntimeError: If the API key is missing.
    """
    global _llm
    if _llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. "
                "Get your free key at https://console.groq.com and add it to .env"
            )
        _llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0,
            max_tokens=4096,
        )
    return _llm
```

### 2c — Update the Type Hint on `_llm`
```python
# ❌ Old:
_llm: ChatGoogleGenerativeAI | None = None

# ✅ New:
_llm: ChatGroq | None = None
```

---

## 📄 Step 3 — Update `prompts.py`

No structural changes needed. However, add this note at the top of the file
as a comment so future developers know which model is in use:

```python
# LLM: Groq — llama-3.3-70b-versatile
# Planner expects JSON-only output. Writer expects markdown report output.
```

---

## 📄 Step 4 — Update `agent.py` — Add Groq Rate Limit Protection

Groq free tier has a **rate limit of 30 requests/minute**. Add a slightly
longer sleep between search iterations to avoid hitting it during the
search node.

In `search_node()`, update the sleep at the bottom of the loop:

```python
# ❌ Old:
time.sleep(1)

# ✅ New:
time.sleep(2)  # Groq free tier: 30 req/min — extra buffer
```

---

## 📄 Step 5 — Update `.gitignore`

Make sure `.gitignore` includes the Groq key pattern. Add this line if not
already present:

```
.env
.venv/
venv/
outputs/
__pycache__/
*.pyc
```

---

## ✅ Verification Checklist

After applying all changes, verify:

- [ ] `GROQ_API_KEY` is set in `.env` with your real key starting with `gsk_`
- [ ] `GOOGLE_API_KEY` line is removed from `.env`
- [ ] `langchain-groq` is installed (`pip show langchain-groq`)
- [ ] `langchain-google-genai` import is removed from `agent.py`
- [ ] `ChatGroq` is imported in `agent.py`
- [ ] `_get_llm()` uses `ChatGroq` with model `llama-3.3-70b-versatile`
- [ ] `temperature=0` and `max_tokens=4096` are set
- [ ] `time.sleep(2)` is used in `search_node()`
- [ ] `requirements.txt` has `langchain-groq` instead of `langchain-google-genai`

---

## 🚀 Step 6 — Run the Agent

Once all changes are applied, run:

```bash
python agent.py
```

Expected output:
```
Enter research topic: The impact of AI on the job market
2024-xx-xx [INFO] Planner: Breaking topic into sub-questions...
2024-xx-xx [INFO] Search: Searching 4 sub-questions...
2024-xx-xx [INFO] Search: Searching: ...
2024-xx-xx [INFO] Reader: Reading content from top URLs...
2024-xx-xx [INFO] Writer: Generating final report...
Report saved to: outputs/report_the_impact_of_ai_on_the_job_market.md
```

---

## 🛑 Common Groq Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `GROQ_API_KEY is not set` | Missing key in `.env` | Add `GROQ_API_KEY=gsk_...` to `.env` |
| `AuthenticationError` | Wrong or expired key | Generate a new key at console.groq.com |
| `RateLimitError` | Too many requests | Increase `time.sleep(2)` to `time.sleep(3)` |
| `ModuleNotFoundError: langchain_groq` | Package not installed | Run `pip install langchain-groq` |
| `model not found` | Wrong model name | Use exactly `llama-3.3-70b-versatile` |

---

## 🚫 Do NOT Change

- `tools.py` — no LLM is used there, no changes needed
- `prompts.py` — prompts work with any LLM, no changes needed
- LangGraph graph structure in `agent.py`
- `AgentState` TypedDict
- Jina Reader or Tavily logic
