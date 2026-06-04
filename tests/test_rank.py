import numpy as np
import pytest

from paper_daily.rank import cosine_similarity, rank_papers

_PAPERS = [
    {"paperId": "a", "title": "Alpha paper", "abstract": "alpha content"},
    {"paperId": "b", "title": "Beta paper", "abstract": "beta content"},
    {"paperId": "c", "title": "Gamma paper", "abstract": "gamma content"},
]


def test_cosine_identical() -> None:
    v = np.array([1.0, 2.0, 3.0])
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_orthogonal() -> None:
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_zero_vector() -> None:
    a = np.array([0.0, 0.0])
    b = np.array([1.0, 2.0])
    assert cosine_similarity(a, b) == 0.0


def test_empty_profile_returns_unchanged() -> None:
    class _FakeModel:
        pass

    result = rank_papers(_PAPERS, _FakeModel(), [])  # type: ignore[arg-type]
    assert result == _PAPERS


def test_ranking_sorts_descending() -> None:
    """Papers should come out highest-similarity-first."""
    import unittest.mock as mock

    # Build embeddings so paper "a" is closest to the profile vector
    profile_emb = np.array([[1.0, 0.0, 0.0]])
    # paper a: parallel to profile → similarity 1.0
    # paper b: orthogonal → similarity 0.0
    # paper c: opposite → similarity -1.0
    candidate_embs = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
        ]
    )

    with mock.patch("paper_daily.rank.embed_texts") as mock_embed:
        mock_embed.side_effect = [profile_emb, candidate_embs]
        model = mock.MagicMock()
        result = rank_papers(_PAPERS, model, ["some profile text"])

    assert [p["paperId"] for p in result] == ["a", "b", "c"]
