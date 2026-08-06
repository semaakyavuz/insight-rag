from unittest.mock import MagicMock, patch

from app.services.llm import generate_answer


def test_generate_answer_returns_llm_content():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Bu bir test cevabidir."

    with patch("app.services.llm.get_client") as mock_get_client:
        mock_get_client.return_value.chat.completions.create.return_value = (
            mock_response
        )

        answer = generate_answer("Test sorusu?", ["ilgili baglam parcasi"])

    assert answer == "Bu bir test cevabidir."


def test_generate_answer_sends_system_and_user_messages():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "cevap"

    with patch("app.services.llm.get_client") as mock_get_client:
        mock_create = mock_get_client.return_value.chat.completions.create
        mock_create.return_value = mock_response

        generate_answer("Soru?", ["chunk1", "chunk2"])

        _, kwargs = mock_create.call_args
        messages = kwargs["messages"]

    assert messages[0]["role"] == "system"
    assert "bağlam" in messages[0]["content"].lower()
    assert messages[1]["role"] == "user"
    assert "chunk1" in messages[1]["content"]
    assert "chunk2" in messages[1]["content"]
    assert "Soru?" in messages[1]["content"]
