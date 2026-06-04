import logging
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from paper_daily.embed import embed_texts, paper_text

logger = logging.getLogger(__name__)


def load_profile(profile_path: str) -> list[str]:
    path = Path(profile_path)
    if not path.exists():
        return []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def rank_papers(
    papers: list[dict[str, object]],
    model: SentenceTransformer,
    profile_texts: list[str],
) -> list[dict[str, object]]:
    if not profile_texts:
        logger.info("No profile — returning papers unranked")
        return papers

    profile_embeddings = embed_texts(model, profile_texts)
    interest_vector: np.ndarray = profile_embeddings.mean(axis=0)

    candidate_texts = [paper_text(p) for p in papers]
    candidate_embeddings = embed_texts(model, candidate_texts)

    scores = [cosine_similarity(emb, interest_vector) for emb in candidate_embeddings]
    ranked = sorted(zip(scores, papers), key=lambda x: x[0], reverse=True)
    logger.info("Ranked %d papers; top score %.4f", len(ranked), ranked[0][0] if ranked else 0)
    return [p for _, p in ranked]
