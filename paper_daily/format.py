import re


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _to_hashtag(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9_]", "", topic.lower().replace(" ", "_").replace("-", "_"))
    return f"#{slug}" if slug else ""


def format_message(paper: dict[str, object], abstract_max_chars: int = 800) -> str:
    title = str(paper.get("title") or "Untitled")
    year = str(paper.get("year") or "")
    venue = str(paper.get("venue") or "")
    paper_id = str(paper.get("paperId") or "")
    abstract = str(paper.get("abstract") or "")

    authors_raw: list[dict[str, object]] = paper.get("authors", [])  # type: ignore[assignment]
    author_names = [str(a.get("name", "")) for a in authors_raw if a.get("name")]
    authors_str = ", ".join(author_names) if author_names else "Unknown authors"

    if len(abstract) > abstract_max_chars:
        abstract = abstract[:abstract_max_chars].rstrip() + "…"

    oa_url = f"https://openalex.org/{paper_id}" if paper_id else ""

    year_part = f" ({_esc(year)})" if year else ""
    lines: list[str] = [
        f"📄 <b>{_esc(title)}</b>",
        "",
        f"👥 {_esc(authors_str)}{year_part}",
    ]
    if venue:
        lines.append(f"🏛 {_esc(venue)}")
    lines += ["", _esc(abstract)]
    if oa_url:
        lines += ["", f'🔗 <a href="{oa_url}">Open in OpenAlex</a>']

    topics: list[str] = paper.get("topics", [])  # type: ignore[assignment]
    tags = [t for topic in topics if (t := _to_hashtag(str(topic)))]
    if tags:
        lines += ["", " ".join(tags)]

    return "\n".join(lines)
