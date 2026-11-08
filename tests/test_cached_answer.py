import threading

from journal.support import cached_answer
from journal.support.cached_answer import CachedAnswer


def test_an_answer_never_asked_is_asked_at_once_however_short_the_time_since_boot(monkeypatch):
    monkeypatch.setattr(cached_answer.time, "monotonic", lambda: 10.0)
    asked = threading.Event()
    answer = CachedAnswer(lambda: asked.set() or "fresh", 3600.0, "first")
    answer.time()
    assert asked.wait(2), "the first read starts the question even ten seconds after boot"
