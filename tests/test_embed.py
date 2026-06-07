import unittest.mock as mock

import numpy as np

from paper_daily.embed import embed_texts, paper_text


def test_paper_text_title_only() -> None:
    assert paper_text({"title": "My Title", "abstract": ""}) == "My Title"


def test_paper_text_title_and_abstract() -> None:
    assert paper_text({"title": "My Title", "abstract": "Some text"}) == "My Title [SEP] Some text"


def test_paper_text_none_abstract_treated_as_empty() -> None:
    assert paper_text({"title": "My Title", "abstract": None}) == "My Title"


def test_paper_text_missing_title_uses_empty_string() -> None:
    result = paper_text({"abstract": "Some text"})
    assert result == " [SEP] Some text"


def test_embed_texts_empty_returns_correct_shape() -> None:
    model = mock.MagicMock()
    model.get_sentence_embedding_dimension.return_value = 768
    result = embed_texts(model, [])
    assert result.shape == (0, 768)


def test_embed_texts_delegates_to_model_encode() -> None:
    model = mock.MagicMock()
    expected = np.array([[1.0, 2.0, 3.0]])
    model.encode.return_value = expected
    result = embed_texts(model, ["some text"])
    model.encode.assert_called_once_with(
        ["some text"], show_progress_bar=False, convert_to_numpy=True
    )
    assert np.array_equal(result, expected)
