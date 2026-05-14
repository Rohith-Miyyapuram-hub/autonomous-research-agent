# 🔧 Fix & Improve: Autonomous Research Agent

Please apply the following fixes and improvements across `tools.py`,
`prompts.py`, and `agent.py`. Do not change the overall architecture or
file structure — only apply the changes listed below.

---

## ⚠️ API Keys Setup (Do This First)

Before running the project, make sure the `.env` file in the project root
contains both API keys:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

> 🔑 **Where to get them:**
> - **Google Gemini API Key** → [Google AI Studio](https://aistudio.google.com) → Sign in → "Get API Key"
> - **Tavily API Key** → [Tavily Dashboard](https://tavily.com) → Sign in → Dashboard → Copy the key starting with `tvly-`

> ⛔ **Never hardcode API keys in any `.py` file. Always load from `.env` only.**

---

## 📄 Fixes for `tools.py`

### Fix 1 — Tavily Client Singleton
Replace `_get_tavily_client()` so it creates the client only once and reuses
it on every call instead of instantiating a new object per search.

```python
_tavily_client: TavilyClient | None = None

def _get_tavily_client() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError("TAVILY_API_KEY is not set in the environment.")
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client
```

### Fix 2 — Retry Logic on `search_web()`
Wrap the Tavily call in exponential-backoff retry logic (max 3 attempts).

```python
def search_web(query: str, retries: int = 3) -> List[Dict[str, Any]]:
    for attempt in range(retries):
        try:
            # ... existing search logic ...
            return results
        except Exception as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"Tavily search failed after {retries} attempts: {exc}") from exc
            time.sleep(2 ** attempt)
```

### Fix 3 — Add User-Agent Header to `read_url()`
Add a `User-Agent` header so websites don't block the Jina Reader request.

```python
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}

response = requests.get(jina_endpoint, timeout=10, headers=HEADERS)
```

### Fix 4 — Truncate Content in `read_url()`
Cap the returned content to 2000 characters to prevent context window overflow.

```python
MAX_CONTENT_CHARS = 2000

# At the end of read_url(), before returning:
return text[:MAX_CONTENT_CHARS]
```

---

## 📄 Fixes for `agent.py`

### Fix 5 — Fix All Broken Regex Patterns
Replace all incorrect escaped regex patterns with correct ones:

```python
# In planner_node — JSON extraction fallback
# ❌ WRONG:  r"\\[.*\\]"
# ✅ CORRECT:
match = re.search(r"\[.*\]", raw_text, re.DOTALL)

# In _sanitize_topic_for_filename
# ❌ WRONG:  r"\\s+"  and  r"[^a-z0-9_\\-]"
# ✅ CORRECT:
slug = re.sub(r"\s+", "_", slug)
slug = re.sub(r"[^a-z0-9_\-]", "", slug)
```

### Fix 6 — Move LLM Client to Module Level
Remove `_get_llm()` calls from inside node functions. Instead, initialise
the LLM once at module level and import it into each node.

```python
# At module level, after load_dotenv()
_llm: ChatGoogleGenerativeAI | None = None

def _get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set in the environment.")
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=api_key,
            temperature=0,        # deterministic output for JSON
        )
    return _llm
```

### Fix 7 — Set Temperature to 0
In `_get_llm()`, change `temperature=0.3` to `temperature=0` for
deterministic, reliable JSON output from the planner.

### Fix 8 — Add Sub-Question Count Validation in `planner_node`
After parsing the JSON response, add guards for minimum and maximum count.

```python
sub_questions = sub_questions[:5]  # cap at 5

if len(sub_questions) < 1:
    raise RuntimeError("Planner returned no sub-questions. Try rephrasing the topic.")
```

### Fix 9 — Replace All `print()` with `logging`
Replace every `print()` statement across the file with Python's `logging`
module. Add this setup at the top of `agent.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
```

Replace all `print(...)` with `logger.info(...)` or `logger.warning(...)`
for errors throughout the file.

### Fix 10 — Add Metadata Header to Saved Report
Before writing the report to disk, prepend a YAML front-matter metadata block.

```python
from datetime import datetime

metadata = (
    f"---\n"
    f"topic: {topic}\n"
    f"generated: {datetime.now().isoformat()}\n"
    f"---\n\n"
)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(metadata + report)
```

---

## 📄 Fix for `prompts.py`

### Fix 11 — Update `WRITER_PROMPT` to Request Inline Source Citations
Add this instruction inside `WRITER_PROMPT` under the Sources section:

```
Where possible, reference the source URL inline using markdown links
so readers can trace each claim back to its origin.
```

---

## ✅ Summary Checklist

After applying all fixes, verify the following:

- [ ] `.env` file exists with both `GOOGLE_API_KEY` and `TAVILY_API_KEY` filled in
- [ ] Tavily client is a singleton (not recreated per call)
- [ ] `search_web()` has retry logic with exponential backoff
- [ ] `read_url()` sends a `User-Agent` header
- [ ] `read_url()` truncates content to 2000 characters
- [ ] All regex patterns use single backslash (`\s`, `\[`, not `\\s`, `\\[`)
- [ ] LLM client is a singleton at module level
- [ ] LLM temperature is set to `0`
- [ ] Sub-questions are capped at 5 and validated to be at least 1
- [ ] All `print()` replaced with `logger.info()` / `logger.warning()`
- [ ] Saved report includes YAML metadata header with topic and timestamp
- [ ] `WRITER_PROMPT` includes inline source citation instruction

---

## 🚫 Do NOT Change

- The LangGraph graph structure (nodes and edges stay the same)
- The `AgentState` TypedDict fields
- The overall file structure and names
- The Jina Reader endpoint format (`https://r.jina.ai/{url}`)
