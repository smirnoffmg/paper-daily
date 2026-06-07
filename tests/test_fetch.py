import unittest.mock as mock

from paper_daily.fetch import (
    _filter_venues,
    _reconstruct_abstract,
    _work_to_paper,
    fetch_papers,
)

_WORK: dict[str, object] = {
    "id": "https://openalex.org/W1234567",
    "title": "Test Paper",
    "abstract_inverted_index": {"hello": [0], "world": [1]},
    "authorships": [
        {"author": {"display_name": "Alice"}},
        {"author": {"display_name": "Bob"}},
    ],
    "publication_year": 2026,
    "primary_location": {"source": {"display_name": "NeurIPS"}},
    "topics": [{"display_name": f"Topic {i}"} for i in range(7)],
}


def _make_resp(results: list[dict], next_cursor: str | None = None) -> mock.MagicMock:
    resp = mock.MagicMock()
    resp.raise_for_status = mock.MagicMock()
    resp.json.return_value = {
        "results": results,
        "meta": {"next_cursor": next_cursor} if next_cursor else {},
    }
    return resp


# --- _reconstruct_abstract ---


def test_reconstruct_abstract_empty() -> None:
    assert _reconstruct_abstract({}) == ""


def test_reconstruct_abstract_single_word() -> None:
    assert _reconstruct_abstract({"hello": [0]}) == "hello"


def test_reconstruct_abstract_multiword() -> None:
    assert _reconstruct_abstract({"hello": [0], "world": [1]}) == "hello world"


def test_reconstruct_abstract_noncontinuous_positions() -> None:
    result = _reconstruct_abstract({"a": [0], "b": [3]})
    assert "a" in result
    assert "b" in result


def test_reconstruct_abstract_word_at_multiple_positions() -> None:
    assert _reconstruct_abstract({"the": [0, 2], "cat": [1]}) == "the cat the"


# --- _work_to_paper ---


def test_work_to_paper_paper_id_extracted() -> None:
    assert _work_to_paper(_WORK)["paperId"] == "W1234567"


def test_work_to_paper_abstract_reconstructed() -> None:
    assert _work_to_paper(_WORK)["abstract"] == "hello world"


def test_work_to_paper_missing_abstract_is_empty() -> None:
    assert _work_to_paper(dict(_WORK, abstract_inverted_index=None))["abstract"] == ""


def test_work_to_paper_authors_extracted() -> None:
    assert _work_to_paper(_WORK)["authors"] == [{"name": "Alice"}, {"name": "Bob"}]


def test_work_to_paper_author_without_display_name_skipped() -> None:
    work = dict(_WORK, authorships=[{"author": {}}, {"author": {"display_name": "Alice"}}])
    assert _work_to_paper(work)["authors"] == [{"name": "Alice"}]


def test_work_to_paper_topics_capped_at_5() -> None:
    assert len(_work_to_paper(_WORK)["topics"]) == 5  # type: ignore[arg-type]


def test_work_to_paper_venue_extracted() -> None:
    assert _work_to_paper(_WORK)["venue"] == "NeurIPS"


# --- _filter_venues ---

_PAPERS: list[dict[str, object]] = [
    {"paperId": "a", "venue": "NeurIPS 2024"},
    {"paperId": "b", "venue": "ICML Workshop"},
    {"paperId": "c", "venue": ""},
]


def test_filter_venues_case_insensitive() -> None:
    result = _filter_venues(_PAPERS, ["neurips"])
    assert [p["paperId"] for p in result] == ["a"]


def test_filter_venues_no_match_returns_empty() -> None:
    assert _filter_venues(_PAPERS, ["arxiv"]) == []


def test_filter_venues_substring_match() -> None:
    assert [p["paperId"] for p in _filter_venues(_PAPERS, ["icml"])] == ["b"]


def test_filter_venues_paper_without_venue_excluded() -> None:
    result = _filter_venues(_PAPERS, ["neurips"])
    assert all(p["paperId"] != "c" for p in result)


# --- fetch_papers ---


def test_fetch_papers_returns_paper() -> None:
    with mock.patch("paper_daily.fetch.requests.get") as mock_get:
        mock_get.return_value = _make_resp([_WORK])
        papers = fetch_papers(["ml"], candidates_per_query=10, venues=[])
    assert len(papers) == 1
    assert papers[0]["paperId"] == "W1234567"


def test_fetch_papers_deduplicates_across_queries() -> None:
    with mock.patch("paper_daily.fetch.requests.get") as mock_get:
        with mock.patch("paper_daily.fetch.time.sleep"):
            mock_get.return_value = _make_resp([_WORK])
            papers = fetch_papers(["ml", "dl"], candidates_per_query=10, venues=[])
    assert len(papers) == 1


def test_fetch_papers_empty_batch_stops_pagination() -> None:
    with mock.patch("paper_daily.fetch.requests.get") as mock_get:
        mock_get.return_value = _make_resp([])
        papers = fetch_papers(["ml"], candidates_per_query=10, venues=[])
    assert papers == []


def test_fetch_papers_missing_next_cursor_stops_pagination() -> None:
    with mock.patch("paper_daily.fetch.requests.get") as mock_get:
        mock_get.return_value = _make_resp([_WORK], next_cursor=None)
        fetch_papers(["ml"], candidates_per_query=200, venues=[])
    assert mock_get.call_count == 1


def test_fetch_papers_inter_query_delay_called() -> None:
    with mock.patch("paper_daily.fetch.requests.get") as mock_get:
        with mock.patch("paper_daily.fetch.time.sleep") as mock_sleep:
            mock_get.return_value = _make_resp([_WORK])
            fetch_papers(["ml", "dl", "rl"], candidates_per_query=10, venues=[])
    assert mock_sleep.call_count == 2


def test_fetch_papers_venue_filter_applied() -> None:
    other: dict[str, object] = {
        **_WORK,  # type: ignore[arg-type]
        "id": "https://openalex.org/W9999999",
        "primary_location": {"source": {"display_name": "ICML"}},
    }
    with mock.patch("paper_daily.fetch.requests.get") as mock_get:
        mock_get.return_value = _make_resp([_WORK, other])
        papers = fetch_papers(["ml"], candidates_per_query=10, venues=["neurips"])
    assert len(papers) == 1
    assert papers[0]["venue"] == "NeurIPS"
