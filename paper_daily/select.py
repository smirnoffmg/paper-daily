import datetime
import random


def select_paper(
    papers: list[dict[str, object]],
    date: str | None = None,
    top_k: int = 30,
) -> dict[str, object]:
    if not papers:
        raise ValueError("Cannot select from an empty paper list")
    seed = date or datetime.date.today().isoformat()
    pool = list(papers[:top_k])
    rng = random.Random(seed)
    rng.shuffle(pool)
    return pool[0]
