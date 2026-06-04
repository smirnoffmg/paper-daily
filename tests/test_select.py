import pytest

from paper_daily.select import select_paper

_PAPERS = [{"paperId": str(i), "title": f"Paper {i}"} for i in range(50)]


def test_determinism_same_date() -> None:
    a = select_paper(_PAPERS, date="2026-01-01")
    b = select_paper(_PAPERS, date="2026-01-01")
    assert a["paperId"] == b["paperId"]


def test_different_dates_vary() -> None:
    results = {select_paper(_PAPERS, date=f"2026-01-{d:02d}")["paperId"] for d in range(1, 15)}
    assert len(results) > 1


def test_empty_raises() -> None:
    with pytest.raises(ValueError):
        select_paper([])


def test_top_k_limits_pool() -> None:
    # With top_k=1 only the first paper can ever be selected
    result = select_paper(_PAPERS, date="2026-06-01", top_k=1)
    assert result["paperId"] == _PAPERS[0]["paperId"]


def test_fewer_papers_than_top_k() -> None:
    small = _PAPERS[:5]
    result = select_paper(small, date="2026-06-01", top_k=30)
    assert result in small
