import json

from journal.providers.support.codex_status_file import CodexStatusFile


def reported_usage(tokens: int) -> str:
    return json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": {
        "model_context_window": 1000,
        "last_token_usage": {"total_tokens": tokens},
        "total_token_usage": {"total_tokens": 1000000},
    }}}) + "\n"


def test_the_latest_usage_record_updates_context_without_counting_cumulative_tokens(tmp_path):
    path = tmp_path / "session.jsonl"
    path.write_text(reported_usage(400))
    status = CodexStatusFile(path)
    assert status.reading().context == 0.4
    with path.open("a") as file:
        file.write(json.dumps({"type": "token_usage_record", "payload": {
            "usage": {"total_tokens": 500}, "thread_token_usage": {"total_tokens": 2000000},
        }}) + "\n")
    assert status.reading().context == 0.5


def test_an_incomplete_record_waits_for_its_final_bytes(tmp_path):
    path = tmp_path / "session.jsonl"
    path.write_text(reported_usage(400))
    status = CodexStatusFile(path)
    assert status.reading().context == 0.4
    update = reported_usage(800)
    with path.open("a") as file:
        file.write(update[:len(update) // 2])
    assert status.reading().context == 0.4
    with path.open("a") as file:
        file.write(update[len(update) // 2:])
    assert status.reading().context == 0.8


def test_a_replaced_log_discards_the_previous_sessions_status(tmp_path):
    path = tmp_path / "session.jsonl"
    path.write_text(reported_usage(900))
    status = CodexStatusFile(path)
    assert status.reading().context == 0.9
    replacement = tmp_path / "replacement.jsonl"
    replacement.write_text(json.dumps({"type": "turn_context", "payload": {"model": "new-model", "effort": "high"}}) + "\n")
    replacement.replace(path)
    current = status.reading()
    assert current.context is None
    assert (current.model, current.effort) == ("new-model", "high")


def test_truncating_the_log_resets_the_read_position(tmp_path):
    path = tmp_path / "session.jsonl"
    path.write_text(reported_usage(900) + reported_usage(800))
    status = CodexStatusFile(path)
    assert status.reading().context == 0.8
    path.write_text(reported_usage(200))
    assert status.reading().context == 0.2


def test_a_rate_limit_only_record_keeps_the_last_reported_context(tmp_path):
    path = tmp_path / "session.jsonl"
    path.write_text(reported_usage(400))
    status = CodexStatusFile(path)
    assert status.reading().context == 0.4
    with path.open("a") as file:
        file.write(json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": None}}) + "\n")
    assert status.reading().context == 0.4
