# Autonomous Research Agent

This project is a production-grade **Autonomous Research Agent** built with
**LangGraph**, **Groq** (Llama 3.3), and **Tavily Search API**. Given a research
topic, it autonomously plans sub-questions, searches the web, reads relevant
pages, and produces a structured markdown research report.

## Tech Stack

- Language: Python 3.10+
- Agent Framework: LangGraph
- LLM: Groq `llama-3.3-70b-versatile` via `langchain-groq`
- Web Search: Tavily (`tavily-python`)
- Web Reader: Jina Reader (`https://r.jina.ai/{url}`)
- Env Management: `python-dotenv`

## Setup

1. **Create and activate a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS / Linux
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file in the project root** with:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

   Get a Groq API key at [console.groq.com](https://console.groq.com) (keys start with `gsk_`).

## Usage

Run the agent from the project root (with the virtual environment activated):

```bash
python agent.py
```

You will be prompted:

```text
Enter research topic: The impact of AI on the job market
```

The agent will:

- Plan 3–5 sub-questions with Groq.
- Search the web for each sub-question using Tavily.
- Read the top URLs with Jina Reader.
- Synthesize a final markdown report with Groq.

When finished, it saves a report to the `outputs/` folder, e.g.:

```text
outputs/report_the_impact_of_ai_on_the_job_market.md
```

## Notes

- All external API calls are wrapped in basic error handling.
- Progress is logged from each node so you can see the agent working.
- The project uses **LangGraph** directly (no LangChain `AgentExecutor`).
- Search uses a **2 second** delay between Tavily calls to reduce pressure on downstream steps and align with typical Groq free-tier usage patterns.
