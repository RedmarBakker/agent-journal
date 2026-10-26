from journal.app import App
from journal.support.caller import Caller
from tests.in_process import posted

USER_CALLER = Caller.user("main")
FEATURE_PREFIX = "features."


def user_set(app: App, key: str, value: object, caller: Caller = USER_CALLER) -> None:
    """Sets a setting the way the user does: an option by running journal settings set through the console, a feature's switch by saving it on the Settings page."""
    if key.startswith(FEATURE_PREFIX):
        status, answer = posted(app, "/journal/settings", {"features": {key.removeprefix(FEATURE_PREFIX): value}}, {"X-Journal-Env": "main"})
        assert status == 200, answer
        return
    text = ("on" if value else "off") if isinstance(value, bool) else "\n".join(value) if isinstance(value, list) else str(value)
    outcome = app.console().run(["settings", "set", key, text], caller)
    assert outcome.code == 0, outcome.error
