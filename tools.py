"""
Tooling utilities for the autonomous research agent.

Provides:
- search_web: Web search via Tavily.
- read_url: Content extraction via Jina Reader.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
MAX_CONTENT_CHARS = 2000

_tavily_client: TavilyClient | None = None


def _get_tavily_client() -> TavilyClient:
    """
    Create and return a TavilyClient using the TAVILY_API_KEY env variable.

    Raises:
        RuntimeError: If the API key is missing.
    """
    global _tavily_client
    if _tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError("TAVILY_API_KEY is not set in the environment.")
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


def search_web(query: str, retries: int = 3) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily and return the top 5 results.

    Each result contains:
        - title: str
        - url: str
        - content: str

    Args:
        query: Search query string.

    Returns:
        A list of dictionaries with search result data.

    Raises:
        RuntimeError: If the search fails.
    """
    for attempt in range(retries):
        try:
            client = _get_tavily_client()
            response = client.search(query=query, max_results=5)
            results: List[Dict[str, Any]] = []

            for item in response.get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                    }
                )

            return results
        except Exception as exc:  # pylint: disable=broad-except
            if attempt == retries - 1:
                raise RuntimeError(
                    f"Tavily search failed after {retries} attempts: {exc}"
                ) from exc
            time.sleep(2**attempt)


def read_url(url: str) -> str:
    """
    Read and extract content from a URL using Jina Reader.

    This uses the public Jina Reader endpoint: https://r.jina.ai/{url}

    Args:
        url: The URL to read.

    Returns:
        Extracted markdown text content.

    Raises:
        RuntimeError: If the request fails or returns a bad status.
    """
    jina_endpoint = f"https://r.jina.ai/{url}"

    try:
        response = requests.get(jina_endpoint, timeout=10, headers=HEADERS)
        response.raise_for_status()
        text = response.text.strip()
        if not text:
            raise RuntimeError(f"Empty response from Jina Reader for URL: {url}")
        return text[:MAX_CONTENT_CHARS]
    except Exception as exc:  # pylint: disable=broad-except
        raise RuntimeError(f"Error reading URL via Jina Reader '{url}': {exc}") from exc


