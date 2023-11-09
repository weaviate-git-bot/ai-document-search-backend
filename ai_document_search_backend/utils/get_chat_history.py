def get_chat_history(inputs: list[tuple[str, str]], max_history_length: int) -> str:
    res = []
    if max_history_length == 0:
        return ""
    take_n_last = len(inputs) if max_history_length < 0 else max_history_length
    for human, ai in inputs[-take_n_last:]:
        res.append(f"Question:{human}\nAnswer:{ai}")
    return "\n".join(res)
