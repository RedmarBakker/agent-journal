"""A reader is judged on what a run really prints, when it is added and again while a watched run goes on, on the readers a consumer project's agent wrote to get past the checks: patterns that pick every line, a test run's reader fitted to its image build, a reader of pass lines with no progress, a progress pattern that read card numbers in product names, and dismissals the run itself disproves."""

import os
import re
import stat
from types import SimpleNamespace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from journal.app import App
from journal.features.shell.support.count_forms import CountForms
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_commands import ReaderCommands
from journal.features.shell.support.reader_judge import ReaderJudge
from journal.features.shell.support.shell_data_reader import ShellDataReader
from journal.features.shell.support.shell_request import ShellRequest
from journal.features.shell.support.shell_runner import ShellRunner
from journal.features.shell.support.watched_run_judge import WatchedRunJudge
from journal.models.command_output import CommandOutput
from journal.models.reader_report import ReaderReport
from journal.models.setting import Setting
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.reader_reports import ReaderReports
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.chain import Chain
from journal.support.command_classifier import CommandClassifier
from journal.support.command_shape import CommandShape
from journal.supervisor_link import SupervisorLink
from tests.test_features import booted, hook

AGENT = Caller.agent("main", "s1", "claude")
MAIN = 1
SUITE = "./scripts/test.sh"
DOCKER_BUILD_LINES = ["#1 [internal] load build definition from Dockerfile", "#4 [php 2/9] RUN apt-get install -y git", "#5 extracting sha256:9f2c", "#6 [php 3/9] COPY composer.json ."]
TEST_LINES = ["  PASS  Tests\\Unit\\ContactPayloadTest", "  ✓ a house number typed on the second line still reaches the label 0.04s", "  PASS  Tests\\Unit\\OrderTest", "  ✓ it ships the order 0.02s"]
PRODUCT_LINES = ["copied Pokemon Booster Pack 65/131 to the shop", "copied Pokemon Promo Card 225/182 to the shop", "copied Pokemon Elite Box 12/165 to the shop"]


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture
def app(app: App):
    with app.container.get(Scope).environment(MAIN):
        hook(app, "SessionStart")
        app.console().run(["environment", "overview"], AGENT)
        yield app


def added(app: App, *argv: str):
    return app.console().run(["reader", "add", *argv], AGENT)


def stored_run(app: App, command: str, lines: list[str]) -> CommandOutput:
    script = app.config.root / command
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("#!/bin/sh\n" + "".join(f"echo '{line}'\n" for line in lines * 20))
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    link = app.container.get(SupervisorLink)
    link.working(MAIN)
    wrapped = f"true && eval {command} < /dev/null && pwd -P >| /dev/null"
    shown = b"".join(app.container.get(ShellRunner).run(ShellRequest(line=wrapped, cwd=str(app.config.root), shell="/bin/sh", environment=dict(os.environ)), AGENT, MAIN)).decode() + link.pending_lines(MAIN)
    number = re.search(r"output (\d+)", shown)
    assert number, shown
    return app.container.get(CommandOutputs).find(int(number.group(1)))


@pytest.mark.parametrize("flags", [("--pattern", ".+", "--finished", ".+"), ("--pattern", ".*"), ("--pattern", "^.*$")], ids=["dot-plus with dot-plus finished", "dot-star", "anchored dot-star"])
def test_a_reader_that_picks_every_line_is_refused(app: App, flags: tuple):
    output = added(app, "ssh-query", *flags, "--about", "what a query on the server prints")
    assert output.code != 0 and "filters nothing" in output.error, output.error


def test_a_test_run_reader_fitted_to_the_image_build_is_refused(app: App):
    output = added(app, "test-sh", "--commands", SUITE, "--pattern", r"^#\d+ \[|^#\d+ extracting", "--about", "the test run")
    assert output.code != 0 and "selects neither its summary" in output.error, output.error


def test_a_test_run_reader_of_pass_lines_alone_is_refused(app: App):
    output = added(app, "test-sh", "--commands", SUITE, "--pattern", r"^\s*PASS\s", "--about", "the test run", "--label", "Running tests")
    assert output.code != 0 and "selects neither its summary" in output.error, output.error


def test_a_test_run_reader_with_its_failures_summary_and_progress_is_added(app: App):
    output = added(app, "test-sh", "--commands", SUITE, "--pattern", r"FAILED|⨯", "--progress", r"(\d+)/(\d+)", "--finished", r"^\s*Tests:", "--failed", r"FAILED|^\s*Tests:", "--about", "the failures, progress and summary of the test run", "--label", "Running tests")
    assert output.code == 0, output.error


def test_card_numbers_in_product_names_are_no_count_of_a_total():
    assert not CountForms.has_total(PRODUCT_LINES)
    assert CountForms.has_total(["Running tests 3/13", "Running tests 7/13", "Running tests 13/13"])


def test_a_progress_pattern_that_reads_card_numbers_is_refused(app: App):
    run = stored_run(app, "scripts/copy.sh", PRODUCT_LINES)
    output = added(app, "file-copy", "--commands", "scripts/copy.sh", "--pattern", "^copied", "--progress", r"(\d+)/(\d+)", "--about", "the files copied", "--label", "Copying the files")
    assert output.code != 0 and f"tried on output {run.id}" in output.error and "count towards no total" in output.error and "225/182" in output.error, output.error


def test_a_reader_fitted_to_the_start_of_a_run_is_reported_once_the_run_prints_its_work(app: App):
    reader = Reader("test-sh", "the test run", pattern=r"^#\d+ \[|^#\d+ extracting", commands=ReaderCommands.parsed(SUITE))
    findings = app.container.get(WatchedRunJudge).findings(reader, DOCKER_BUILD_LINES * 3 + TEST_LINES * 11)
    assert any("none of its newest" in finding for finding, _ in findings), findings


def test_a_reader_that_shows_every_line_is_reported_while_the_run_goes_on():
    reader = Reader("ssh-query", "a query", pattern=".+")
    assert any("filtered nothing" in finding for finding, _ in WatchedRunJudge.unfiltered(reader, PRODUCT_LINES * 15)), "a card that shows the raw output is reported"


def test_a_dismissal_the_watched_run_disproves_is_opened_again(app: App):
    reports = app.container.get(ReaderReports)
    dismissed = reports.save(ReaderReport(environment_id=MAIN, reader="test-sh", output=1, command=SUITE, session="s1", findings=("the run took 362 seconds and its card showed no progress",), fixes=("give it --progress",)).dismissed("the test containers were only booting"), Actor.system())
    lines = [f"Running tests {n}/40" for n in range(1, 30)]
    folder = app.config.root / "watched-output"
    folder.mkdir()
    (folder / "parts").write_text("R-\n")
    (folder / "0.part").write_text(SUITE)
    (folder / "0.out").write_text("\n".join(lines) + "\n")
    output = app.container.get(CommandOutputs).save(CommandOutput(environment_id=MAIN, chain="w", command=SUITE, session="s1", folder=str(folder), moved=True, is_watched=True, watch_reader="test-sh-quiet"), Actor.system())
    reader_file = app.config.root / ".journal" / "readers" / "test-sh-quiet.pattern"
    reader_file.write_text(f"# the test run\nFAILED\ncommands: {SUITE}\n")
    app.container.get(WatchedRunJudge).judged(output, datetime.now(timezone.utc))
    reopened = reports.find(dismissed.id)
    assert reopened.is_refuted and reopened.dismissal is None and "was wrong" in reopened.verdict, reopened
    assert reports.open_with_output_finding(output.id, "showed no progress"), "the watched run raised its own report"


def test_a_second_dismissal_of_the_same_finding_waits_for_the_first_to_be_judged_sound(app: App):
    reports = app.container.get(ReaderReports)
    finding = ("the run printed nothing for 41 seconds while it ran, so its card had nothing to show",)
    reports.save(ReaderReport(environment_id=MAIN, reader="test-sh", output=1, command=SUITE, session="s1", findings=finding, fixes=("run it unbuffered",)).dismissed("health checks"), Actor.system())
    second = reports.save(ReaderReport(environment_id=MAIN, reader="test-sh", output=2, command=SUITE, session="s1", findings=finding, fixes=("run it unbuffered",)), Actor.system())
    output = app.console().run(["reader", "dismiss", str(second.id), "--why", "Laravel booting and migrating"], AGENT)
    assert output.code != 0 and "the cause is still there" in output.error, output.error


def test_a_test_run_watched_through_a_reader_with_no_progress_still_owes_a_reader(app: App):
    reader_file = app.config.root / ".journal" / "readers" / "pass-lines.pattern"
    reader_file.write_text(f"# the pass lines\n^\\s*PASS\\s\ncommands: {SUITE}\n")
    assert not app.container.get(ShellDataReader).is_read_well(SUITE)


def test_the_release_chain_is_read_as_its_work_and_owes_no_git_checkout_reader():
    line = "git checkout -q main && git merge --ff-only development && git push origin main && git tag v4.63.2 && git push origin v4.63.2 && gh release create v4.63.2 --notes done && git checkout -q development && git log --oneline -1 main"
    assert Chain.choosing_parts(line)[0] == "git merge --ff-only development"
    assert CommandShape.command_name(line) == "git merge"


def test_a_reader_for_git_checkout_is_tried_on_the_git_checkout_part_alone(app: App, tmp_path: Path):
    line = "git checkout -q main && git push origin main"
    files = OutputFiles(tmp_path)
    files.split(line, Chain.parts(line), app.container.get(CommandClassifier))
    (tmp_path / "0.out").write_text("Switched to branch 'main'\n")
    (tmp_path / "1.out").write_text("....................\n")
    reader = Reader("branch-switch", "the branch switched to", pattern="^Switched", commands=ReaderCommands.parsed("git checkout"))
    assert app.container.get(ReaderJudge).read_lines(reader, files) == ["Switched to branch 'main'"]


def test_a_stored_release_chain_joined_by_newlines_is_named_by_its_work(app: App):
    line = "git checkout -q main\ngit merge --ff-only development\ngit push origin main\ngit tag v4.63.2\ngit checkout -q development\ngit log --oneline -1 main"
    app.container.get(CommandOutputs).save(CommandOutput(environment_id=MAIN, chain="release", command=line, session="s1", moved=True), Actor.system())
    assert "git checkout" not in app.container.get(ShellDataReader).unwatched_commands(SimpleNamespace(session="s1"))


def test_a_reader_is_owed_only_for_test_runs_and_builds_and_one_named_by_the_demand_clears_it(app: App):
    for n, line in enumerate(("while true; do git status; sleep 5; done", 'ssh prod "cd app && php artisan migrate"', "php -m", "php -d memory_limit=-1 vendor/bin/phpunit")):
        app.container.get(CommandOutputs).save(CommandOutput(environment_id=MAIN, chain=f"c{n}", command=line, session="s1", moved=True), Actor.system())
    owed = app.container.get(ShellDataReader).unwatched_commands(SimpleNamespace(session="s1"))
    assert owed == ("php",), f"a git status loop, an ssh to production and php -m owe no reader; the php run of phpunit does (another project's php demand): {owed}"
    reader_file = app.config.root / ".journal" / "readers" / "phpunit-run.pattern"
    reader_file.write_text("# the phpunit run\n(FAILURES|Tests:|OK \\()\nprogress: (\\d+) / (\\d+)\nlabel: Running the tests\ncommands: php\nsummary: (Tests: .*)\n")
    assert app.container.get(ShellDataReader).unwatched_commands(SimpleNamespace(session="s1")) == (), "a labelled reader for php, the name the demand gives, clears it, and it is never asked to read the git, ssh or php -m runs"
