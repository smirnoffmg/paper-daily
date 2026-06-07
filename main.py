import logging

from paper_daily.config import Settings
from paper_daily.embed import load_model
from paper_daily.fetch import fetch_papers
from paper_daily.format import format_message
from paper_daily.rank import load_profile, rank_papers
from paper_daily.select import select_paper
from paper_daily.telegram import post_message

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    cfg = Settings()
    papers = fetch_papers(cfg.paper_queries, cfg.candidates_per_query, cfg.paper_venues)
    if not papers:
        raise SystemExit("No papers found — check your queries or API key")
    model = load_model(cfg.model_name)
    profile = load_profile(cfg.profile_path)
    ranked = rank_papers(papers, model, profile)
    paper = select_paper(ranked, top_k=cfg.top_k)
    text = format_message(paper, cfg.abstract_max_chars)
    post_message(cfg.telegram_token, cfg.telegram_chat_id, text)


if __name__ == "__main__":
    main()
