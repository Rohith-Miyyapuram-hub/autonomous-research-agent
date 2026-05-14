"""
Main LangGraph-based autonomous research agent.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from prompts import PLANNER_PROMPT, WRITER_PROMPT
from tools import read_url, search_web


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

_llm: ChatGroq | None = None


class AgentState(TypedDict):
    """State container for the research agent."""

    topic: str
    sub_questions: List[str]
    search_results: List[Dict[str, Any]]
    extracted_content: List[str]
    final_report: str


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


def planner_node(state: AgentState) -> AgentState:
    """
    Planner node: decompose the topic into focused sub-questions using Groq.
    """
    topic = state["topic"]
    logger.info("[Planner] Breaking topic into sub-questions...")

    llm = _get_llm()
    prompt = f"{PLANNER_PROMPT}\n\nUser topic:\n{topic}"

    try:
        response = llm.invoke(prompt)
        raw_text = response.content if hasattr(response, "content") else str(response)
        try:
            sub_questions: List[str] = json.loads(raw_text)
        except json.JSONDecodeError:
            # Try to extract JSON substring if model wrapped it
            match = re.search(r"\[.*\]", raw_text, re.DOTALL)
            if not match:
                raise
            sub_questions = json.loads(match.group(0))

        if not isinstance(sub_questions, list) or not all(isinstance(q, str) for q in sub_questions):
            raise ValueError("Planner output is not a list of strings.")

        sub_questions = sub_questions[:5]
        if len(sub_questions) < 1:
            raise RuntimeError("Planner returned no sub-questions. Try rephrasing the topic.")

        new_state: AgentState = {
            **state,
            "sub_questions": sub_questions,
        }
        return new_state
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Planner node failed for topic '{topic}': {exc}") from exc


def search_node(state: AgentState) -> AgentState:
    """
    Search node: perform Tavily web search for each sub-question.
    """
    sub_questions = state.get("sub_questions", [])
    logger.info("[Search] Searching %s sub-questions...", len(sub_questions))

    all_results: List[Dict[str, Any]] = []
    for question in sub_questions:
        logger.info("[Search] Searching: %s", question)
        try:
            results = search_web(question)
            all_results.append({"question": question, "results": results})
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("[Search] Error searching '%s': %s", question, exc)
        time.sleep(2)  # Groq free tier: 30 req/min — extra buffer

    new_state: AgentState = {
        **state,
        "search_results": all_results,
    }
    return new_state


def reader_node(state: AgentState) -> AgentState:
    """
    Reader node: use Jina Reader to fetch full content for top URLs.
    """
    logger.info("[Reader] Reading content from top URLs...")
    search_results = state.get("search_results", [])
    extracted: List[str] = []

    for entry in search_results:
        results = entry.get("results", [])[:2]
        for res in results:
            url = res.get("url")
            if not url:
                continue
            logger.info("[Reader] Reading: %s", url)
            try:
                content = read_url(url)
                extracted.append(content)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("[Reader] Error reading '%s': %s", url, exc)

    new_state: AgentState = {
        **state,
        "extracted_content": extracted,
    }
    return new_state


def writer_node(state: AgentState) -> AgentState:
    """
    Writer node: synthesize final markdown report using Groq.
    """
    logger.info("[Writer] Generating final report...")

    topic = state["topic"]
    notes = state.get("extracted_content", [])
    combined_notes = "\n\n---\n\n".join(notes)

    llm = _get_llm()
    prompt = (
        f"{WRITER_PROMPT}\n\n"
        f"Research topic:\n{topic}\n\n"
        f"Collected notes and content:\n{combined_notes}\n"
    )

    try:
        response = llm.invoke(prompt)
        report = response.content if hasattr(response, "content") else str(response)
        new_state: AgentState = {
            **state,
            "final_report": report,
        }
        return new_state
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Writer node failed: {exc}") from exc


def _build_app() -> Any:
    """
    Build and compile the LangGraph StateGraph for the agent.
    """
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

    return graph.compile()


def _sanitize_topic_for_filename(topic: str) -> str:
    """
    Convert the research topic into a safe file-name fragment.
    """
    slug = topic.strip().lower()
    slug = re.sub(r"\s+", "_", slug)
    slug = re.sub(r"[^a-z0-9_\-]", "", slug)
    return slug or "report"


def main() -> None:
    """
    CLI entrypoint: prompt for topic, run graph, and save report.
    """
    topic = input("Enter research topic: ").strip()
    if not topic:
        logger.info("No topic provided. Exiting.")
        return

    app = _build_app()
    initial_state: AgentState = {
        "topic": topic,
        "sub_questions": [],
        "search_results": [],
        "extracted_content": [],
        "final_report": "",
    }

    final_state = app.invoke(initial_state)
    report = final_state.get("final_report", "")

    os.makedirs("outputs", exist_ok=True)
    filename = f"report_{_sanitize_topic_for_filename(topic)}.md"
    output_path = os.path.join("outputs", filename)

    with open(output_path, "w", encoding="utf-8") as f:
        metadata = (
            f"---\n"
            f"topic: {topic}\n"
            f"generated: {datetime.now().isoformat()}\n"
            f"---\n\n"
        )
        f.write(metadata + report)

    logger.info("Report saved to: %s", output_path)


if __name__ == "__main__":
    main()

