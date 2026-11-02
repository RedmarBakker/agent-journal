from pathlib import Path

import pytest

from journal.features.shell.support.shell_request import ShellRequest
from journal.features.shell.support.shell_runner import ShellRunner
from journal.features.workers.support.test_run_result import TestRunResult
from journal.features.workers.support.test_turns import TestTurns
from journal.features.workers.workers_options import WorkersOptions
from journal.models.command_output import CommandOutput
from journal.models.test_turn import TestTurn
from journal.models.test_turn_state import TestTurnState
from journal.models.worker import Worker
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope
from journal.repositories.test_turns import TestTurns as TurnRows
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.user_settings import user_set


@pytest.fixture
def turn_scope(app):
    with app.container.get(Scope).environment(1):
        yield app.container.get(TestTurns), app.container.get(TurnRows), app.container.get(CommandOutputs)


def running_output(outputs, tmp_path, name):
    folder = tmp_path / name
    folder.mkdir()
    (folder / "parts").write_text("R\n")
    (folder / "0.out").write_text("running\n")
    return outputs.save(CommandOutput(chain=name, command="pytest -q", ran_in=str(tmp_path / "worktree"), folder=str(folder)), Actor.system())


def running_turn(rows, output):
    return rows.save(TestTurn(worker=1, folder=output.ran_in, command=output.command).started(output.creation_time.timestamp() - 1).backgrounded(output.row_id), Actor.system())


def test_an_ended_turns_deadline_leaves_a_later_run_in_the_same_worktree_running(turn_scope, tmp_path):
    turns, rows, outputs = turn_scope
    first_output = running_output(outputs, tmp_path, "first")
    first = running_turn(rows, first_output)
    rows.save(first.ended(), Actor.system())
    later_output = running_output(outputs, tmp_path, "later")
    later = running_turn(rows, later_output)

    turns.stopped(first)

    assert rows.find(later.id).state == TestTurnState.RUNNING
    assert not outputs.find(later_output.row_id).ended
    assert (Path(later_output.folder) / "0.out").read_text() == "running\n"
    assert (Path(first_output.folder) / "0.out").read_text() == "running\n"
    assert turns.timed_out == set()


def test_a_background_turns_old_deadline_does_not_stop_the_next_run_after_its_output_ended(turn_scope, tmp_path):
    turns, rows, outputs = turn_scope
    first_output = running_output(outputs, tmp_path, "first")
    first = running_turn(rows, first_output)
    outputs.save(first_output.with_(ended=True), Actor.system())
    later_output = running_output(outputs, tmp_path, "later")
    later = running_turn(rows, later_output)

    turns.stopped(first)

    assert rows.find(later.id).state == TestTurnState.RUNNING
    assert not outputs.find(later_output.row_id).ended
    assert (Path(later_output.folder) / "0.out").read_text() == "running\n"
    assert turns.timed_out == set()


def test_a_running_turns_deadline_stops_its_recorded_output_even_when_another_output_is_newer(turn_scope, tmp_path):
    turns, rows, outputs = turn_scope
    first_output = running_output(outputs, tmp_path, "first")
    first = running_turn(rows, first_output)
    later_output = running_output(outputs, tmp_path, "later")

    turns.stopped(first)

    assert "test budget's time limit" in (Path(first_output.folder) / "0.out").read_text()
    assert (Path(later_output.folder) / "0.out").read_text() == "running\n"
    assert turns.timed_out == {first.id}


def test_a_deadline_without_a_recorded_output_does_not_guess_from_the_worktree(turn_scope, tmp_path):
    turns, rows, outputs = turn_scope
    later_output = running_output(outputs, tmp_path, "later")
    first = rows.save(TestTurn(worker=1, folder=later_output.ran_in).started(later_output.creation_time.timestamp() - 1), Actor.system())

    turns.stopped(first)

    assert (Path(later_output.folder) / "0.out").read_text() == "running\n"
    assert turns.timed_out == set()


def test_a_foreground_turn_records_its_output_before_its_deadline_fires(app, turn_scope, tmp_path, monkeypatch):
    turns, rows, outputs = turn_scope
    worker = app.container.get(Workers).save(Worker(name="Test worker"), Actor.system())
    turn = rows.save(TestTurn(worker=worker.id, folder=str(tmp_path / "worktree"), command="pytest -q").started(0), Actor.system())
    bound = []

    def run(request, caller, environment, *, on_output=None):
        output = running_output(outputs, tmp_path, "foreground")
        if on_output is not None:
            on_output(output.row_id)
        bound.append((rows.find(turn.id).output, output.row_id))
        turns.stopped(turn)
        outputs.save(output.with_(ended=True), Actor.system())
        yield b"1 passed in 0.1s\n__journal_exit 0\n"

    monkeypatch.setattr(turns.runner, "run", run)
    turns.run_turn(turn, Caller.user("main"), 1)

    assert bound[0][0] == bound[0][1]
    assert rows.find(turn.id).output == bound[0][1]
    assert turn.id in turns.timed_out


def test_the_shell_runner_reports_its_exact_output_before_launching_the_process(app, turn_scope, tmp_path, monkeypatch):
    _, _, outputs = turn_scope
    runner = app.container.get(ShellRunner)
    bound = []
    monkeypatch.setattr(runner, "is_held", lambda request, caller, environment: True)

    list(runner.run(ShellRequest(line="pytest -q tests/example.py", cwd=str(tmp_path), shell="bash", environment={}), Caller.user("main"), 1, on_output=bound.append))

    assert len(bound) == 1
    assert outputs.find(bound[0]).ran_in == str(tmp_path)
    assert outputs.find(bound[0]).command == "pytest -q tests/example.py"


def test_a_turns_failure_is_counted_once_when_its_output_and_foreground_both_record_it(app, turn_scope, tmp_path):
    turns, rows, outputs = turn_scope
    workers = app.container.get(Workers)
    worker = workers.save(Worker(name="Test worker"), Actor.system())
    output = running_output(outputs, tmp_path, "foreground")
    turn = rows.save(TestTurn(worker=worker.id, output=output.row_id).started(0), Actor.system())

    turns.recorded(turn, TestRunResult(status=1, failed=1))
    once = workers.find(worker.id)
    turns.recorded(turn, TestRunResult(status=1, failed=1))

    assert workers.find(worker.id) == once


def test_a_clockout_run_accepts_a_short_output_the_shell_runner_has_already_discarded(app, turn_scope, tmp_path, monkeypatch):
    turns, _, outputs = turn_scope
    worker = app.container.get(Workers).save(Worker(name="Test worker"), Actor.system())
    user_set(app, WorkersOptions.TEST_COMMAND.key, "pytest -q")

    def run(request, caller, environment, *, on_output):
        output = running_output(outputs, tmp_path, "short")
        on_output(output.row_id)
        outputs.delete(output, Actor.system())
        yield b"1 passed in 0.1s\n__journal_exit 0\n"

    monkeypatch.setattr(turns.runner, "run", run)
    turn, result = turns.checked(worker, "tests/example.py", Caller.user("main"))

    assert turn.has_passed()
    assert "1 passed" in result
