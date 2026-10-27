"""Phase two: journal task create, start, log, done and list run against a real .journal/journal.db through the console, from the terminal and through the server."""

from pathlib import Path

import pytest

from worker_dispatch import dispatched

from journal.app import App
from journal.repositories.scope import Scope
from journal.config import Config
from journal.support.caller import Caller
from journal.providers.providers import Providers
from journal.support.actor import Actor
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.task_logs import TaskLogs
from journal.repositories.tasks import Tasks


MAIN = Caller.user("main")


@pytest.fixture
def app(journal_root: Path) -> App:
    return App(Config(journal_root, port=0))


def test_a_task_lives_through_the_cli(app: App):
    console = app.console()
    assert console.run(["task", "create", "write the notes", "--brief", "what and where"], MAIN).code == 0
    assert console.run(["task", "start", "1"], MAIN).code == 0
    assert console.run(["task", "log", "1", "half done"], MAIN).code == 0
    assert "started  write the notes" in console.run(["task", "list"], MAIN).text
    assert console.run(["task", "complete", "1", "--how", "published"], MAIN).code == 0
    tasks = app.container.get(Tasks)
    task = tasks.find(1)
    assert task.state == TaskState.COMPLETED and task.outcome == "published" and task.started_at is not None
    assert task.creator == Actor.user(1)
    assert [log.line for log in app.container.get(TaskLogs).logs(task)] == ["half done"]
    assert (app.config.database).is_file()


def test_the_agent_is_the_actor_when_its_session_is_set(app: App):
    app.console().run(["task", "create", "t", "--start"], Caller.agent("main", "s-1", "claude"))
    assert app.container.get(Tasks).find(1).creator == Actor.agent("s-1")


def test_the_environment_is_made_on_first_use(app: App):
    from journal.repositories.environments import Environments
    app.console().run(["task", "create", "t"], Caller.user("other"))
    assert app.container.get(Tasks).find(1).environment_id == app.container.get(Environments).lookup("other").id


def test_bad_arguments_answer_with_usage_not_an_exit(app: App):
    outcome = app.console().run(["task", "nope"], MAIN)
    assert outcome.code == 2 and "usage: journal task" in outcome.error and "usage: journal [-h]" not in outcome.error, "the noun's own usage, once"
    helped = app.console().run(["plan", "--help"], MAIN)
    assert helped.code == 0 and "approve" in helped.text and "usage: journal [-h]" not in helped.text + helped.error, "a noun's help is its verbs, and no failure"


def test_the_server_runs_the_same_console_for_the_shim(app: App):
    import json
    from urllib.request import Request as HttpRequest, urlopen
    server = app.server()
    server.start()
    try:
        body = json.dumps({"argv": ["task", "create", "over http"], "env": "main", "session": "s-9"}).encode()
        with urlopen(HttpRequest(f"http://127.0.0.1:{server.port}/cli", data=body, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main"}), timeout=5) as reply:
            outcome = json.loads(reply.read())
    finally:
        server.stop()
    assert outcome["code"] == 0 and "task 1 open" in outcome["text"]
    assert app.container.get(Tasks).find(1).creator == Actor.agent("s-9")


def test_deleting_an_environment_takes_everything_recorded_in_it(app: App):
    from journal.repositories.environments import Environments
    from journal.repositories.tasks import Tasks
    app.console().run(["task", "create", "t"], Caller.user("spike"))
    app.console().run(["task", "create", "kept"], MAIN)
    outcome = app.console().run(["environment", "delete", "spike"], MAIN)
    assert "deleted environment" in outcome.text and outcome.code == 0
    assert [e.name for e in app.container.get(Environments).all()] == ["main"]
    with app.container.get(Scope).environment(1):
        assert [t.title for t in app.container.get(Tasks).all()] == ["kept"]
    assert app.console().run(["environment", "delete", "spike"], MAIN).code == 1


def test_a_command_from_the_agents_shell_is_the_live_agents_wherever_it_came_from(app: App):
    from journal.support.caller import Caller
    from journal.repositories.reactions import Reactions
    from journal.support.actor import Actor
    from journal.models.agent import Agent
    from journal.repositories.agents import Agents
    app.container.get(Agents).save(Agent(session="s1", environment_id=1, provider="claude"), Actor.system())
    app.console().run(["message", "send", "hi"], Caller.user("main"))
    app.console().run(["message", "react", "1", "👍"], Providers().caller({"CLAUDECODE": "1"}))
    assert Providers().caller({"JOURNAL_AGENT_SHELL": "1"}).is_unnamed_agent(), "a worker's shell is an agent's whatever its program marks"
    named = Providers().caller({"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "abc"})
    assert named.session == "abc" and named.provider == "claude", "a Claude Code shell names its own session, so its lines and outputs are its agent's"
    with app.container.get(Scope).environment(1):
        assert app.container.get(Reactions).all()[-1].creator.actor_type == "agent"


def test_a_shells_variables_name_its_caller_by_kind_with_the_provider_that_marks_it():
    from journal.support.caller_variables import CallerVariables
    providers = Providers()
    assert providers.caller({"JOURNAL_PLUGIN": ""}) == Caller.user("main") and Caller.user("main").actor == Actor.user(1), "a shell nothing marks is the user's, and a variable set empty is no plugin"
    assert providers.caller({"CODEX_THREAD_ID": "t1", "CODEX_CI": "1"}) == Caller.agent("main", "t1", "codex"), "an agent knows its own provider from the markers its shell carries"
    assert providers.caller({"CLAUDECODE": "1"}) == Caller.shell("main", "claude"), "a Claude shell names no session, only its provider"
    assert providers.caller({"JOURNAL_PLUGIN": "echo", "JOURNAL_PLUGIN_TOKEN": "x"}) == Caller.plugin("main", "echo")
    assert providers.caller({"JOURNAL_ACTOR": "worker:3", "JOURNAL_AGENT_SHELL": "1", "CLAUDECODE": "1"}) == Caller.worker("main", 3, None, "claude")
    assert providers.caller({"JOURNAL_ACTOR": "verifier:4", "JOURNAL_AGENT_SHELL": "1", "CLAUDECODE": "1"}) == Caller.verifier("main", 4, None, "claude"), "one actor variable names a worker or a verifier by its stamp"
    variables = providers.caller_variables({"JOURNAL_ENV": "development", "CODEX_THREAD_ID": "t1", "JOURNAL_LAUNCH": "l1"})
    assert CallerVariables.parsed(variables.body(), "claude") == variables, "what the shim posts reads back as the variables it posted"


def test_a_codex_agent_with_no_row_yet_dispatches_a_codex_worker_and_raises_its_events(app: App, monkeypatch):
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.repositories.workers import Workers
    monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: None)
    codex = Caller.agent("main", "t9", "codex")
    assert dispatched(app.console(), ["Ada Lovelace", "write storage.py", "--changes", "the files of its task", "--profile", "journal-medior", "--model", "gpt-5"], codex).code == 0
    assert app.container.get(Workers).find(1).provider == "codex", "the provider comes with the caller, not from the agent's row"
    assert app.console().run(["stuck", "the build is red"], MAIN).code == 1, "only an agent says it is stuck"


def test_a_command_from_an_agents_shell_with_no_agent_live_is_the_users_own(app: App):
    from journal.support.caller import Caller
    from journal.repositories.reactions import Reactions
    app.console().run(["message", "send", "hi"], Caller.user("main"))
    assert app.console().run(["message", "react", "1", "👍"], Providers().caller({"CLAUDECODE": "1"})).code == 0
    with app.container.get(Scope).environment(1):
        assert app.container.get(Reactions).all()[-1].creator.actor_type == "user", "a shell outside the journal is the user's"


def test_a_codex_command_orients_its_own_session_in_the_chosen_environment(app: App):
    from journal.models.agent import Agent
    from journal.repositories.agents import Agents
    from journal.repositories.environments import Environments
    environments, agents = app.container.get(Environments), app.container.get(Agents)
    development = environments.lookup("development")
    with app.container.get(Scope).environment(development.id):
        agents.save(Agent(session="codex-session", environment_id=development.id, provider="codex", is_overview_read=False), Actor.system())
        agents.save(Agent(session="claude-session", environment_id=development.id, provider="claude", is_overview_read=False), Actor.system())
    caller = Providers().caller({"JOURNAL_ENV": "development", "CODEX_THREAD_ID": "codex-session", "CODEX_CI": "1"})
    assert app.console().run(["environment", "overview"], caller).code == 0
    with app.container.get(Scope).environment(development.id):
        assert agents.session_agent("codex-session").is_overview_read
        assert not agents.session_agent("claude-session").is_overview_read
    assert app.console().run(["task", "create", "Codex task"], caller).code == 0
    with app.container.get(Scope).environment(development.id):
        assert app.container.get(Tasks).all()[-1].creator == Actor.agent("codex-session")
    assert Providers().caller({"JOURNAL_SESSION": "worker-session", "CODEX_THREAD_ID": "parent-session"}).session == "worker-session"


def test_a_workers_shim_never_runs_the_package_when_no_server_answers(app: App):
    import os
    import subprocess
    environ = {key: value for key, value in os.environ.items() if key != "JOURNAL_SESSION"}
    environ.update(JOURNAL_ROOT=str(app.config.root), JOURNAL_ENV="main", JOURNAL_ACTOR="worker:1", JOURNAL_ACTOR_TOKEN="tok")
    (app.config.home / "port").unlink(missing_ok=True)
    outcome = subprocess.run(["sh", str(Path(__file__).resolve().parents[1] / "src" / "journal.sh"), "task", "list"], env=environ, capture_output=True, text=True, timeout=10)
    assert outcome.returncode == 1 and "restarting" in outcome.stderr, "a worker's command waits for the server that can check its token"


@pytest.mark.parametrize("online", [False, True])
def test_the_shim_attributes_a_codex_command_with_and_without_a_server(app: App, online):
    import os
    import subprocess
    from journal.models.agent import Agent
    from journal.providers.claude import Claude
    from journal.repositories.agents import Agents
    from journal.repositories.environments import Environments
    agents = app.container.get(Agents)
    development = app.container.get(Environments).lookup("development")
    with app.container.get(Scope).environment(development.id):
        agents.save(Agent(session="codex-session", environment_id=development.id, provider="codex", is_overview_read=False), Actor.system())
    environ = {key: value for key, value in os.environ.items() if key not in ("JOURNAL_SESSION", "CODEX_SANDBOX", *Claude.inherited_markers)}
    environ.update(JOURNAL_ROOT=str(app.config.root), JOURNAL_ENV="development", JOURNAL_PORT="0", CODEX_THREAD_ID="codex-session", CODEX_CI="1")
    server = app.server()
    if online:
        server.start()
    try:
        outcome = subprocess.run(["sh", str(Path(__file__).resolve().parents[1] / "src" / "journal.sh"), "environment", "overview"], env=environ, capture_output=True, text=True, timeout=10)
        assert outcome.returncode == 0, outcome.stderr
        with app.container.get(Scope).environment(development.id):
            assert agents.session_agent("codex-session").is_overview_read
    finally:
        server.stop()


def test_the_boot_menu_is_offered_only_a_session_whose_conversation_still_exists(app: App, monkeypatch, tmp_path):
    from journal.support.caller import Caller
    from journal.support.actor import Actor
    from journal.models.agent import Agent
    from journal.providers.claude import Claude
    from journal.repositories.agents import Agents
    stored = tmp_path / "s1.jsonl"
    stored.write_text("{}\n")
    monkeypatch.setattr(Claude, "transcript", lambda self, project, session: stored if session == "s1" else None)
    agents = app.container.get(Agents)
    agents.save(Agent(session="s1", environment_id=1, provider="claude"), Actor.system())
    agents.save(Agent(session="lost", environment_id=1, provider="claude", state="ended"), Actor.system())
    import json as j
    rows = j.loads(app.console().run(["environment", "json"], Caller.user("main")).text)
    assert rows[0]["last_sessions"] == {"claude": "s1"}, "a codex launch finds no Claude session to carry on"


def test_the_boot_menu_never_carries_on_from_a_workers_conversation(app: App, monkeypatch, tmp_path):
    from journal.support.caller import Caller
    from journal.support.actor import Actor
    from journal.models.agent import Agent
    from journal.support.agent_role import AgentRole
    from journal.providers.claude import Claude
    from journal.repositories.agents import Agents
    stored = tmp_path / "kept.jsonl"
    stored.write_text("{}\n")
    monkeypatch.setattr(Claude, "transcript", lambda self, project, session: stored)
    agents = app.container.get(Agents)
    agents.save(Agent(session="main-session", environment_id=1, provider="claude", state="ended"), Actor.system())
    agents.save(Agent(session="worker-session", environment_id=1, provider="claude", role=AgentRole.WORKER), Actor.system())
    import json as j
    rows = j.loads(app.console().run(["environment", "json"], Caller.user("main")).text)
    assert rows[0]["last_sessions"] == {"claude": "main-session"}, "the newest conversation is a worker's: the main agent carries on from its own"
    assert not rows[0]["working"], "a worker at work is not the environment's agent working"


def test_an_environment_is_renamed_with_everything_in_it_and_never_while_an_agent_works_there(app: App):
    from journal.models.agent import Agent
    from journal.repositories.agents import Agents
    from journal.repositories.environments import Environments
    from journal.repositories.tasks import Tasks
    console, environments = app.console(), app.container.get(Environments)
    assert console.run(["environment", "create", "spike"], MAIN).code == 0
    spike = environments.lookup("spike")
    with app.container.get(Scope).environment(spike.id):
        app.container.get(Tasks).save(Task(title="in spike"), Actor.user(1))
    claimed = console.run(["environment", "rename", "spike", "main"], MAIN)
    assert claimed.code == 1 and "exists already" in claimed.error
    with app.container.get(Scope).environment(spike.id):
        app.container.get(Agents).save(Agent(session="s-spike", environment_id=spike.id, provider="claude", state="idle"), Actor.system())
    busy = console.run(["environment", "rename", "spike", "probe"], MAIN)
    assert busy.code == 1 and "an agent works in spike" in busy.error
    with app.container.get(Scope).environment(spike.id):
        app.container.get(Agents).save(app.container.get(Agents).session_agent("s-spike").with_(state="ended"), Actor.system())
    assert console.run(["environment", "rename", "spike", "probe"], MAIN).code == 0
    with app.container.get(Scope).environment(environments.lookup("probe").id):
        assert [t.title for t in app.container.get(Tasks).all()] == ["in spike"], "its rows go with it"
    assert not environments.matching(name="spike")


def test_any_row_docks_above_the_chat_by_noun_and_number_in_either_order(app: App):
    from journal.repositories.messages import Messages
    app.runtime().boot()
    console = app.console()
    console.run(["task", "create", "write the notes", "--brief", "what and where\nand how"], MAIN)
    docked = console.run(["task", "12", "dock"], MAIN)
    assert docked.code == 1 and "12" in docked.error, "the number in the verb's place turns the line around, and the row it names is looked for"
    assert console.run(["task", "1", "dock"], MAIN).text.startswith("Task 1: write the notes docked above the chat")
    with app.container.get(Scope).environment(1):
        messages = app.container.get(Messages)
        [card] = [m for m in messages.all() if m.data.get("docked")]
        assert card.author.value == "system" and card.text == "Task 1: write the notes"
        assert card.data["kind"] == "docked" and card.data["row"] == "tasks:1" and card.data["key"] == "made:task:1"
        assert card.data["heading"] == "Task 1: write the notes" and card.data["summary"] == "what and where"
        assert card.data["dock"] == {"buttons": [{"label": "Open", "act": "open"}, {"label": "Close", "act": "close"}], "folds": True}
        assert console.run(["task", "dock", "1"], MAIN).code == 0 and len([m for m in messages.all() if m.data.get("docked")]) == 1, "docking it again keeps the one card"
        assert console.run(["task", "undock", "1"], MAIN).text.startswith("Task 1: write the notes undocked")
        assert messages.find(card.id).data["docked"] is False
        assert "is not docked" in console.run(["task", "1", "undock"], MAIN).error
    assert "dock" in console.run(["report", "--help"], MAIN).text and "dock" not in console.run(["search", "--help"], MAIN).text, "every row noun has the verbs, a noun that is no row has not"


def test_a_workers_environment_carries_no_providers_markers_no_session_and_no_launch(app: App, monkeypatch):
    from journal.providers.support.helper_setup import HelperSetup
    parents = {*Providers().inherited_markers(), *Providers().session_variables(), "JOURNAL_LAUNCH", "JOURNAL_SESSION"}
    for name in parents:
        monkeypatch.setenv(name, "parent")
    from journal.support.agent_token import AgentToken
    handed = app.container.get(HelperSetup).variables("main", Actor.worker(7), AgentToken("tok"))
    assert not parents & set(handed), "a worker carries none of the parent's thread, and never its session, which its report would take as its own"
    assert (handed["JOURNAL_ACTOR"], handed["JOURNAL_ACTOR_TOKEN"], handed["JOURNAL_ENV"]) == ("worker:7", "tok", "main")
    assert app.container.get(HelperSetup).variables("main", Actor.verifier(3), AgentToken("tok"))["JOURNAL_ACTOR"] == "verifier:3", "a verifier's shell names it as a verifier, never a worker"


def test_a_worktree_launch_takes_name_2_beside_a_live_session_and_reuses_a_crashed_ones_name(app: App, monkeypatch):
    import json
    import os
    import subprocess
    from journal.launcher.launch import Launch
    from journal.launcher.menu import Menu
    from journal.models.agent import Agent
    from journal.providers.support.status_line import StatusLine
    from journal.repositories.agents import Agents
    from journal.repositories.environments import Environments
    root = app.config.root
    for argv in (["init", "-q", "-b", "main"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "start"]):
        subprocess.run(["git", *argv], cwd=root, capture_output=True, timeout=30)
    monkeypatch.setattr(Menu, "journal", lambda self, *argv: app.console().run(list(argv), Caller.user("main")).text)
    gone = subprocess.Popen(["true"])
    gone.wait(10)
    launches = app.config.home / "runtime" / "launches"
    launches.mkdir(parents=True, exist_ok=True)
    for name, owner in (("alpha", os.getpid()), ("beta", gone.pid)):
        app.console().run(["environment", "create", name], Caller.user("main"))
        environment = app.container.get(Environments).existing(name)
        app.container.get(Agents).save(Agent(environment_id=environment.row_id, session=f"s-{name}", provider="claude", state="idle"), Actor.system())
        (launches / f"{name}.json").write_text(json.dumps({"launch": f"launch-{name}", "owner": owner}))
    live = Launch.parse(["claude", "--worktree", "alpha"], root)
    choice = live.choice()
    folder = live.chosen(choice).launch_file(choice, StatusLine(root))["front"]["folder"]
    assert choice.environment == "alpha-2" and folder == str(root / ".claude" / "worktrees" / "alpha-2"), "a live session holds alpha, so the launch takes alpha-2 with a worktree of its own"
    crashed = Launch.parse(["claude", "--worktree", "beta"], root)
    assert crashed.choice().environment == "beta", "a crashed session, its launcher gone, holds nothing, so its name is taken again"


def test_every_worktree_failure_at_launch_is_one_plain_line_naming_its_cause_and_what_to_do(app: App, monkeypatch, capsys, tmp_path):
    import os
    import subprocess
    from journal.launcher.launch import Launch
    from journal.launcher.menu import Menu
    from journal.support.worktree import Worktree
    from journal.support.worktree_failure import WorktreeFailure
    root = app.config.root
    git = lambda *argv, cwd=root: subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, timeout=30)
    monkeypatch.setattr(Menu, "journal", lambda self, *argv: app.console().run(list(argv), Caller.user("main")).text)

    def launched(name: str) -> str:
        code = Launch.parse(["claude", "--worktree", name], root).run()
        error = capsys.readouterr().err.strip()
        assert code == 1 and len(error.splitlines()) == 1 and "Traceback" not in error, error
        return error

    assert "is neither a git repository nor a folder holding git repositories" in launched("no-git") and "git init" in launched("no-git"), "a folder with no git says so, and what to do"
    git("init", "-q", "-b", "main")
    assert "has no commit yet" in launched("no-commit"), "a repository with no commit says so"
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "start")
    git("checkout", "-q", "-b", "worktree-taken")
    assert "is checked out in another folder" in launched("taken"), "a branch checked out elsewhere says so, and what to do"
    git("checkout", "-q", "main")
    stand_ins = tmp_path / "slow-git"
    stand_ins.mkdir()
    (stand_ins / "git").write_text("#!/bin/sh\nexec sleep 5\n")
    (stand_ins / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{stand_ins}:{os.environ['PATH']}")
    try:
        Worktree(root, "slow", git_seconds=0.5).created()
        raise AssertionError("a git that never answers fails the launch")
    except WorktreeFailure as failed:
        assert "git gave no answer within 0.5 seconds" in str(failed) and len(str(failed).splitlines()) == 1, "and a git that hangs is cut off with one line"


def test_a_worktree_reads_the_journals_hooks_through_one_link_and_its_git_status_stays_clean(app: App, monkeypatch):
    import json
    import subprocess
    from journal.launcher.launch import Launch
    from journal.launcher.menu import Menu
    from journal.providers.support.status_line import StatusLine
    from journal.support.choice import Choice
    root = app.config.root
    git = lambda *argv, cwd=root: subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, timeout=30)
    (root / ".claude").mkdir(exist_ok=True)
    tracked = root / ".claude" / "settings.json"
    tracked.write_text('{"permissions": {}}\n')
    for argv in (["init", "-q", "-b", "main"], ["add", ".claude/settings.json"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "start"]):
        git(*argv)
    monkeypatch.setattr(Menu, "journal", lambda self, *argv: app.console().run(list(argv), Caller.user("main")).text)
    main_settings = tracked.read_text()
    folder = Path(Launch.parse(["claude", "--worktree", "calm-river"], root).launch_file(Choice("calm-river"), StatusLine(root))["front"]["folder"])
    local = folder / ".claude" / "settings.local.json"
    written = json.loads(local.read_text())
    assert local.is_symlink() and local.resolve() == (app.config.home / "runtime" / "worktree-settings" / "claude.json").resolve(), "the worktree reads the journal's hooks through a link to one file the main checkout's journal writes"
    assert str(root) in json.dumps(written["hooks"]) and written["statusLine"]["command"], "naming the main root, with the status line"
    assert git("status", "--porcelain", cwd=folder).stdout == "", "the worktree's git status stays clean"
    assert tracked.read_text() == main_settings and (folder / ".claude" / "settings.json").read_text() == main_settings, "and no settings file of the project is written, in the worktree or in the main checkout"


def test_a_launch_marks_a_new_worktree_trusted_in_claude_codes_state_and_never_the_persons_own(app: App, monkeypatch, tmp_path):
    import json
    import os
    import subprocess
    from journal.launcher.launch import Launch
    from journal.launcher.menu import Menu
    from journal.providers.support.status_line import StatusLine
    from journal.support.choice import Choice
    real = Path.home() / ".claude.json"
    real_time = real.stat().st_mtime_ns if real.exists() else 0
    root = app.config.root
    for argv in (["init", "-q", "-b", "main"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "start"]):
        subprocess.run(["git", *argv], cwd=root, capture_output=True, timeout=30)
    monkeypatch.setattr(Menu, "journal", lambda self, *argv: app.console().run(list(argv), Caller.user("main")).text)
    state = Path(os.environ["CLAUDE_CONFIG_DIR"]) / ".claude.json"
    state.write_text(json.dumps({"projects": {str(root): {"hasTrustDialogAccepted": True, "allowedTools": ["Bash"]}}}))
    folder = Launch.parse(["claude", "--worktree", "calm-river"], root).launch_file(Choice("calm-river"), StatusLine(root))["front"]["folder"]
    projects = json.loads(state.read_text())["projects"]
    assert projects[folder]["hasTrustDialogAccepted"] and projects[str(root)]["allowedTools"] == ["Bash"], "the new worktree is marked trusted in Claude Code's state, the rest of it kept"
    assert (real.stat().st_mtime_ns if real.exists() else 0) == real_time, "and the person's own state file is never touched by a test"


def test_codex_in_a_new_worktree_runs_the_main_checkouts_hooks_trusted_without_a_new_trust_step(app: App, monkeypatch, tmp_path):
    import json
    import subprocess
    import tomllib
    from journal.launcher.launch import Launch
    from journal.launcher.menu import Menu
    from journal.providers.codex import Codex
    from journal.providers.support.status_line import StatusLine
    from journal.support.choice import Choice
    root = app.config.root
    for argv in (["init", "-q", "-b", "main"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "start"]):
        subprocess.run(["git", *argv], cwd=root, capture_output=True, timeout=30)
    monkeypatch.setattr(Menu, "journal", lambda self, *argv: app.console().run(list(argv), Caller.user("main")).text)
    home = tmp_path / "codex-home"
    home.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(home))
    main_hooks = root.resolve() / ".codex" / "hooks.json"
    (home / "config.toml").write_text("".join(f'[hooks.state."{main_hooks}:{type_name}:0:0"]\ntrusted_hash = "x"\n\n' for type_name in ("session_start", "stop")))
    folder = Path(Launch.parse(["codex", "--worktree", "calm-river"], root).launch_file(Choice("calm-river"), StatusLine(root))["front"]["folder"])
    hooks = folder / ".codex" / "hooks.json"
    assert hooks.is_symlink() and hooks.resolve() == main_hooks and str(root) in hooks.read_text(), "the worktree reads the main checkout's hooks, naming the main root"
    assert Codex.trusted_kinds(folder.resolve() / ".codex" / "hooks.json") == {"session_start", "stop"}, "and Codex trusts them at the worktree's path as it trusts them in the main checkout"
    assert tomllib.loads((home / "config.toml").read_text())["hooks"]["state"][f"{main_hooks}:stop:0:0"]["trusted_hash"] == "x", "the main checkout's trust kept"


def test_two_worktree_launches_run_side_by_side_each_with_its_own_environment_and_agent(app: App, monkeypatch):
    import json
    import subprocess
    from urllib.request import Request as HttpRequest, urlopen
    from journal.launcher.launch import Launch
    from journal.launcher.menu import Menu
    from journal.providers.support.status_line import StatusLine
    from journal.repositories.agents import Agents
    from journal.repositories.environments import Environments
    root = app.config.root
    for argv in (["init", "-q", "-b", "main"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "start"]):
        subprocess.run(["git", *argv], cwd=root, capture_output=True, timeout=30)
    monkeypatch.setattr(Menu, "journal", lambda self, *argv: app.console().run(list(argv), Caller.user("main")).text)
    launches = app.config.home / "runtime" / "launches"
    launches.mkdir(parents=True, exist_ok=True)
    folders = {}
    for name in ("alpha", "beta"):
        launch = Launch.parse(["claude", "--worktree", name], root)
        choice = launch.choice()
        written = launch.launch_file(choice, StatusLine(root))
        assert choice.environment == name, "a worktree launch works the environment named after it"
        folders[name] = written["front"]["folder"]
        (launches / f"{name}.json").write_text(json.dumps({"launch": written["launch"]}))
    assert folders == {name: str(root / ".claude" / "worktrees" / name) for name in ("alpha", "beta")} and all(Path(folder).is_dir() for folder in folders.values()), "each runs in a worktree of its own"
    import re
    bare = Launch.parse(["claude", "--worktree"], root).choice().environment
    assert re.fullmatch(r"[a-z]+-[a-z]+", bare) and bare not in ("alpha", "beta"), "a bare --worktree's made-up name is the environment the menu starts"
    app.runtime().start()
    try:
        for name in ("alpha", "beta"):
            launch_id = json.loads((launches / f"{name}.json").read_text())["launch"]
            body = json.dumps({"hook_event_name": "SessionStart", "session_id": f"s-{name}", "source": "startup"}).encode()
            urlopen(HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=body, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": name, "X-Journal-Launch": launch_id}), timeout=5).read()
        agents, environments = app.container.get(Agents), app.container.get(Environments)
        alpha, beta = agents.session_agent("s-alpha"), agents.session_agent("s-beta")
        assert alpha.environment_id == environments.lookup("alpha").row_id and beta.environment_id == environments.lookup("beta").row_id, "each launch's agent is its own environment's"
        assert alpha.state != "ended" and beta.state != "ended", "and the second never ends the first"
    finally:
        app.runtime().stop()


def test_a_hook_whose_launch_id_names_another_environments_launch_is_reported_and_registers_no_agent(app: App):
    import json
    from urllib.request import Request as HttpRequest, urlopen
    from journal.repositories.agents import Agents
    from journal.repositories.entries import Entries
    from journal.repositories.messages import Messages
    launches = app.config.home / "runtime" / "launches"
    launches.mkdir(parents=True, exist_ok=True)
    (launches / "main.json").write_text(json.dumps({"launch": "launch-main"}))
    (launches / "spike.json").write_text(json.dumps({"launch": "launch-spike"}))
    app.runtime().start()
    try:
        def started(session: str, launch: str) -> int:
            body = json.dumps({"hook_event_name": "SessionStart", "session_id": session, "source": "startup"}).encode()
            request = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=body, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Launch": launch})
            with urlopen(request, timeout=5) as reply:
                return reply.status

        assert started("stray", "launch-spike") == 200 and started("bare", "") == 200, "a session without the launch id is let through, never refused"
        agents = app.container.get(Agents)
        assert not [agent for agent in agents.all_agents() if agent.session in ("stray", "bare")], "and never taken as the environment's agent"
        with app.container.get(Scope).environment(1):
            assert {entry.data["session_id"] for entry in app.container.get(Entries).kind_entries("unbound_session")} == {"stray", "bare"}, "its hooks are recorded"
            assert any("could not match to this project" in message.text for message in app.container.get(Messages).all()), "and it is reported in the chat"
        assert started("bound", "launch-main") == 200 and agents.session_agent("bound").environment_id == 1
        from journal.support.agent_role import AgentRole
        from journal.models.worker import Worker
        from journal.repositories.workers import Workers
        from journal.support.actor import Actor
        from journal.support.agent_token import AgentToken
        with app.container.get(Scope).environment(1):
            worker = app.container.get(Workers).save(Worker(environment_id=1, name="Mr. Babbage", brief="b", token_hash=AgentToken.hashed("tok")), Actor.system())

        def worker_started(session: str, token: str) -> int:
            body = json.dumps({"hook_event_name": "SessionStart", "session_id": session, "source": "startup"}).encode()
            request = HttpRequest(f"http://127.0.0.1:{app.server().port}/hooks/claude", data=body, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main", "X-Journal-Actor": f"worker:{worker.id}", "X-Journal-Actor-Token": token})
            with urlopen(request, timeout=5) as reply:
                return reply.status

        assert worker_started("w-forged", "nope") == 200 and not [a for a in agents.all_agents() if a.session == "w-forged"], "a wrong token is no worker's: its hooks are unbound"
        assert worker_started("w-real", "tok") == 200 and agents.session_agent("w-real").role == AgentRole.WORKER, "a worker's token stands in for the launch id, and its agent row is a worker's"
        with app.container.get(Scope).environment(1):
            assert app.container.get(Workers).find(worker.id).session == "w-real", "and its first hook binds the session its row did not name"
    finally:
        app.runtime().stop()


def test_a_helper_runs_only_the_verbs_its_file_names(app: App):
    from journal.support.agent_role import AgentRole
    console, worker, agent = app.console(), Caller.worker("main", 1, "w1", "claude"), Caller.agent("main", "s1", "claude")
    refused = console.run(["panic", "pop"], worker)
    assert refused.code == 1 and refused.error.startswith("a worker may not run journal panic apply: WorkerHelper names the verbs it runs, ") and "journal memory list" in refused.error and "journal rule read" in refused.error, "a verb its file does not name is refused, naming the file and the verbs it runs"
    assert agent.subagent_caller().role == AgentRole.SUBAGENT and console.run(["panic", "pop"], agent.subagent_caller()).error.startswith("a subagent may not run journal panic apply: ResearcherHelper")
    assert console.run(["task", "show", "1"], worker).error.find("may not run") == -1 and console.run(["task", "complete", "1"], worker).error.startswith("a worker may not run journal task complete"), "a worker whose file names task show runs it and is refused task complete"
    assert console.run(["memory", "list"], worker).code == 0 and console.run(["rule", "strike", "1"], worker).code == 1, "a named verb runs, and its neighbour stays refused"
    assert console.run(["memory", "add", "the port is 9"], agent).code == 0 and console.run(["task", "list"], MAIN).code == 0 and console.run(["task", "create", "x"], worker).code == 1, "the main agent and the user run every verb"


def test_help_shows_a_worker_only_the_verbs_its_kind_may_run(app: App):
    console, worker = app.console(), Caller.worker("main", 1, "w1", "claude")
    nouns = console.run(["-h"], worker)
    shown = nouns.text + nouns.error
    listed_nouns = shown.split("{")[1].split("}")[0].split(",")
    assert "task" in listed_nouns and "worker" in listed_nouns and "message" not in listed_nouns and "panic" not in listed_nouns, "journal -h lists only the nouns a worker may use"
    verbs = console.run(["task", "-h"], worker)
    listed = verbs.text + verbs.error
    assert "show" in listed and "log" in listed and "create" not in listed and "complete" not in listed, "journal task -h lists only its verbs"
    usage = console.run(["task"], worker)
    assert usage.code != 0 and "{log,show}" in usage.text + usage.error and "create" not in usage.text + usage.error, "and so does a usage error"
    full = console.run(["task", "-h"], MAIN)
    assert "create" in full.text + full.error and "complete" in full.text + full.error, "the user sees every verb as before"


def test_the_help_of_a_noun_with_a_default_verb_lists_every_verb(app: App):
    shown = app.console().run(["setup", "--help"], MAIN)
    assert "restart" in shown.text + shown.error and "project" in shown.text + shown.error, "setup --help names every verb, its default among them"


def test_a_command_the_server_fails_on_prints_the_fault_and_exits_non_zero(app: App, tmp_path):
    import os
    import subprocess
    from journal.providers.claude import Claude
    environ = {key: value for key, value in os.environ.items() if key not in ("JOURNAL_SESSION", "CODEX_SANDBOX", *Claude.inherited_markers)}
    environ.update(JOURNAL_ROOT=str(app.config.root), JOURNAL_ENV="main", JOURNAL_PORT="0")
    server = app.server()
    server.start()
    try:
        missing = tmp_path / "gone.md"
        outcome = subprocess.run(["sh", str(Path(__file__).resolve().parents[1] / "src" / "journal.sh"), "doc", "create", "Notes", "--abstract", "The notes", "--file", str(missing)], env=environ, capture_output=True, text=True, timeout=10)
        assert outcome.returncode == 1 and "gone.md" in outcome.stderr, "a fault is printed with what it names, never a silent success"
    finally:
        server.stop()


def test_remote_github_init_writes_the_server_workflow_once_and_says_how_to_register_the_runner(tmp_path, capsys):
    from journal.launcher.remote_github import RUNNER_LABEL, WORKFLOW, RemoteGithub
    from journal.version import VERSION
    root = tmp_path / "shop"
    root.mkdir()
    assert RemoteGithub.parsed(["init"], root).run() == 0
    workflow = (root / WORKFLOW).read_text()
    assert f"runs-on: [self-hosted, {RUNNER_LABEL}]" in workflow and "workflow_dispatch:" in workflow
    assert 'default: "shop"' in workflow and f'default: "{VERSION}"' in workflow
    assert "TEAM_PROJECT: ${{ inputs.project }}" in workflow and "TEAM_ADDRESS: ${{ inputs.address }}" in workflow
    assert 'curl -fsSL "https://github.com/jessegall/agent-journal/releases/download/v${TEAM_VERSION}/install.sh" | sh' in workflow
    told = capsys.readouterr().out
    assert "--labels agent-journal" in told and "journal team join <url>" in told
    assert RemoteGithub.parsed(["init"], root).run() == 1, "a workflow already there is not written over"
    assert RemoteGithub.parsed(["init", "--replace"], root).run() == 0


def test_a_team_url_is_its_address_or_an_invitation():
    from journal.sync.team_url import TeamUrl
    assert TeamUrl.parse("https://team.example/?setup=ABCD-EFGH").address == "https://team.example", "a bare address claims a server with no code"
    assert TeamUrl.parse("https://team.example/join?code=X&fingerprint=Y").is_invitation()
    assert TeamUrl.parse("https://203.0.113.5.").address == "https://203.0.113.5", "a sentence's full stop is no part of the address"
    assert TeamUrl.parse("203.0.113.5").address == "https://203.0.113.5", "a bare IP is reached over HTTPS"
    assert TeamUrl.parse("https://team.example/").address == "https://team.example"
    assert TeamUrl.parse("https://team.example.com:8443").has_self_signed_certificate() and TeamUrl.parse("https://203.0.113.5").has_self_signed_certificate()
    assert not TeamUrl.parse("https://team.example.com").has_self_signed_certificate(), "a domain on 443 has a public certificate"


def test_the_library_link_publishes_an_item_with_its_file_and_reads_it_back_from_a_team_server(app: App, tmp_path: Path):
    import hashlib
    import json
    from journal.db.schema import Schema
    from journal.features.library.support.library_link import LibraryLink
    from journal.sync.team_account import TEAM_FILE, TeamAccount
    from sync_server.item_query import ItemQuery
    from sync_server.publish_request import PublishRequest
    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path / "team")
    team.accounts.create("ada@example.com", "Ada", "correct horse battery", "admin", 1.0)
    _, token = team.devices.login("ada@example.com", "correct horse battery", "laptop", "127.0.0.1", 1.0)
    server = team.started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"
    (app.config.home / TEAM_FILE).write_text(json.dumps({"address": address, "token": token}))
    link = LibraryLink(TeamAccount(app.config), app.container.get(Schema))
    try:
        assert link.summary(address).has_admin
        data = b"# Release"
        version = link.publish("skill", "release", PublishRequest("Releasing", json.dumps({"files": {"SKILL.md": hashlib.sha256(data).hexdigest()}}), "first"))
        assert not version.is_complete() and link.put_file("skill", "release", version.number, "SKILL.md", data).is_complete()
        [entry] = link.items(ItemQuery("skill", None)).items
        assert entry.item.name == "release" and link.version("skill", "release", 1).note == "first" and link.file("skill", "release", 1, "SKILL.md") == data
        assert link.withdraw("skill", "release").withdrawn_at > 0 and link.items(ItemQuery(None, None)).items == []
    finally:
        team.close(server)


def test_a_journal_connects_to_a_library_sees_its_status_and_disconnects(app: App, tmp_path: Path):
    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path / "team")
    server = team.started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"
    console, user = app.console(), Caller.user("main")
    try:
        assert "run this line yourself" in console.run(["library", "connect", address, "--email", "ada@example.com"], user).error, "no password, no connection"
        connected = console.run(["library", "connect", address, "--email", "ada@example.com", "--name", "Ada", "--password", "correct horse battery"], user)
        assert connected.code == 0 and "as Ada, admin" in connected.text, connected.error
        key = team.details.answer().key
        assert (app.config.home / "libraries" / f"{key}.json").is_file(), "the connection is kept by the library's key"
        assert f"library {address}, as Ada (admin)" in console.run(["library", "status"], user).text
        assert console.run(["library", "connect", address, "--email", "ada@example.com", "--password", "x"], user).code != 0, "one library at a time"
        assert console.run(["library", "login", "--email", "ada@example.com", "--password", "correct horse battery"], user).code == 0, "a machine logs in again"
        assert "disconnected" in console.run(["library", "disconnect"], user).text
        assert "connected to no library" in console.run(["library", "status"], user).text
    finally:
        team.close(server)
