import unittest.mock as mock

import pytest

from paper_daily.telegram import post_message


def test_post_message_sends_correct_payload() -> None:
    with mock.patch("paper_daily.telegram.requests.post") as mock_post:
        mock_resp = mock.MagicMock()
        mock_resp.ok = True
        mock_post.return_value = mock_resp
        post_message("token123", "@channel", "Hello")
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    payload = kwargs["json"]
    assert payload["chat_id"] == "@channel"
    assert payload["text"] == "Hello"
    assert payload["parse_mode"] == "HTML"
    assert payload["link_preview_options"] == {"is_disabled": True}


def test_post_message_raises_on_error_response() -> None:
    with mock.patch("paper_daily.telegram.requests.post") as mock_post:
        mock_resp = mock.MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request"
        mock_post.return_value = mock_resp
        with pytest.raises(RuntimeError, match="Telegram API error 400"):
            post_message("token", "@ch", "text")
