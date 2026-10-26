"""Every shell call an agent makes reaches the journal's runner and becomes an output when it runs long, on the calls a consumer project's agent reported escaping: a bare ./scripts/test.sh, which Claude Code evals unquoted, and a call Claude Code was told to run in its own background."""

import os
import re
import stat

import pytest

from journal.app import App
from journal.features.shell.support.shell_request import ShellRequest
from journal.features.shell.support.shell_runner import ShellRunner
from journal.models.setting import Setting
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.chain import Chain
from journal.supervisor_link import SupervisorLink
from tests.test_features import booted, hook

AGENT = Caller.agent("main", "s1", "claude")
MAIN = 1
BARE_SUITE = "setopt NO_EXTENDED_GLOB 2>/dev/null || true && eval ./scripts/test.sh < /dev/null && pwd -P >| /dev/null"
SUITE_CALL = {"command": "./scripts/test.sh", "description": "Run the full suite including end-to-end tests", "run_in_background": True}


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture
def app(app: App):
    with app.container.get(Scope).environment(MAIN):
        hook(app, "SessionStart")
        app.console().run(["environment", "overview"], AGENT)
        yield app


def test_a_bare_command_claude_code_evals_unquoted_is_read_as_the_agents_own_part():
    parts = [part for part in Chain.parts(BARE_SUITE) if part.recorded]
    assert [part.text for part in parts] == ["./scripts/test.sh"]


def test_a_bare_eval_is_quoted_before_a_part_of_it_is_replaced():
    replaced = Chain.replaced(BARE_SUITE, "./scripts/test.sh", "./scripts/test.sh --filter='ContactPayloadTest'")
    assert "eval './scripts/test.sh --filter='\"'\"'ContactPayloadTest'\"'\"'' < /dev/null" in replaced, replaced


def test_the_bare_suite_call_runs_through_the_runner_and_becomes_an_output_when_it_runs_long(app: App):
    script = app.config.root / "scripts" / "test.sh"
    script.parent.mkdir(exist_ok=True)
    script.write_text("#!/bin/sh\nsleep 2\necho 'Tests: 41 passed (105 assertions)'\n")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    app.container.get(SettingRows).save(Setting(environment_id=0, key="shell.foreground", value=1), Actor.system())
    link = app.container.get(SupervisorLink)
    link.working(MAIN)
    request = ShellRequest(line=BARE_SUITE, cwd=str(app.config.root), shell="/bin/sh", environment=dict(os.environ))
    shown = b"".join(app.container.get(ShellRunner).run(request, AGENT, MAIN)).decode() + link.pending_lines(MAIN)
    moved = re.search(r"output (\d+)", shown)
    assert moved, shown
    assert app.container.get(CommandOutputs).find(int(moved.group(1))).command == "./scripts/test.sh"


def test_a_shell_call_claude_code_would_run_in_its_own_background_runs_in_the_foreground_through_the_journal(app: App):
    status, answer = hook(app, "PreToolUse", tool_name="Bash", tool_input=SUITE_CALL)
    output = answer["hookSpecificOutput"]
    assert status == 200 and output["permissionDecision"] == "allow", answer
    assert output["updatedInput"] == {**SUITE_CALL, "run_in_background": False}

