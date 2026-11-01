from hosted_login import escape_login_message, prune_expired_sessions
from login_throttle import LoginThrottle


def test_global_login_cap_slows_different_sources():
    throttle = LoginThrottle(source_limit=10, global_limit=2, global_lockout=30)

    assert throttle.failed("198.51.100.1", 10) == 1
    assert throttle.failed("203.0.113.17", 11) == 30
    assert throttle.retry_after("192.0.2.9", 12) == 29


def test_login_form_message_escapes_html():
    assert escape_login_message('<script onload="run()">') == "&lt;script onload=&quot;run()&quot;&gt;"


def test_expired_hosted_sessions_are_removed():
    sessions = {"current": 12.0, "expired": 10.0}

    prune_expired_sessions(sessions, 10.0)

    assert sessions == {"current": 12.0}
