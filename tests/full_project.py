"""Builds tests/fixtures/full_project.db.gz, the database of a full project the route timing run measures against: every row is generated here from a fixed seed and a list of plain words, never copied from a real journal, since the repository is public. Built again, from the checkout's root, when the schema moves far enough that the saved file no longer boots: PYTHONPATH=src python3 -m tests.full_project"""
import gzip
import random
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

from journal.app import App
from journal.config import Config
from journal.features.voices.voices_options import VoicesOptions
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.features.workers.workers_options import WorkersOptions
from journal.models.author import Author
from journal.models.message import Message
from journal.models.setting import Setting
from journal.repositories.environments import Environments
from journal.repositories.messages import Messages
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.in_process import posted

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "full_project.db.gz"
SEED = 2992
WORDS = ("parser", "header", "footer", "login", "release", "report", "plan", "phase", "query", "index", "page", "list", "row", "table", "link", "worker",
         "branch", "commit", "test", "suite", "shard", "budget", "route", "hook", "entry", "message", "reply", "comment", "doc", "draft", "review", "check",
         "script", "build", "viewer", "panel", "button", "label", "notice", "chart", "count", "cache", "write", "read", "lock", "thread", "queue", "job",
         "timer", "clock", "file", "folder", "path", "name", "title", "brief", "goal", "step", "order", "field", "column", "value", "number", "text")
PLANS, PHASES, PLAN_TASKS, LOOSE_TASKS, FINISHED_TASKS, WORKERS = 30, 3, 8, 400, 150, 40
MESSAGES, TOOL_CALLS, DISPLAYS, COMMENTS, REACTIONS = 4000, 1200, 300, 400, 300
DOCS, REPORTS, ABOUT_REPORTS, CHECKS, FACTS, RULES, REMINDERS, QUESTIONS = 80, 60, 20, 25, 40, 30, 30, 20
SPARE_TASKS, SPARE_MESSAGES = 50, 100
MAIN = {"X-Journal-Env": "main"}
USER, AGENT = Caller.user("main"), Caller.agent("main", "s1", "claude")


def unpacked(root: Path) -> App:
    """The saved full project laid down as the journal under root, and booted."""
    config = Config(root, port=0)
    config.home.mkdir(parents=True, exist_ok=True)
    with gzip.open(FIXTURE, "rb") as packed:
        config.database.write_bytes(packed.read())
    app = App(config)
    app.runtime().start()
    return app


def phrase(words: random.Random, count: int) -> str:
    return " ".join(words.choice(WORDS) for _ in range(count))


def sentence(words: random.Random) -> str:
    return phrase(words, words.randint(6, 30)).capitalize() + "."


def number(text: str, noun: str) -> int:
    return int(re.search(rf"{noun} (\d+)", text)[1])


def booted(root: Path) -> App:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True, timeout=30)
    (root / ".gitignore").write_text(".journal/\n")
    subprocess.run(["git", "add", ".gitignore"], cwd=root, check=True, timeout=30)
    subprocess.run(["git", "-c", "user.email=fixture@example.com", "-c", "user.name=Fixture", "commit", "-qm", "start"], cwd=root, check=True, timeout=30)
    app = App(Config(root, port=0))
    settings = app.container.get(SettingRows)
    settings.save(Setting(environment_id=PROJECT, key=VoicesOptions.NAME.key, value="Ada"), Actor.system())
    for key in ("skills.session_start", "skills.after_compaction"):
        settings.set(key, [], Actor.user(1))
    app.runtime().start()
    for name in ("main", "spare"):
        app.container.get(Environments).lookup(name)
    return app


def hook(app: App, kind: str, **body) -> None:
    posted(app, "/hooks/claude", {"hook_event_name": kind, "session_id": "s1", **body}, MAIN)


def plans(app: App, words: random.Random) -> list[int]:
    console, tasks = app.console(), []
    for _ in range(PLANS):
        plan = number(console.run(["plan", "create", phrase(words, 4), "--brief", sentence(words)], USER).text, "plan")
        added = [number(console.run(["plan", "add", str(plan), phrase(words, 5), "--brief", sentence(words)], USER).text, "task") for _ in range(PLAN_TASKS)]
        for phase in range(1, PHASES + 1):
            console.run(["plan", "phase", str(plan), phrase(words, 3), "--when", sentence(words)], USER)
            console.run(["plan", "todos", str(plan), str(phase), *(str(task) for task in added[phase - 1::PHASES])], USER)
        tasks.extend(added)
    return tasks


def loose_tasks(app: App, words: random.Random) -> list[int]:
    console = app.console()
    tasks = [number(console.run(["task", "create", phrase(words, 5), "--brief", sentence(words)], AGENT).text, "task") for _ in range(LOOSE_TASKS)]
    for task in tasks[:FINISHED_TASKS]:
        posted(app, f"/journal/tasks/{task}/finish", {"how": sentence(words)}, MAIN)
    return tasks


def workers(app: App, words: random.Random) -> None:
    console, settings, limits = app.console(), app.container.get(SettingRows), (WorkersOptions.WORKER_LIMIT, WorkersOptions.PROFILE_LIMIT)
    for limit in limits:
        settings.set(limit.key, 0, Actor.user(1))
    for n in range(WORKERS):
        task = number(console.run(["task", "create", f"the job of worker {n + 1}", "--brief", sentence(words)], AGENT).text, "task")
        dispatch = console.run(["worker", "dispatch", f"Worker {n + 1}", "--task", str(task), "--changes", "the files of its task", "--tests", "Scoped tests", "--profile", "journal-medior", "--model", "sonnet"], AGENT)
        assert dispatch.code == 0, dispatch.error
    for limit in limits:
        settings.set(limit.key, limit.default, Actor.user(1))


def chat(app: App, words: random.Random) -> list[int]:
    messages = app.container.get(Messages)
    with app.container.get(Scope).environment(app.container.get(Environments).existing("main").row_id):
        saved = [messages.save(Message(author=Author.USER, text=sentence(words)) if n % 2 == 0 else Message(author=Author.AGENT, session="s1", text=sentence(words)), Actor.user(1) if n % 2 == 0 else Actor.agent("s1")) for n in range(MESSAGES)]
    return [message.row_id for message in saved]


def hooks(app: App, words: random.Random) -> None:
    hook(app, "SessionStart")
    for n in range(TOOL_CALLS):
        call = {"tool_name": "Read", "tool_input": {"file_path": f"src/{words.choice(WORDS)}.py"}, "tool_use_id": f"t-{n}"}
        hook(app, "PreToolUse", **call)
        hook(app, "PostToolUse", **call, tool_response="")
        app.runtime().deferred.drain()
    for _ in range(DISPLAYS):
        hook(app, "MessageDisplay", message=sentence(words))
    app.runtime().deferred.drain()


def writing(app: App, words: random.Random, plan_tasks: list[int]) -> None:
    for kind, count in (("docs", DOCS), ("reports", REPORTS)):
        for _ in range(count):
            posted(app, f"/journal/{kind}", {"title": phrase(words, 4), "body": "\n\n".join(sentence(words) for _ in range(12))}, MAIN)
    with tempfile.TemporaryDirectory() as folder:
        body = Path(folder) / "report.md"
        for n in range(ABOUT_REPORTS):
            body.write_text("\n\n".join(sentence(words) for _ in range(8)))
            app.console().run(["report", "create", phrase(words, 4), "--file", str(body), "--about", f"plans:{n % PLANS + 1}", f"tasks:{plan_tasks[n]}"], AGENT)


def memory(app: App, words: random.Random) -> None:
    for _ in range(CHECKS):
        posted(app, "/journal/checks", {"title": phrase(words, 3), "brief": sentence(words), "command": "true"}, MAIN)
    for kind, count in (("facts", FACTS), ("rules", RULES), ("reminders", REMINDERS), ("questions", QUESTIONS)):
        for _ in range(count):
            posted(app, f"/journal/{kind}", {"text": sentence(words)}, MAIN)


def remarks(app: App, words: random.Random, tasks: list[int], messages: list[int]) -> None:
    for n in range(COMMENTS):
        posted(app, "/journal/comments", {"on": f"tasks:{tasks[n % len(tasks)]}", "text": sentence(words)}, MAIN)
    for n in range(REACTIONS):
        posted(app, f"/journal/messages/{messages[n * 7 % len(messages)]}/react", {"emoji": words.choice(("👍", "👀", "✅"))}, MAIN)


def spare(app: App, words: random.Random) -> None:
    spare_env = {"X-Journal-Env": "spare"}
    for _ in range(SPARE_TASKS):
        posted(app, "/journal/tasks", {"title": phrase(words, 4)}, spare_env)
    for _ in range(SPARE_MESSAGES):
        posted(app, "/journal/messages", {"text": sentence(words)}, spare_env)


def saved(app: App) -> None:
    with tempfile.TemporaryDirectory() as folder:
        copy = Path(folder) / "journal.db"
        with sqlite3.connect(app.config.database) as live, sqlite3.connect(copy) as target:
            live.backup(target)
        with sqlite3.connect(copy) as target:
            target.execute("VACUUM")
        FIXTURE.parent.mkdir(parents=True, exist_ok=True)
        with gzip.GzipFile(FIXTURE, "wb", mtime=0) as packed:
            packed.write(copy.read_bytes())


def main() -> int:
    WorkerRunner.start = lambda self, worker, actor: None
    words = random.Random(SEED)
    with tempfile.TemporaryDirectory() as folder:
        app = booted(Path(folder))
        try:
            plan_tasks = plans(app, words)
            tasks = plan_tasks + loose_tasks(app, words)
            workers(app, words)
            messages = chat(app, words)
            hooks(app, words)
            writing(app, words, plan_tasks)
            memory(app, words)
            remarks(app, words, tasks, messages)
            spare(app, words)
            app.runtime().deferred.drain()
            saved(app)
        finally:
            app.runtime().stop()
    print(f"wrote {FIXTURE.relative_to(ROOT)}, {FIXTURE.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
