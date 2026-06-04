import logging

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


def load_model(model_name: str) -> SentenceTransformer:
    logger.info("Loading model %s", model_name)
    model: SentenceTransformer = SentenceTransformer(model_name)
    return model


def embed_texts(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, model.get_sentence_embedding_dimension() or 768))
    embeddings: np.ndarray = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings


def paper_text(paper: dict[str, object]) -> str:
    title = str(paper.get("title") or "")
    abstract = str(paper.get("abstract") or "")
    if abstract:
        return f"{title} [SEP] {abstract}"
    return title
