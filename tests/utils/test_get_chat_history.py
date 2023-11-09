from ai_document_search_backend.utils.get_chat_history import get_chat_history

empty_history = []
non_empty_history = [("a", "b"), ("c", "d"), ("e", "f")]


def test_minus_one_returns_whole_history():
    assert get_chat_history(empty_history, -1) == ""
    assert (
        get_chat_history(non_empty_history, -1)
        == "Question:a\nAnswer:b\nQuestion:c\nAnswer:d\nQuestion:e\nAnswer:f"
    )


def test_minus_two_returns_whole_history():
    assert get_chat_history(empty_history, -2) == ""
    assert (
        get_chat_history(non_empty_history, -2)
        == "Question:a\nAnswer:b\nQuestion:c\nAnswer:d\nQuestion:e\nAnswer:f"
    )


def test_zero_returns_empty_history():
    assert get_chat_history(empty_history, 0) == ""
    assert get_chat_history(non_empty_history, 0) == ""


def test_one_returns_last_pair():
    assert get_chat_history(empty_history, 1) == ""
    assert get_chat_history(non_empty_history, 1) == "Question:e\nAnswer:f"


def test_two_returns_last_two_pairs():
    assert get_chat_history(empty_history, 2) == ""
    assert get_chat_history(non_empty_history, 2) == "Question:c\nAnswer:d\nQuestion:e\nAnswer:f"


def test_four_returns_whole_history():
    assert get_chat_history(empty_history, 4) == ""
    assert (
        get_chat_history(non_empty_history, 4)
        == "Question:a\nAnswer:b\nQuestion:c\nAnswer:d\nQuestion:e\nAnswer:f"
    )
