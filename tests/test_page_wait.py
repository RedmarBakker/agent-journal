from journal.launcher.support.page_wait import PageWait
from journal.support.supervisor_reply import SupervisorReply


def test_page_wait_retries_the_band_update_when_the_journal_answers_before_the_supervisor(monkeypatch, tmp_path):
    requests = []

    def ask(socket, request):
        requests.append((socket, request))
        if len(requests) == 1:
            raise OSError("the supervisor has not opened its socket yet")
        return SupervisorReply(True)

    monkeypatch.setattr("journal.launcher.support.page_wait.SupervisorSocket.ask", ask)
    monkeypatch.setattr("journal.launcher.support.page_wait.time.sleep", lambda _: None)
    page = PageWait(
        tmp_path / "port",
        str(tmp_path / "supervisor.sock"),
        ("journal", "project · smoke-1"),
        "",
        lambda _: None,
    )

    page.shown("http://127.0.0.1:8424/")

    assert len(requests) == 2, "PageWait asks again after the worktree supervisor opens its socket"
    assert requests[-1] == (
        str(tmp_path / "supervisor.sock"),
        {"verb": "band", "left": "journal", "middle": "project · smoke-1", "right": "http://127.0.0.1:8424/"},
    )


def test_page_wait_updates_the_band_on_the_first_ready_supervisor_socket(monkeypatch, tmp_path):
    requests = []
    monkeypatch.setattr(
        "journal.launcher.support.page_wait.SupervisorSocket.ask",
        lambda path, request: requests.append((path, request)) or SupervisorReply(True),
    )
    page = PageWait(
        tmp_path / "port",
        str(tmp_path / "supervisor.sock"),
        ("journal", "project · main"),
        "",
        lambda _: None,
    )

    page.shown("http://127.0.0.1:8424/")

    assert requests == [
        (
            str(tmp_path / "supervisor.sock"),
            {"verb": "band", "left": "journal", "middle": "project · main", "right": "http://127.0.0.1:8424/"},
        )
    ]
