import os
import subprocess
import threading
from pathlib import Path
from types import SimpleNamespace

from journal.engine.agent_launcher import AgentLauncher
from journal.support.worktree import Worktree
from tests.shared_journal import SharedJournal
from tests.stories.conftest import story_booted
from tests.template_copy import copied


def test_story_reset_has_no_detached_plan_launch_left_to_write_skills(tmp_path, template_journal, monkeypatch):
    app = story_booted(copied(template_journal, tmp_path), monkeypatch)
    snapshot = SharedJournal(app)
    release, written = threading.Event(), []
    writers = []
    remove_directory = os.rmdir

    def launch_child(arguments, **options):
        worktree = Path(options["cwd"]) / ".claude" / "worktrees" / arguments[arguments.index("--env") + 1]

        def write_skills():
            if release.wait(5):
                Worktree.linked(worktree / ".claude/skills/journal-late", app.config.root / ".claude/skills/journal")
                written.append(threading.current_thread().name)

        thread = threading.Thread(target=write_skills, name="detached-plan-skill-writer")
        writers.append(thread)
        thread.start()
        return SimpleNamespace(pid=1)

    def remove_after_late_writer(path, *, dir_fd=None):
        if writers and str(path).endswith("skills"):
            release.set()
            for thread in writers:
                thread.join(5)
                assert not thread.is_alive(), "the gated child completed its skill write"
        return remove_directory(path, dir_fd=dir_fd)

    monkeypatch.setattr(subprocess, "Popen", launch_child)
    monkeypatch.setattr(os, "rmdir", remove_after_late_writer)
    launcher = app.container.get(AgentLauncher)
    try:
        for _ in range(2):
            launches = []
            worktrees = [app.config.root / ".claude/worktrees" / f"plan-{number}" for number in range(4)]
            for worktree in worktrees:
                (worktree / ".claude/skills").mkdir(parents=True, exist_ok=True)
                app.runtime().deferred.add(lambda worktree=worktree: launches.append(launcher.launched(
                    worktree.name, ["claude", "--env", worktree.name], worktree,
                )))
            app.runtime().deferred.drain()
            snapshot.reset()
            assert launches == [0] * len(worktrees), "every launch finishes in-process without a child or a deferred fault"
            assert not writers and not written, "story launches cannot leave a child writing beyond the drained queue"
            assert all(not worktree.exists() for worktree in worktrees), "reset removes the stopped writers' worktrees"
    finally:
        release.set()
        for thread in writers:
            thread.join(5)
        app.runtime().stop()
