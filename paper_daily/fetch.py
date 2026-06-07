import datetime
import logging
import time
from typing import Any

import requests
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

_OA_WORKS = "https://api.openalex.org/works"
_MAILTO = "smirnoffmg@gmail.com"
_INTER_QUERY_DELAY = 1.0


def _is_rate_limit(exc: BaseException) -> bool:
    return (
        isinstance(exc, requests.HTTPError)
        and exc.response is not None
        and exc.response.status_code == 429
    )


@retry(
    retry=retry_if_exception(_is_rate_limit),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def _get(url: str, params: dict[str, str | int]) -> requests.Response:
    headers = {"User-Agent": f"paper-daily/0.1 (mailto:{_MAILTO})"}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp


def _reconstruct_abstract(inverted_index: dict[str, list[int]]) -> str:
    if not inverted_index:
        return ""
    max_pos = max(pos for positions in inverted_index.values() for pos in positions)
    words: list[str] = [""] * (max_pos + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(w for w in words if w)


def _work_to_paper(work: dict[str, Any]) -> dict[str, object]:
    oa_id = str(work.get("id") or "")
    paper_id = oa_id.rsplit("/", 1)[-1] if oa_id else ""

    inv_index: dict[str, list[int]] | None = work.get("abstract_inverted_index")
    abstract = _reconstruct_abstract(inv_index) if inv_index else ""

    authorships: list[dict[str, Any]] = work.get("authorships") or []
    authors = [
        {"name": str(a["author"]["display_name"])}
        for a in authorships
        if (a.get("author") or {}).get("display_name")
    ]

    primary_location: dict[str, Any] = work.get("primary_location") or {}
    source: dict[str, Any] = primary_location.get("source") or {}
    venue = str(source.get("display_name") or "")

    raw_topics: list[dict[str, Any]] = work.get("topics") or []
    topics = [str(t["display_name"]) for t in raw_topics[:5] if t.get("display_name")]

    return {
        "paperId": paper_id,
        "title": str(work.get("title") or ""),
        "abstract": abstract,
        "authors": authors,
        "year": work.get("publication_year"),
        "venue": venue,
        "topics": topics,
    }


def fetch_papers(
    queries: list[str],
    candidates_per_query: int,
    venues: list[str],
) -> list[dict[str, object]]:
    current_year = datetime.date.today().year

    seen: set[str] = set()
    papers: list[dict[str, object]] = []

    for i, query in enumerate(queries):
        if i > 0:
            time.sleep(_INTER_QUERY_DELAY)

        cursor = "*"
        remaining = candidates_per_query
        while remaining > 0:
            per_page = min(remaining, 200)
            params: dict[str, str | int] = {
                "search": query,
                "filter": f"publication_year:{current_year},type:article,open_access.is_oa:true",
                "select": (
                    "id,title,abstract_inverted_index,authorships,publication_year,primary_location,topics"
                ),
                "per-page": per_page,
                "cursor": cursor,
                "mailto": _MAILTO,
            }
            resp = _get(url=_OA_WORKS, params=params)
            data = resp.json()
            batch: list[dict[str, Any]] = data.get("results") or []
            if not batch:
                break
            for work in batch:
                paper = _work_to_paper(work)
                pid = str(paper["paperId"])
                if pid and pid not in seen:
                    seen.add(pid)
                    papers.append(paper)
            remaining -= len(batch)
            next_cursor: str = (data.get("meta") or {}).get("next_cursor") or ""
            if not next_cursor or len(batch) < per_page:
                break
            cursor = next_cursor

    if venues:
        papers = _filter_venues(papers, venues)

    logger.info("Fetched %d unique papers", len(papers))
    return papers


def _filter_venues(papers: list[dict[str, object]], venues: list[str]) -> list[dict[str, object]]:
    lower_venues = [v.lower() for v in venues]
    return [p for p in papers if any(v in str(p.get("venue", "")).lower() for v in lower_venues)]
