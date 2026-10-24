import re
"""The supervisor's parts that start no process: the launch, the picker, the hooks set aside, the status line, the inbox's announce file, the mirror, and that it imports every module at start. Its processes are tested in supervisor_processes_run.py."""

import io
import json
import os
import signal
import time as timing
from pathlib import Path

from supervisor.inbox import Inbox
from supervisor.supervisor import Supervisor
from supervisor.terminal import Terminal
from journal.support.environment_row import EnvironmentRow
from journal.launcher.support.program_settings import ProgramSettings
from journal.launcher.launch import Launch
from journal.support.choice import Choice
from journal.launcher.menu import Menu
from journal.launcher.remote_install import RemoteInstall
from journal.launcher.screen import Screen
from journal.launcher.support.option import Option
from journal.providers.support.status_line import StatusLine
from journal.providers.claude import Claude


ROWS = [EnvironmentRow("main", True, "2 hours ago", {"claude": "abc"}), EnvironmentRow("spike")]
OTHER = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "say done"}]}]}, "model": "opus"}


def settings_with_other_hooks(root: Path) -> Path:
    path = root / ".claude" / "settings.json"
    path.parent.mkdir(parents=True)
    journal_owned = {"hooks": [{"type": "command", "command": "sh /pkg/journal/hooks/hook.sh claude /p"}]}
    path.write_text(json.dumps({**OTHER, "hooks": {**OTHER["hooks"], "PreToolUse": [journal_owned]}}))
    return path


def menu_answering(tmp_path: Path, monkeypatch, answers: list[str]) -> Menu:
    value = iter(answers)
    monkeypatch.setattr("builtins.input", lambda: next(value))
    menu = Menu(tmp_path, tmp_path / "journal.sh", Screen(io.StringIO()))
    menu.environments = lambda: ROWS
    return menu


def test_the_menu_defaults_and_answers_and_remembers(tmp_path: Path, monkeypatch):
    settings_with_other_hooks(tmp_path)
    menu = menu_answering(tmp_path, monkeypatch, ["", "2", "1", "2"])
    assert menu.choose("claude") == Choice("main", "", stashed_hooks=False, prompt_flags=True)
    assert menu.choose("claude", confirmed=True) == Choice("main", "abc", stashed_hooks=False, prompt_flags=True), "yes takes the defaults, which are last time's answers"
    assert menu.choose("claude", environment="spike", confirmed=True).resume == ""
    assert menu.choose("claude", environment="spike", new=True, stashed=True, omit=False, confirmed=True) == Choice("spike", "", stashed_hooks=True, prompt_flags=True)


def test_a_new_environment_in_the_menu_may_carry_on_from_a_past_conversation_or_start_fresh(tmp_path: Path, monkeypatch):
    calls = []
    kept = [{"provider": "claude", "session": "old-1", "updated_at": 2.0, "first_prompt": "fix the login page\nand the footer", "line_count": 40, "title": "Claude Code", "environment": ""},
            {"provider": "codex", "session": "old-3", "updated_at": 1.5, "first_prompt": "a codex conversation", "line_count": 12, "title": "Codex", "environment": ""},
            {"provider": "claude", "session": "old-2", "updated_at": 1.0, "first_prompt": "already used", "line_count": 9, "title": "Claude Code", "environment": "spike"}]
    shown = []
    menu = menu_answering(tmp_path, monkeypatch, ["3", "login", "2", "1", "1", "2"])
    menu.journal = lambda *argv: calls.append(argv) or (json.dumps(kept) if argv == ("environment", "sessions") else "")
    menu.fill_chat = lambda name, session: calls.append(("filled", name, session.session, session.provider))
    real_pick = menu.screen.pick
    menu.screen.pick = lambda heading, notes, options, default: shown.append((heading, options)) or real_pick(heading, notes, options, default)
    choice = menu.choose("claude")
    assert choice.environment == "login" and choice.resume == "old-1", "the picked conversation is carried on"
    assert ("filled", "login", "old-1", "claude") in calls, "the picked conversation fills the new environment"
    first = next(options for heading, options in shown if heading.startswith("Start login fresh or continue an earlier session"))
    assert [option.label for option in first] == ["Start fresh", "Continue from an earlier session"], "the first screen holds the two choices alone"
    sessions = next(options for heading, options in shown if heading.startswith("Which earlier session does login continue"))
    assert [option.label for option in sessions] == ["fix the login page"], "the sessions show only once continuing is chosen: the launched program's free sessions, each by its first line"
    calls.clear()
    menu = menu_answering(tmp_path, monkeypatch, ["3", "fresh", "1", "1", "2"])
    menu.journal = lambda *argv: calls.append(argv) or (json.dumps(kept) if argv == ("environment", "sessions") else "")
    menu.fill_chat = lambda name, session: calls.append(("filled", name, session.session, session.provider))
    assert menu.choose("claude").environment == "fresh"
    assert not [call for call in calls if call[0] == "filled"], "start fresh fills nothing"
    shown.clear()
    menu = menu_answering(tmp_path, monkeypatch, ["3", "toaster", "1", "2"])
    menu.journal = lambda *argv: calls.append(argv) or (json.dumps(kept) if argv == ("environment", "sessions") else "")
    real_pick = menu.screen.pick
    menu.screen.pick = lambda heading, notes, options, default: shown.append((heading, options)) or real_pick(heading, notes, options, default)
    assert menu.choose("claude", new=True) == Choice("toaster", "", stashed_hooks=False, prompt_flags=True) and not [heading for heading, _ in shown if "earlier session" in heading], "a launch into a worktree, which starts fresh, asks nothing about earlier sessions"


def test_a_menu_line_longer_than_the_terminal_is_cut_to_its_width_so_a_redraw_lands_in_place(monkeypatch):
    import os
    from journal.launcher.screen import Screen
    monkeypatch.setattr("shutil.get_terminal_size", lambda fallback=None: os.terminal_size((30, 20)))
    screen = Screen(io.StringIO())
    lines = screen._lines("Carry on from a past conversation in 1024-toaster?", ["a note far longer than thirty characters, which would wrap"], [Option("The whole journal thing is pretty broken in this repo, can you check")], 0, ())
    plain = [re.sub(r"\x1b\[[0-9;]*m", "", line) for line in lines]
    assert all(len(line) < 30 for line in plain), "no line drawn wider than the terminal, so none wraps"


def test_the_hooks_question_is_asked_even_when_no_other_hooks_are_found_yet(tmp_path: Path, monkeypatch):
    menu = menu_answering(tmp_path, monkeypatch, ["", "2", "2", "1"])
    assert menu.choose("claude") == Choice("main", "", stashed_hooks=True, prompt_flags=False)
    assert menu.choose("claude", confirmed=True).stashed_hooks is True, "remembered"


def test_version_threes_hook_is_somebody_elses(tmp_path: Path):
    from journal.launcher.support.foreign_hooks import ForeignHooks
    assert not ProgramSettings.is_journals({"hooks": [{"type": "command", "command": "sh /p/.journal/src/hook.sh claude /p/.journal"}]})
    assert ProgramSettings.is_journals({"hooks": [{"type": "command", "command": "sh /pkg/src/journal/hooks/hook.sh claude /p"}]})


def test_the_status_line_keeps_claudes_status_json_through_the_journals_script(tmp_path):
    status = StatusLine(tmp_path)
    assert json.loads(status.settings())["statusLine"]["command"] == f"sh '{tmp_path / '.journal' / 'src' / 'journal' / 'hooks' / 'status.sh'}'", "one status script keeps the session's JSON; the band says where the agent is"


def test_x_on_an_environment_deletes_it_after_a_confirmation_and_never_one_an_agent_works(tmp_path: Path, monkeypatch):
    deleted = []
    menu = menu_answering(tmp_path, monkeypatch, ["x1", "1", "x2", "2", "1", "2", "2", "2"])
    menu.journal = lambda *argv: deleted.append(argv) or ""
    assert menu.choose("claude").environment == "main"
    assert deleted == [("environment", "delete", "spike")]


def test_the_other_hooks_are_set_aside_and_put_back_with_later_edits_kept(tmp_path: Path):
    from journal.launcher.support.foreign_hooks import ForeignHooks
    path = settings_with_other_hooks(tmp_path)
    hooks = ForeignHooks(tmp_path, Claude())
    assert hooks.foreign() == [path]
    hooks.stash()
    remaining = json.loads(path.read_text())
    assert list(remaining["hooks"]) == ["PreToolUse"] and remaining["model"] == "opus"
    path.write_text(json.dumps({**remaining, "model": "sonnet"}))
    hooks.restore()
    back = json.loads(path.read_text())
    assert set(back["hooks"]) == {"Stop", "PreToolUse"}
    assert back["model"] == "sonnet" and hooks.foreign() == [path]
    assert hooks.restore() == [], "putting back twice does nothing"


def test_the_picker_moves_with_the_arrow_keys_and_jumps_by_number(tmp_path: Path):
    from journal.launcher.screen import Screen as Picker
    assert Picker._moved(0, "\x1b[B", 3) == 1 and Picker._moved(0, "\x1b[A", 3) == 2 and Picker._moved(0, "3", 3) == 2 and Picker._moved(1, "q", 3) == 1


def test_launch_parses_flags_and_builds_the_commands(tmp_path: Path):
    launch = Launch.parse(["claude", "--env", "spike", "--aside", "--", "--model", "x"], tmp_path)
    assert launch.environment == "spike" and launch.stashed and launch.args == ("--model", "x")
    status = StatusLine(tmp_path)
    assert launch.agent_command(Choice("spike", "s-1", True), status) == ["claude", "--settings", status.settings(), "--model", "x"], "the resume goes in the launch file apart"
    assert launch.agent_command(Choice("spike", "", True, prompt_flags=True), status) == ["claude", "--dangerously-skip-permissions", "--settings", status.settings(), "--model", "x"]
    codex = Launch.parse(["codex"], tmp_path)
    assert codex.agent_command(Choice("spike", "", True), status) == ["codex", "--no-daemon", "-c", "sandbox_workspace_write.network_access=true"], "Codex keeps this launch's environment and reaches its journal's server"
    assert codex.agent_command(Choice("spike", "", True, prompt_flags=True), status) == ["codex", "--no-daemon", "--dangerously-bypass-approvals-and-sandbox"]
    environ = launch.environ(Choice("spike", "", True), "launch-1")
    assert environ["AGENT_JOURNAL_ACTIVE"] == "1" and environ["JOURNAL_ENV"] == "spike", "the journal's own hooks always run"
    assert environ["JOURNAL_LAUNCH"] == "launch-1" and environ["CLAUDE_CODE_SHELL_PREFIX"].endswith("hooks/run.sh"), "the launch is named in the agent's environment, and Claude's shell runs through the journal"
    assert "CLAUDE_CODE_SHELL_PREFIX" not in {k: v for k, v in codex.environ(Choice("spike", "", True), "launch-1").items() if k not in os.environ}, "Codex is handed no Claude variable"
    assert environ["PATH"].startswith(str(tmp_path / ".journal" / "bin")), "the project's own journal command is on the agent's PATH, and nowhere else"
    assert launch.journal_command()[-1] == "serve"


def test_the_launch_puts_the_other_hooks_back_however_the_run_ends(tmp_path: Path):
    from journal.launcher.support.foreign_hooks import ForeignHooks
    path = settings_with_other_hooks(tmp_path)

    class Launched(Launch):
        def choice(self):
            return Choice("main", "", stashed_hooks=True)

        def supervise(self, choice):
            assert len(json.loads(path.read_text())["hooks"]) == 1, "the other hooks are aside while the agent runs"
            raise RuntimeError("the agent fell over")

    try:
        Launched.parse(["claude", "--env", "main", "--aside", "--yes"], tmp_path).run()
    except RuntimeError:
        pass
    assert set(json.loads(path.read_text())["hooks"]) == {"Stop", "PreToolUse"} and ForeignHooks(tmp_path, Claude()).restore() == []


def test_the_launch_notices_the_journals_page_when_it_answers(tmp_path: Path, monkeypatch):
    from journal.app import App
    from journal.config import Config
    app = App(Config(tmp_path, port=0))
    app.server().start()
    try:
        from journal.launcher.support.page_wait import PageWait
        line_text, opened = [], []
        waiting = PageWait(tmp_path / ".journal" / "port", "/tmp/no-supervisor.sock", ("agent-journal", "p · main"), "", line_text.append)
        assert waiting.is_responsive() == f"http://127.0.0.1:{app.server().port}/", "the launch sees the page answer, with no supervisor to tell"
        waiting.wait()
        import webbrowser
        monkeypatch.setattr(webbrowser, "open", lambda url, new=0: opened.append(url) or True)
        monkeypatch.setattr(PageWait, "tab_open", lambda self, url: False)
        PageWait(tmp_path / ".journal" / "port", "/tmp/no-supervisor.sock", ("agent-journal", "p · main"), "?env=main", line_text.append).wait()
        assert opened == [f"http://127.0.0.1:{app.server().port}/?env=main"] and line_text[-1] == f"viewer: opened {opened[0]}", "with no tab open the viewer is opened, and the launch log says so"
    finally:
        app.server().stop()


def test_the_supervisor_imports_every_module_at_start_so_an_upgrade_never_changes_a_running_one():
    import ast
    late = []
    for path in sorted((Path(__file__).parent.parent / "src" / "supervisor").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                late += [f"{path.name}:{inner.lineno}" for inner in ast.walk(node) if isinstance(inner, (ast.Import, ast.ImportFrom))]
    assert late == [], "an import inside a function would load what an upgrade put on disk into a supervisor already running"


def test_the_mirror_goes_with_its_supervisor(tmp_path: Path):
    from supervisor.screen_copy import ScreenCopy
    mirror = ScreenCopy(tmp_path / "screens" / "main.out")
    mirror.add(b"Switch model?")
    mirror._written_at = 0
    mirror.flush()
    mirror.keyed()
    assert mirror.path.exists() and mirror.path.with_suffix(".keyed").exists()
    mirror.close()
    assert not mirror.path.exists() and not mirror.path.with_suffix(".keyed").exists(), "no screen is left for a process that is gone"


def test_the_inbox_announces_where_the_screen_is_mirrored(tmp_path: Path):
    inbox = Inbox(Path(f"/tmp/journal-{os.getuid()}") / f"test-{os.getpid()}.sock", tmp_path / "inboxes" / "main")
    inbox.open_mirrored(tmp_path / "screens" / "main.out")
    try:
        assert json.loads(inbox.announced_at.read_text())["screen"] == str(tmp_path / "screens" / "main.out"), "the journal reads the screen where the supervisor says it is"
    finally:
        inbox.close()


def test_the_launch_writes_what_the_supervisor_starts_and_a_bad_launch_file_is_refused(tmp_path: Path, capsys):
    from supervisor.__main__ import main
    launch = Launch.parse(["claude", "--env", "spike", "--no-journal"], tmp_path)
    saved = launch.launch_file(Choice("spike", "s1"), StatusLine(tmp_path))
    assert saved["front"]["command"][0] == "claude" and saved["front"]["resume"] == ["--resume", "s1"] and saved["services"] == [], "a launch with a journal running already starts none of its own; the resume apart, for a restart to replace"
    assert saved["launch"] and saved["front"]["env"]["JOURNAL_LAUNCH"] == saved["launch"], "the launch's id is in its file and in the agent's environment alike"
    assert Launch.parse(["codex"], tmp_path).launch_file(Choice("spike", "s1"), StatusLine(tmp_path))["front"]["resume"] == ["resume", "s1"]
    assert saved["announce"].endswith("runtime/inboxes/spike") and saved["screen"].endswith("runtime/screens/spike.out") and f"journal-{os.getuid()}" in saved["socket"]
    with_journal = Launch.parse(["claude", "--env", "spike"], tmp_path).launch_file(Choice("spike", ""), StatusLine(tmp_path))
    assert [s["name"] for s in with_journal["services"]] == ["journal"], "the launch file names the journal server alone; the services the installed version needs beside it are started by its boot, so an upgrade brings them with no new launch"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"front": {"command": ["claude"]}}))
    assert main([str(bad)]) == 0, "a launch file that cannot be started from ends the launcher's loop rather than being tried again every second"
    assert "has no socket, announce, front's folder, front's env" in capsys.readouterr().err
    assert main([str(tmp_path / "missing.json")]) == 0 and "cannot be read" in capsys.readouterr().err


def test_the_supervisor_restarts_itself_by_exiting_to_its_launcher_with_the_conversation_to_resume_in_the_launch_file(tmp_path: Path):
    from supervisor.request import Request
    from supervisor.services import Services
    from supervisor.supervisor import ENDED, RESTART, Supervisor
    from supervisor.terminal import Terminal
    path = tmp_path / "spike.json"
    path.write_text(json.dumps(Launch.parse(["claude", "--env", "spike", "--no-journal"], tmp_path).launch_file(Choice("spike", "s1"), StatusLine(tmp_path))))
    started = json.loads(path.read_text())
    supervisor = Supervisor(Terminal(["true"], str(tmp_path), {}, ("--resume", "s1")), Inbox(tmp_path / "s.sock", tmp_path / "announce"), Services(), stdin=None, launch=path)
    assert supervisor.verbs.handle(Request.parsed({"verb": "hello"})).answer["outdated"] is False
    supervisor.source = "older"
    assert supervisor.verbs.handle(Request.parsed({"verb": "hello"})).answer["outdated"] is True, "hello says when the code on disk is not the code it started with, so the journal knows to restart it"
    assert supervisor.verbs.handle(Request.parsed({"verb": "restart", "name": "supervisor", "resume": ["--resume", "s2"]})).is_success
    assert supervisor._code == RESTART, "the restart is an exit with the code that has the launcher start it again"
    assert json.loads(path.read_text()) == {**started, "front": {**started["front"], "resume": ["--resume", "s2"]}}, "the launch file keeps everything but the conversation to resume"
    again = Supervisor(Terminal(["true"], str(tmp_path), {}, ("--resume", "s2")), Inbox(tmp_path / "s.sock", tmp_path / "announce"), Services(), stdin=None, launch=path)
    again.restart("supervisor", (), 0.0)
    assert json.loads(path.read_text())["front"]["resume"] == ["--resume", "s2"], "a restart that names no conversation keeps the one running"
    again.stop()
    assert again._code == ENDED, "a stop ends the launcher's loop"


def test_the_supervisor_imports_nothing_but_the_standard_library_and_itself():
    import ast
    import sys
    foreign = []
    for path in sorted((Path(__file__).parent.parent / "src" / "supervisor").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            names = [item.name for item in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            foreign += [f"{path.name}: {name}" for name in names if name.split(".")[0] not in (*sys.stdlib_module_names, "supervisor")]
    assert foreign == [], "the supervisor knows no journal module and needs nothing installed"


def test_a_service_that_cannot_start_dies_in_its_log_and_never_takes_the_supervisor_down(tmp_path: Path):
    from supervisor.service import Service
    from supervisor.services import Services
    services = Services(Service("mypy", ["bin/gone", "serve"], tmp_path / "moved-mid-upgrade", {}, tmp_path / "mypy.log"))
    services.start_all()
    services.revive_stopped()
    assert not services.runs("mypy") and "mypy could not start" in (tmp_path / "mypy.log").read_text(), "its folder gone, as mid-upgrade, the start dies at once and says why"


def test_a_fault_in_a_verb_or_a_turn_is_written_down_and_the_supervisor_carries_on(tmp_path: Path):
    from supervisor.request import Request
    from supervisor.services import Services
    from supervisor.supervisor import Supervisor
    from supervisor.terminal import Terminal
    faults = tmp_path / "supervisor.log"
    supervisor = Supervisor(Terminal(["true"], str(tmp_path), {}), Inbox(tmp_path / "s.sock", tmp_path / "announce"), Services(), stdin=None, faults=faults)
    reply = supervisor.verbs.handle(Request.parsed({"verb": "start", "name": "mypy", "command": ["true"], "folder": str(tmp_path), "env": {"COUNT": 3}}))
    assert not reply.is_success and "start failed in the supervisor, which carries on" in reply.error, "a verb that raises is answered with why"
    supervisor.turn()
    assert faults.read_text().count("supervisor fault, carried on") == 2, "the verb's fault and the turn's are both written down, and neither ended the supervisor"


def test_a_worktree_launch_makes_its_worktree_and_never_hands_the_flag_to_the_agent(tmp_path: Path):
    import subprocess
    from journal.support.worktree import Worktree
    launch = Launch.parse(["claude", "--worktree", "1012-inventory-page", "--resume", "abc"], tmp_path)
    assert launch.worktree == "1012-inventory-page" and launch.args == ("--resume", "abc"), "the journal takes --worktree; Claude Code would remove a worktree it made"
    assert Launch.parse(["claude", "-w", "x"], tmp_path).worktree == "x"
    git = lambda *args: subprocess.run(["git", "-C", str(tmp_path), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m", "start")
    produced = Worktree(tmp_path, "1012-inventory-page").created()
    assert produced == tmp_path / ".claude" / "worktrees" / "1012-inventory-page" and (produced / ".git").exists(), "made at Claude Code's own place, so an older one is found"
    assert "worktree-1012-inventory-page" in git("branch").stdout
    subprocess.run(["rm", "-rf", str(produced)], timeout=30)
    assert Worktree(tmp_path, "1012-inventory-page").created().is_dir(), "a worktree whose folder went is made again on its branch, and nothing is lost from the branch"


def test_a_bare_worktree_flag_takes_the_chosen_environments_name(tmp_path: Path):
    import subprocess
    git = lambda *args: subprocess.run(["git", "-C", str(tmp_path), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text('{"permissions": {}}\n')
    git("add", ".claude/settings.json")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", "start")
    for argv in (["claude", "-w"], ["claude", "--worktree", "--resume", "abc"]):
        launch = Launch.parse(argv, tmp_path)
        assert launch.worktree_launch and launch.worktree == "" and "--worktree" not in launch.args and "-w" not in launch.args
    launch = Launch.parse(["claude", "-w"], tmp_path)
    produced = launch.launch_file(Choice("calm-river", "", False, False), StatusLine(tmp_path))
    assert produced["front"]["folder"] == str(tmp_path / ".claude" / "worktrees" / "calm-river"), "the worktree is named after the environment the menu chose"
    hooked = json.loads((tmp_path / ".claude" / "worktrees" / "calm-river" / ".claude" / "settings.json").read_text())
    assert "hook.sh" in json.dumps(hooked.get("hooks", {})) and str(tmp_path) in json.dumps(hooked["hooks"]), "a project whose settings git tracks without the journal's hooks gets them in the new worktree too, posting to the project's journal"
    assert "worktree-calm-river" in git("branch").stdout


def test_a_worktree_shares_the_projects_journal_skills_and_hooks_without_git_seeing_them(tmp_path: Path):
    import subprocess
    import threading
    from journal.support.worktree import Worktree
    git = lambda *args, time=tmp_path: subprocess.run(["git", "-C", str(time), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    (tmp_path / ".gitignore").write_text("/.journal\n/.claude/settings.json\n")
    (tmp_path / "AGENTS.md").write_text("the law\n")
    git("add", ".gitignore", "AGENTS.md")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", "start")
    (tmp_path / ".journal").mkdir()
    (tmp_path / ".journal" / "port").write_text("8421")
    (tmp_path / ".claude" / "skills" / "journal").mkdir(parents=True)
    (tmp_path / ".claude" / "skills" / "journal" / "SKILL.md").write_text("# The journal\n")
    (tmp_path / ".claude" / "settings.json").write_text("{}")
    threads = [threading.Thread(target=Worktree(tmp_path, "calm-river").created) for _ in range(4)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    tree = tmp_path / ".claude" / "worktrees" / "calm-river"
    assert (tree / ".journal" / "port").read_text() == "8421" and (tree / ".journal").is_symlink(), "the worktree reads the project's journal, made four times at once"
    assert (tree / ".claude" / "skills" / "journal" / "SKILL.md").is_file() and (tree / ".claude" / "settings.json").is_symlink(), "an untracked skill and an ignored hook file are shared"
    assert not (tree / "AGENTS.md").is_symlink(), "a tracked file comes with the checkout, never a link"
    assert git("status", "--porcelain", time=tree).stdout == "" and git("status", "--porcelain").stdout == "", "git sees none of it, in the worktree or the project"


def test_a_worktree_links_the_projects_journal_even_when_git_brings_old_journal_files(tmp_path: Path):
    import subprocess
    from journal.support.worktree import Worktree
    git = lambda *args: subprocess.run(["git", "-C", str(tmp_path), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    (tmp_path / ".journal").mkdir()
    (tmp_path / ".journal" / "old.txt").write_text("from long ago")
    git("add", ".journal/old.txt")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", "start")
    (tmp_path / ".journal" / "port").write_text("8421")
    tree = Worktree(tmp_path, "x").created()
    assert (tree / ".journal").is_symlink() and (tree / ".journal" / "port").read_text() == "8421", "the checked-out old journal files make way for the link"


def test_a_command_or_hook_inside_a_worktree_works_the_worktrees_environment(tmp_path: Path):
    import subprocess
    from journal.support.worktree import Worktree
    git = lambda *args: subprocess.run(["git", "-C", str(tmp_path), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m", "start")
    tree = Worktree(tmp_path, "calm-river").created()
    (tree / "deep").mkdir()
    rule = Path(__file__).parents[1] / "src" / "journal" / "hooks" / "environment.sh"
    matched = lambda time, environment="": subprocess.run(["sh", "-c", f'. "{rule}"; journal_environment'], cwd=time, capture_output=True, text=True, timeout=30, env={"PATH": os.environ["PATH"], **({"JOURNAL_ENV": environment} if environment else {})}).stdout
    assert matched(tree / "deep") == "calm-river", "a command run anywhere inside the worktree works its environment"
    assert matched(tmp_path) == "main" and matched(tmp_path.parent) == "main", "the project's own checkout, and a folder outside git, work main"
    assert matched(tree, "spike") == "spike", "an environment named outright wins"


def test_a_conversation_resumed_runs_in_its_environment_and_that_environments_worktree(tmp_path: Path, monkeypatch):
    import subprocess
    from journal.support.worktree import Worktree
    git = lambda *args: subprocess.run(["git", "-C", str(tmp_path), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m", "start")
    tree = Worktree(tmp_path, "calm-river").created()
    menu = menu_answering(tmp_path, monkeypatch, [])
    menu.environments = lambda: [EnvironmentRow("main", last_sessions={"claude": "abc"}), EnvironmentRow("calm-river", last_sessions={"claude": "def"})]
    assert Launch.parse(["claude", "--resume", "def"], tmp_path).resume_folder(menu) == "calm-river", "a conversation is resumed in the environment it last ran in"
    assert Launch.parse(["claude", "--resume", "zzz"], tmp_path).resume_folder(menu) == "" and Launch.parse(["claude"], tmp_path).resume_folder(menu) == ""
    status = StatusLine(tmp_path)
    plain = Launch.parse(["claude", "--resume", "def"], tmp_path)
    assert plain.launch_file(Choice("calm-river", "", False, False), status)["front"]["folder"] == str(tree), "an environment with a worktree runs its agent there, where its conversations are"
    assert plain.launch_file(Choice("main", "", False, False), status)["front"]["folder"] == str(tmp_path)


def test_the_menu_marks_an_environment_with_a_worktree_and_its_branch(tmp_path: Path):
    import subprocess
    from journal.support.worktree import Worktree
    git = lambda *args: subprocess.run(["git", "-C", str(tmp_path), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m", "start")
    Worktree(tmp_path, "calm-river").created()
    assert Worktree(tmp_path, "calm-river").badges() == ("worktree on worktree-calm-river",) and Worktree(tmp_path, "main").badges() == ()


def test_a_worktree_whose_folder_and_branch_went_is_made_again_from_its_kept_tip(tmp_path: Path):
    import subprocess
    from journal.support.worktree import Worktree
    git = lambda *args, time=tmp_path: subprocess.run(["git", "-C", str(time), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m", "start")
    tree = Worktree(tmp_path, "1012-inventory-page").created()
    (tree / "page.py").write_text("PAGE = 1\n")
    git("add", "page.py", time=tree)
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", "the page", time=tree)
    Worktree(tmp_path, "1012-inventory-page").created()
    git("worktree", "remove", "--force", str(tree))
    git("branch", "-D", "worktree-1012-inventory-page")
    repeat = Worktree(tmp_path, "1012-inventory-page").created()
    assert (repeat / "page.py").read_text() == "PAGE = 1\n", "the committed work comes back from the kept tip though the folder and the branch were removed"


def test_a_folder_no_worktree_owns_is_moved_aside_never_deleted_and_a_failed_make_leaves_nothing_half_made(tmp_path: Path):
    import subprocess
    from journal.support.worktree import Worktree
    from journal.support.worktree_failure import WorktreeFailure
    git = lambda *args: subprocess.run(["git", "-C", str(tmp_path), *args], capture_output=True, text=True, timeout=30)
    git("init", "-q")
    git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m", "start")
    stray = tmp_path / ".claude" / "worktrees" / "calm-river"
    stray.mkdir(parents=True)
    (stray / "mine.txt").write_text("not a worktree's\n")
    produced = Worktree(tmp_path, "calm-river").created()
    stashed = [p for p in produced.parent.iterdir() if p.name.startswith("calm-river.moved-aside-")]
    assert (produced / ".git").exists() and len(stashed) == 1 and (stashed[0] / "mine.txt").read_text() == "not a worktree's\n", "the stray folder is kept aside and the worktree made"
    git("branch", "worktree-taken")
    git("worktree", "add", str(tmp_path / "elsewhere"), "worktree-taken")
    try:
        Worktree(tmp_path, "taken").created()
        raise AssertionError("a branch checked out elsewhere cannot be made a second time")
    except WorktreeFailure:
        pass
    assert not (tmp_path / ".claude" / "worktrees" / "taken").exists(), "nothing half made is left at the worktree's place"


def test_the_boot_screen_offers_a_newer_release_of_the_same_major_before_the_journal_starts(tmp_path: Path, monkeypatch):
    from journal.config import Config
    from journal.features.updates.support.release_source import ReleaseSource
    from journal.launcher.support.update_prompt import UpdatePrompt
    from journal.version import VERSION
    major = VERSION.split(".")[0]
    monkeypatch.setattr(ReleaseSource, "tags", lambda self, prefix: [f"v{VERSION}", f"v{major}.99.0", f"v{int(major) + 1}.0.0"])
    asked = tmp_path / "asked"
    (tmp_path / ".journal" / "src").mkdir(parents=True)
    (tmp_path / ".journal" / "src" / "journal.sh").write_text(f'echo "$@" >> {asked}\n')
    answers = iter(["2", "1"])
    monkeypatch.setattr("builtins.input", lambda: next(answers))
    proposal = UpdatePrompt(Config(tmp_path), Screen(io.StringIO()), ReleaseSource())
    assert proposal.newest().version == f"{major}.99.0", "the newest of the same major, never the next major"
    assert not proposal.installed_newer() and not asked.exists(), "Start as it is installs nothing"
    assert proposal.installed_newer() and asked.read_text() == "update\n", "Update runs journal update, the one route every update takes, before the journal starts"


def test_every_start_asks_to_skip_the_permission_prompts_with_skip_selected_even_when_carrying_on(tmp_path: Path, monkeypatch):
    requested = []
    menu = menu_answering(tmp_path, monkeypatch, ["", "", ""])
    selected = menu.screen.pick
    monkeypatch.setattr(menu.screen, "pick", lambda heading, notes, options, default: requested.append((heading, default)) or selected(heading, notes, options, default))
    choice = menu.choose("claude")
    assert choice.resume == "abc" and choice.prompt_flags, "carrying on main's conversation still starts with the prompts skipped"
    assert ("Run without permission prompts", 0) in requested, "the question is asked, with skip under the cursor"


def test_a_start_command_that_skips_the_prompts_itself_is_not_asked(tmp_path: Path):
    assert Launch.parse(["claude", "--dangerously-skip-permissions"], tmp_path).is_skipping()
    assert Launch.parse(["codex", "--dangerously-bypass-approvals-and-sandbox"], tmp_path).is_skipping()
    assert Launch.parse(["claude", "--skip"], tmp_path).is_skipping() and not Launch.parse(["claude"], tmp_path).is_skipping()


def test_a_closed_window_stops_the_supervisor_without_writing_to_the_screen_that_went(tmp_path: Path):
    from supervisor.band import Band
    from supervisor.band_labels import BandLabels
    from supervisor.services import Services
    from supervisor.supervisor import Supervisor
    from supervisor.terminal import Terminal
    read, write = os.pipe()
    os.close(read)
    os.close(write)
    supervisor = Supervisor(Terminal(["true"], str(tmp_path), {}), Inbox(tmp_path / "s.sock", tmp_path / "announce"), Services(), stdin=None, stdout=write, band=Band(BandLabels("a", "b", "c"), write))
    supervisor.handle_hangup()
    supervisor.stop()
    assert supervisor.band is None, "a hang-up leaves no band to clear on a terminal that is gone"


def test_the_band_a_launch_file_carries_is_read_by_its_wire_keys():
    from supervisor.band_labels import BandLabels
    labels = BandLabels.parsed({"left": "agent-journal", "middle": "app · main", "right": "journal starting…"})
    assert labels == BandLabels("agent-journal", "app · main", "journal starting…"), "the launch file's band keys, left, middle and right, are the band's words"


def test_a_new_environment_named_at_the_launch_gets_its_row_before_the_agent_starts(tmp_path: Path, monkeypatch):
    produced = []
    menu = menu_answering(tmp_path, monkeypatch, [])
    menu.journal = lambda *argv: produced.append(argv) or ""
    assert menu.choose("codex", environment="providers", confirmed=True).environment == "providers"
    assert produced == [("environment", "create", "providers")], "a hook or command in an environment with no row is refused, so the launch makes the row first"
    produced.clear()
    menu.choose("codex", environment="main", confirmed=True)
    assert produced == [], "an environment that exists is not made again"


def test_a_restart_asked_with_a_delay_waits_so_the_command_that_asked_ends_its_answer_first(tmp_path: Path):
    import time
    from supervisor.request import Request
    from supervisor.service import Service
    from supervisor.services import Services
    from supervisor.supervisor import Supervisor
    from supervisor.terminal import Terminal
    restarts = []
    service = Service("journal", ["sleep", "5"], tmp_path, {}, tmp_path / "journal.log")
    service.restart = lambda: restarts.append(time.monotonic())
    supervisor = Supervisor(Terminal(["true"], str(tmp_path), {}), Inbox(tmp_path / "s.sock", tmp_path / "announce"), Services(service), stdin=None, faults=tmp_path / "supervisor.log")
    asked = time.monotonic()
    assert supervisor.verbs.handle(Request.parsed({"verb": "restart", "name": "journal", "after": 0.3})).is_success
    assert restarts == [], "the answer goes back before the restart"
    time.sleep(0.6)
    assert len(restarts) == 1 and restarts[0] - asked >= 0.3, "and the restart comes once the delay is over"


def test_a_team_journal_launches_in_the_normal_checkout_and_a_worktree_only_when_asked(tmp_path: Path):
    import subprocess
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, timeout=30)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=Ada", "-c", "user.email=ada@example.com", "commit", "-q", "--allow-empty", "-m", "first"], check=True, timeout=30)
    (tmp_path / ".journal").mkdir(exist_ok=True)
    (tmp_path / ".journal" / "team.json").write_text("{}")
    shared = Launch.parse(["claude", "--env", "main", "--no-journal"], tmp_path).launch_file(Choice("main", ""), StatusLine(tmp_path))
    assert shared["front"]["folder"] == str(tmp_path) and not (tmp_path / ".claude" / "worktrees" / "main").exists(), "joining a team never moves an environment out of the checkout the person works in"
    asked = Launch.parse(["claude", "--env", "main", "--worktree", "feature", "--no-journal"], tmp_path).launch_file(Choice("main", ""), StatusLine(tmp_path))
    assert asked["front"]["folder"] == str(tmp_path / ".claude" / "worktrees" / "feature"), "a worktree asked for is still made and used"


def test_a_session_from_the_main_checkout_is_carried_into_the_worktree_or_the_launch_says_it_starts_fresh(tmp_path: Path, monkeypatch, capsys):
    import subprocess
    from journal.providers.claude import Claude
    project = tmp_path / "project"
    subprocess.run(["git", "init", "-q", str(project)], check=True, timeout=30)
    subprocess.run(["git", "-C", str(project), "-c", "user.name=Ada", "-c", "user.email=ada@example.com", "commit", "-q", "--allow-empty", "-m", "first"], check=True, timeout=30)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claude"))
    session = tmp_path / "claude" / "projects" / Claude.folder_name(project) / "s1.jsonl"
    session.parent.mkdir(parents=True)
    session.write_text("{}\n")
    carried = Launch.parse(["claude", "--env", "ada-main", "--worktree", "ada-main", "--no-journal"], project).launch_file(Choice("ada-main", "s1"), StatusLine(project))
    worktree = project / ".claude" / "worktrees" / "ada-main"
    assert carried["front"]["resume"] == ["--resume", "s1"] and (tmp_path / "claude" / "projects" / Claude.folder_name(worktree) / "s1.jsonl").is_file(), "yesterday's session is carried into the environment's worktree and resumed there"
    fresh = Launch.parse(["claude", "--env", "ada-main", "--worktree", "ada-main", "--no-journal"], project).launch_file(Choice("ada-main", "gone"), StatusLine(project))
    assert fresh["front"]["resume"] == [] and "cannot be carried into" in capsys.readouterr().err, "a session that cannot be found starts fresh, and the launch says so"


def test_a_stop_whose_child_was_reaped_by_a_nested_stop_never_signals_pid_minus_one(tmp_path: Path, monkeypatch):
    """A second stop from a signal handler can reap the agent while the first waits; the first then signals nothing, since on macOS a signal to -1 reaches every process of the user."""
    terminal = Terminal(["true"], str(tmp_path), {})
    terminal.pid = 4242
    sent = []
    monkeypatch.setattr(os, "kill", lambda pid, kind: sent.append((pid, kind)))

    def nested_reap(seconds: float) -> None:
        terminal.pid = -1

    monkeypatch.setattr(terminal, "wait_exit", nested_reap)
    assert terminal.stop(0.1) == 0
    assert sent == [(4242, signal.SIGTERM)], "only the child the stop began with hears a signal, and no SIGKILL follows once another caller reaped it"
    assert terminal.stop(0.1) == 0 and sent == [(4242, signal.SIGTERM)], "a terminal with no child signals nothing"
    assert Supervisor.is_running(-1) is False and Supervisor.is_running(0) is False, "an owner pid of zero or below is never probed"


def test_remote_install_hands_the_host_it_reaches_as_the_team_address():
    """The installer asks the address the team reaches the server at only when the ssh target names none: an ssh alias."""
    assert "TEAM_ADDRESS=203.0.113.5 sh" in RemoteInstall("root@203.0.113.5", "4.55.0", {}).command()[-1]
    assert "TEAM_ADDRESS=team.example.com sh" in RemoteInstall("deploy@team.example.com", "4.55.0", {}).command()[-1]
    assert "TEAM_ADDRESS" not in RemoteInstall("teamserver", "4.55.0", {}).command()[-1], "an ssh alias names no address the team can reach"
    beside = RemoteInstall.parsed(["install", "app@shop.example.com", "--address", "203.0.113.7", "--https-port", "8443", "--http-port", "8081"]).command()[-1]
    assert "TEAM_ADDRESS=203.0.113.7 TEAM_HTTPS_PORT=8443 TEAM_HTTP_PORT=8081 sh" in beside, "a server whose 80 and 443 are another service's takes the team server on ports of its own, at the address given"


class PressedKeys:
    """Keys a test presses: each read hands the next, and an interrupt is raised as a Ctrl+C would be."""

    def __init__(self, *keys) -> None:
        self.keys = list(keys)

    def read(self) -> list[str]:
        key = self.keys.pop(0)
        if key is KeyboardInterrupt:
            raise KeyboardInterrupt
        return [key]


def test_the_boot_menu_is_left_quietly_with_escape_or_ctrl_c():
    from journal.launcher.support.option import Option
    for key, code in (("\x1b", 0), (KeyboardInterrupt, 130)):
        printed = io.StringIO()
        try:
            Screen(printed, PressedKeys(key)).key_choice("Start which journal?", [], [Option("main")], 0, ())
            raise AssertionError("the menu went on")
        except SystemExit as left:
            assert left.code == code, (key, left.code)
        assert "Left without starting the journal." in printed.getvalue() and "Traceback" not in printed.getvalue()



def test_a_release_tag_is_made_in_one_place_and_a_hand_written_one_is_refused_at_commit():
    """The team image and the installer are asked for by the release's tag, v4.55.3; a version written into a tag by hand once asked for 4.55.2, which no release has."""
    import importlib.util
    from journal.support.release import Release
    assert Release.tagged("4.55.3") == "v4.55.3" and Release.tagged("v4.55.3") == "v4.55.3", "either spelling gives the tag"
    assert "/releases/download/v4.55.3/install.sh" in RemoteInstall("root@203.0.113.5", "4.55.3", {}).command()[-1]
    spec = importlib.util.spec_from_file_location("release_tags", Path(__file__).resolve().parents[1] / "scripts" / "checks" / "release_tags.py")
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    assert check.problems() == [], "no tag is written by hand in the packages"
    assert all(check.HAND_WRITTEN_TAG.search(line) for line in ('url = f"v{version}"', 'tag = "v" + version', '"releases/download/v{version}/install.sh"')), "the guard knows a tag written by hand"


def test_the_commit_guard_refuses_a_private_word_or_a_real_machines_address_and_never_quotes_the_word():
    import importlib.util
    spec = importlib.util.spec_from_file_location("private_data", Path(__file__).resolve().parents[1] / "scripts" / "checks" / "private_data.py")
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    found = guard.problems([("a.py", 3, "ssh root@8.8.8.8 for the Acme shop"), ("b.py", 9, "curl https://203.0.113.5 and 127.0.0.1 and 10.0.0.2")], ["acme"])
    assert found == ["a.py:3: private word 1 of " + str(guard.WORDS), "a.py:3: the address 8.8.8.8 is a real machine's; use a documentation address such as 203.0.113.5"], found
    assert all("acme" not in line.lower() for line in found), "the word itself is never printed"


def test_a_supervisor_started_again_ends_the_services_a_supervisor_killed_outright_left_running(tmp_path: Path):
    import time
    from supervisor.service import Service
    from supervisor.service_record import ServiceRecord
    left = Service("journal", ["sleep", "61"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "journal.log")
    left.start()
    stranger = Service("stranger", ["sleep", "62"], tmp_path, {"PATH": os.environ["PATH"]}, tmp_path / "stranger.log")
    stranger.start()
    try:
        record = tmp_path / "main.services"
        ServiceRecord(record).write({left.pid(): left.command, stranger.pid(): ["sleep", "999"]})
        ServiceRecord(record).ended()
        deadline = time.time() + 5
        while left._process.poll() is None and time.time() < deadline:
            time.sleep(0.05)
        assert left._process.poll() is not None, "the service the killed supervisor left is ended by the next"
        assert stranger.is_active(), "a recorded pid now running another command is left alone"
        assert ServiceRecord(record).recorded() == {}, "and the record is emptied"
    finally:
        left.stop()
        stranger.stop()


def test_the_left_arrow_in_the_boot_menu_asks_the_question_before_again(tmp_path: Path):
    from journal.launcher.support.keys import Keys
    left, enter, down = Keys.BACK[0], Keys.ENTER[0], Keys.DOWN[0]
    printed = io.StringIO()
    # main, then left at "carry on" back to the environments, main again, no carry on, prompts skipped, hooks kept; left on the first question stays on it
    screen = Screen(printed, PressedKeys(left, enter, left, enter, down, enter, enter, enter, enter, enter))
    screen.interactive = True
    screen._pick_with_keys = screen.key_choice
    menu = Menu(tmp_path, tmp_path / "journal.sh", screen)
    menu.environments = lambda: ROWS
    choice = menu.choose("claude")
    assert choice.environment == "main" and choice.resume == "" and choice.prompt_flags, choice
    assert printed.getvalue().count("Which environment") == 3, "the environments were asked again after the left arrow, and a left arrow on them asked them again"
    assert printed.getvalue().count("Carry on from the last session") == 3, "asked twice, the second drawn again as the down arrow moved"
    assert "← to go back" in printed.getvalue()


def test_a_health_url_must_answer_200_in_time_a_health_file_must_be_fresh_and_the_launch_file_carries_both_checks(tmp_path: Path):
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from supervisor.front_health import FrontHealth
    from supervisor.health_check import HealthCheck
    from supervisor.launch_file import LaunchFile

    answers = {"/well": 200, "/unwell": 503}

    class StandIn(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(answers[self.path])
            self.end_headers()

        def log_message(self, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), StandIn)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    try:
        assert HealthCheck(url=f"http://127.0.0.1:{port}/well").fault() == "", "a URL that answers 200 is well"
        assert "answered 503" in HealthCheck(url=f"http://127.0.0.1:{port}/unwell").fault(), "one that answers anything else is not, and says what it answered"
        (tmp_path / "port").write_text(str(port))
        assert HealthCheck(url="http://127.0.0.1:{port}/well", port_file=str(tmp_path / "port")).fault() == "", "a URL's port is read from the file it names, which a server started again rewrites"
        assert "names no port" in HealthCheck(url="http://127.0.0.1:{port}/well", port_file=str(tmp_path / "none")).fault()
    finally:
        server.shutdown()
    assert "did not answer" in HealthCheck(url=f"http://127.0.0.1:{port}/well", timeout_seconds=1).fault(), "a URL nothing answers is not well"
    beat = tmp_path / "beat"
    assert "never written" in HealthCheck(file=str(beat), fresh_seconds=5).fault()
    beat.write_text("1")
    assert HealthCheck(file=str(beat), fresh_seconds=5).fault() == "", "a file written within its seconds is well"
    os.utime(beat, (timing.time() - 60, timing.time() - 60))
    assert "last written 60 seconds ago" in HealthCheck(file=str(beat), fresh_seconds=5).fault(), "and one older is not"
    hooks = FrontHealth(str(beat), 30.0, "warned")
    assert hooks.is_dead(timing.time(), timing.time() - 120), "an agent whose output moves while its hooks file stands still past the limit has dead hooks"
    assert not hooks.is_dead(timing.time() - 120, timing.time() - 120), "one whose output stands still too is only idle"
    assert not hooks.is_dead(timing.time(), timing.time() - 5), "and one started within the limit is given the time to fire its first hook"
    beat.write_text("2")
    assert not hooks.is_dead(timing.time(), timing.time() - 120), "a hook written again ends it"
    launch = Launch.parse(["claude", "--env", "spike"], tmp_path).launch_file(Choice("spike", ""), StatusLine(tmp_path))
    journal_health = launch["services"][0]["health"]
    assert journal_health["url"] == "http://127.0.0.1:{port}/journal/health" and journal_health["port_file"] == str(tmp_path / ".journal" / "port") and journal_health["failures"] == 3, "the journal service is checked at its health URL, its port read from the project's port file"
    assert launch["front"]["health"]["file"] == str(tmp_path / ".journal" / "runtime" / "hooks" / "spike.fired") and "start it again from the project's root with journal" in launch["front"]["health"]["warning"], "the agent's hooks are watched through the file the hook script writes, and the warning names the fix"
    path = tmp_path / "launch.json"
    path.write_text(json.dumps(launch))
    supervisor = LaunchFile.read(path).supervisor()
    assert supervisor.services.service("journal").health == HealthCheck(**journal_health) and supervisor.front_health == FrontHealth(**launch["front"]["health"]), "the supervisor takes both checks as the launch file says them, knowing nothing of what they check"
