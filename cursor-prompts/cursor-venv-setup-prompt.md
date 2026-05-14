# ⚙️ Environment Setup & Auto-Run: Autonomous Research Agent

Please perform the following steps **in order**, using the terminal inside
Cursor. Execute each command and wait for it to complete before moving to
the next step.

---

## 🔐 Step 0 — Confirm API Keys Exist

Before doing anything, check that the `.env` file exists in the project root
and contains both keys. If it does not exist, create it with this content:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

> ⚠️ Remind the user:
> - Replace `your_google_gemini_api_key_here` with the real key from [aistudio.google.com](https://aistudio.google.com)
> - Replace `your_tavily_api_key_here` with the real key from [tavily.com](https://tavily.com)
> - The Tavily key starts with `tvly-`

---

## 🐍 Step 1 — Create the Virtual Environment

Run this command in the terminal to create a `.venv` folder in the project root:

```bash
python -m venv .venv
```

> ✅ Expected result: A `.venv/` folder appears in the project root containing
> `Scripts/` (Windows) or `bin/` (Mac/Linux).

If `python` is not found, try:
```bash
python3 -m venv .venv
```

---

## ⚡ Step 2 — Activate the Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac / Linux:**
```bash
source .venv/bin/activate
```

> ✅ Expected result: The terminal prompt now starts with `(.venv)`.

---

## 📦 Step 3 — Create `requirements.txt`

Create a `requirements.txt` file in the project root with this exact content:

```txt
langgraph
langchain
langchain-google-genai
tavily-python
python-dotenv
requests
```

---

## 📥 Step 4 — Install All Dependencies

Run this command to install everything from `requirements.txt`:

```bash
pip install -r requirements.txt
```

> ✅ Expected result: All packages install without errors.
> If you see any red errors, run `pip install --upgrade pip` first, then retry.

---

## 🔍 Step 5 — Verify Installation

Run this to confirm all key packages installed correctly:

```bash
python -c "import langgraph; import langchain; import langchain_google_genai; import tavily; import dotenv; import requests; print('All packages OK')"
```

> ✅ Expected result: `All packages OK` printed in terminal.
> ❌ If any import fails, run `pip install <package-name>` for the missing one.

---

## 🚀 Step 6 — Run the Agent

Once all packages are confirmed, run the agent:

```bash
python agent.py
```

> ✅ Expected result: You will see this prompt in the terminal:
> ```
> Enter research topic:
> ```
> Type any research topic and press Enter, for example:
> ```
> The impact of AI on the job market
> ```

The agent will then:
1. `[Planner]` — Break the topic into sub-questions
2. `[Search]` — Search the web for each sub-question
3. `[Reader]` — Read top URLs for each result
4. `[Writer]` — Generate the final markdown report

When finished, the report will be saved to:
```
outputs/report_<your_topic>.md
```

---

## 🛑 Common Errors & Fixes

| Error | Fix |
|---|---|
| `GOOGLE_API_KEY is not set` | Open `.env` and add your Gemini API key |
| `TAVILY_API_KEY is not set` | Open `.env` and add your Tavily API key |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `python not found` | Use `python3` instead of `python` |
| `.venv not activating` | Make sure you are in the project root folder |
| `pip not found` | Run `python -m pip install -r requirements.txt` |

---

## 📁 Final Project Structure

After completing all steps, the project should look like this:

```
autonomous-research-agent/
│
├── .venv/                  ✅ Created by Step 1
├── .env                    ✅ Contains both API keys
├── requirements.txt        ✅ Created by Step 3
│
├── tools.py                ✅ Web search + URL reader
├── prompts.py              ✅ LLM prompts
├── agent.py                ✅ LangGraph agent
│
├── outputs/                ✅ Auto-created at runtime
│   └── report_<topic>.md
│
├── .gitignore              ✅ Ignores .venv, .env, outputs/
└── README.md               ✅ Project documentation
```

---

## 🚫 Do NOT

- Do not commit `.env` to Git — it contains secret API keys
- Do not commit `.venv/` to Git — it is too large and machine-specific
- Do not run `agent.py` without activating `.venv` first
- Do not skip Step 5 verification — it catches missing packages early
