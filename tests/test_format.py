from paper_daily.format import format_message

_PAPER: dict[str, object] = {
    "paperId": "W2741809807",
    "title": "Attention Is All You Need",
    "abstract": "A" * 1000,
    "year": 2017,
    "venue": "NeurIPS",
    "authors": [{"name": "Vaswani"}, {"name": "Shazeer"}],
}


def test_abstract_truncated() -> None:
    msg = format_message(_PAPER, abstract_max_chars=100)
    assert "…" in msg


def test_abstract_not_truncated_when_short() -> None:
    paper = dict(_PAPER, abstract="Short abstract.")
    msg = format_message(paper, abstract_max_chars=800)
    assert "…" not in msg


def test_missing_venue_defaults_to_arxiv() -> None:
    paper = dict(_PAPER, venue=None)
    msg = format_message(paper, abstract_max_chars=800)
    assert "arXiv" in msg


def test_url_present() -> None:
    msg = format_message(_PAPER, abstract_max_chars=800)
    assert "openalex.org/W2741809807" in msg


def test_title_in_message() -> None:
    msg = format_message(_PAPER, abstract_max_chars=800)
    assert "Attention Is All You Need" in msg


def test_html_special_chars_escaped() -> None:
    paper = dict(_PAPER, title="A < B & C > D", abstract="safe")
    msg = format_message(paper, abstract_max_chars=800)
    assert "<" not in msg.split("<b>")[1].split("</b>")[0]
    assert "&lt;" in msg
    assert "&amp;" in msg


def test_authors_joined() -> None:
    msg = format_message(_PAPER, abstract_max_chars=800)
    assert "Vaswani" in msg
    assert "Shazeer" in msg


def test_year_in_message() -> None:
    msg = format_message(_PAPER, abstract_max_chars=800)
    assert "2017" in msg
