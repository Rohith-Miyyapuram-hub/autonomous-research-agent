# 🤖 Autonomous Research Agent — Cursor AI Project Prompt

## 🎯 Project Overview

Build a **production-grade Autonomous Research Agent** using **LangGraph**, **Google Gemini**, and **Tavily Search API**. The agent accepts a research topic from the user, autonomously breaks it into sub-questions, searches the web, reads and extracts relevant information, and produces a structured markdown research report — with zero manual intervention.

This project is designed to demonstrate **Agentic AI** skills for a professional portfolio.

---

## 🧰 Tech Stack

| Component         | Technology                        |
|------------------|-----------------------------------|
| Language          | Python 3.10+                      |
| Agent Framework   | LangGraph                         |
| LLM               | Google Gemini (`gemini-1.5-flash`) via `langchain-google-genai` |
| Web Search        | Tavily API (`tavily-python`)       |
| Web Content Read  | Jina Reader (free, no key needed) |
| Env Management    | `python-dotenv`                   |
| Output Format     | Markdown Report (`.md` file)       |

---

## 📁 Project File Structure

```
autonomous-research-agent/
│
├── venv/                   # Virtual environment (do not modify)
├── .env                    # API keys (GOOGLE_API_KEY, TAVILY_API_KEY)
├── .gitignore              # Ignore .env and venv
│
├── tools.py                # Search and web reading tools
├── prompts.py              # All LLM system and task prompts
├── agent.py                # LangGraph agent graph definition and runner
│
├── outputs/                # Folder where generated reports are saved
│   └── report_<topic>.md
│
└── README.md               # Project documentation
```

---

## 🔐 Environment Variables

The `.env` file contains:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Load them using `python-dotenv` at the top of every file that needs them.

---

## 🏗️ Agent Architecture

The agent is built as a **LangGraph StateGraph** with the following nodes:

```
User Input (research topic)
        ↓
┌───────────────────┐
│   planner_node    │  → Uses Gemini to break topic into 3–5 sub-questions
└───────────────────┘
        ↓
┌───────────────────┐
│   search_node     │  → Uses Tavily to search each sub-question
└───────────────────┘
        ↓
┌───────────────────┐
│   reader_node     │  → Uses Jina Reader to extract full content from top URLs
└───────────────────┘
        ↓
┌───────────────────┐
│   writer_node     │  → Uses Gemini to synthesize all content into a report
└───────────────────┘
        ↓
  Final Markdown Report (saved to /outputs/)
```

---

## 📄 File-by-File Implementation Plan

### 1. `tools.py`
Define two tool functions:

- **`search_web(query: str) -> list`**
  - Uses `TavilyClient` to search the web
  - Returns top 5 results with `title`, `url`, `content`

- **`read_url(url: str) -> str`**
  - Uses Jina Reader (`https://r.jina.ai/{url}`) via `requests.get()`
  - Returns clean markdown text of the page
  - Add a timeout of 10 seconds and error handling

---

### 2. `prompts.py`
Define all prompts as Python string constants:

- **`PLANNER_PROMPT`** — instructs Gemini to decompose a research topic into 3–5 focused sub-questions as a JSON list
- **`WRITER_PROMPT`** — instructs Gemini to synthesize all gathered content into a well-structured markdown report with sections: Executive Summary, Key Findings, Detailed Analysis, Conclusion, and Sources

---

### 3. `agent.py`
This is the main file. It must:

**Define the AgentState TypedDict:**
```python
class AgentState(TypedDict):
    topic: str
    sub_questions: list[str]
    search_results: list[dict]
    extracted_content: list[str]
    final_report: str
```

**Define 4 node functions:**

- `planner_node(state)` — calls Gemini with `PLANNER_PROMPT` + topic, parses JSON output into `sub_questions`
- `search_node(state)` — loops through `sub_questions`, calls `search_web()` for each, stores all results in `search_results`
- `reader_node(state)` — takes top 2 URLs from each search result, calls `read_url()`, stores content in `extracted_content`
- `writer_node(state)` — passes all `extracted_content` + `topic` to Gemini with `WRITER_PROMPT`, stores result in `final_report`

**Build the LangGraph:**
```python
graph = StateGraph(AgentState)
graph.add_node("planner", planner_node)
graph.add_node("search", search_node)
graph.add_node("reader", reader_node)
graph.add_node("writer", writer_node)

graph.set_entry_point("planner")
graph.add_edge("planner", "search")
graph.add_edge("search", "reader")
graph.add_edge("reader", "writer")
graph.add_edge("writer", END)

app = graph.compile()
```

**Add a `main()` runner:**
- Accepts topic via `input()` from the user
- Runs the graph with `app.invoke({"topic": topic})`
- Saves `final_report` as a `.md` file in `/outputs/`
- Prints a success message with the output file path

---

## ⚙️ Coding Standards & Rules

- Use **type hints** on all functions
- Add **docstrings** to every function
- Wrap all API calls in **try/except** blocks with meaningful error messages
- Use **f-strings** for string formatting
- Use `json.loads()` safely to parse LLM JSON output — wrap in try/except
- Print **progress logs** at each node so the user can see the agent working:
  - `[Planner] Breaking topic into sub-questions...`
  - `[Search] Searching: {question}`
  - `[Reader] Reading: {url}`
  - `[Writer] Generating final report...`
- Save reports to `outputs/` folder — create it if it doesn't exist using `os.makedirs()`

---

## 📦 Required Libraries

```bash
pip install langgraph langchain langchain-google-genai tavily-python python-dotenv requests
```

---

## ✅ Expected Output

When the user runs:
```bash
python agent.py
```

They are prompted:
```
Enter research topic: The impact of AI on the job market
```

The agent runs through all 4 nodes with progress logs, then saves:
```
outputs/report_the_impact_of_ai_on_the_job_market.md
```

The report includes:
- Executive Summary
- Key Findings (bullet points)
- Detailed Analysis (multiple sections)
- Conclusion
- Sources (list of URLs used)

---

## 🚫 Do NOT

- Do not use `AgentExecutor` from LangChain — use **LangGraph only**
- Do not hardcode API keys — always load from `.env`
- Do not skip error handling on API calls
- Do not ignore rate limits — add `time.sleep(1)` between Tavily searches
- Do not use deprecated LangChain APIs

---

## 🏁 Execution Order

Please implement the files in this order:
1. `.gitignore`
2. `tools.py`
3. `prompts.py`
4. `agent.py`
5. `README.md`

Start by showing the complete implementation of `tools.py` first, then proceed file by file.
