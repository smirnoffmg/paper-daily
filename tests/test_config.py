from paper_daily.config import Settings

_REQ = {"telegram_token": "t", "telegram_chat_id": "c"}


def _s(**kwargs: object) -> Settings:
    return Settings(_env_file=None, **{**_REQ, **kwargs})  # type: ignore[arg-type]


def test_csv_string_parsed_to_list() -> None:
    s = _s(paper_queries="ml, dl, rl")
    assert s.paper_queries == ["ml", "dl", "rl"]


def test_csv_string_strips_whitespace() -> None:
    s = _s(paper_queries=" ml , dl ")
    assert s.paper_queries == ["ml", "dl"]


def test_csv_empty_entries_filtered() -> None:
    s = _s(paper_queries="ml,,dl")
    assert s.paper_queries == ["ml", "dl"]


def test_csv_whitespace_only_entries_filtered() -> None:
    s = _s(paper_queries="ml, ,dl")
    assert s.paper_queries == ["ml", "dl"]


def test_list_passthrough_unchanged() -> None:
    s = _s(paper_queries=["ml", "dl"])
    assert s.paper_queries == ["ml", "dl"]


def test_default_paper_queries() -> None:
    s = _s()
    assert s.paper_queries == ["machine learning", "deep learning"]


def test_default_paper_venues_empty() -> None:
    s = _s()
    assert s.paper_venues == []


def test_paper_venues_csv_parsed() -> None:
    s = _s(paper_venues="NeurIPS, ICML")
    assert s.paper_venues == ["NeurIPS", "ICML"]
