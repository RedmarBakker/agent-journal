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
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.reader_drafts import ReaderDrafts
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


def stored_run(app: App, command: str, lines: list[str], status: int = 0) -> CommandOutput:
    script = app.config.root / command
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("#!/bin/sh\n" + "".join(f"echo '{line}'\n" for line in lines * 20) + f"exit {status}\n")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    link = app.container.get(SupervisorLink)
    link.working(MAIN)
    wrapped = f"true && eval {command} < /dev/null && pwd -P >| /dev/null"
    shown = b"".join(app.container.get(ShellRunner).run(ShellRequest(line=wrapped, cwd=str(app.config.root), shell="/bin/sh", environment=dict(os.environ)), AGENT.subagent_caller(), MAIN)).decode() + link.pending_lines(MAIN)
    number = re.search(r"output (\d+)", shown)
    assert number, shown
    return app.container.get(CommandOutputs).find(int(number.group(1)))


@pytest.mark.parametrize("flags", [("--pattern", ".+", "--finished", ".+"), ("--pattern", ".*"), ("--pattern", "^.*$")], ids=["dot-plus with dot-plus finished", "dot-star", "anchored dot-star"])
def test_a_reader_that_picks_every_line_is_refused(app: App, flags: tuple):
    output = added(app, "ssh-query", *flags, "--about", "what a query on the server prints")
    assert output.code != 0 and "matches every line" in output.error, output.error


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
    assert output.code != 0 and "found the same, unjudged" in output.error, output.error


def test_a_test_run_watched_through_a_reader_with_no_progress_still_owes_a_reader(app: App):
    reader_file = app.config.root / ".journal" / "readers" / "pass-lines.pattern"
    reader_file.write_text(f"# the pass lines\n^\\s*PASS\\s\ncommands: {SUITE}\n")
    assert not app.container.get(ReaderDrafts).is_read_well(SUITE)


def test_the_release_chain_is_read_as_its_work_and_owes_no_git_checkout_reader(app: App):
    line = "git checkout -q main && git merge --ff-only development && git push origin main && git tag v4.63.2 && git push origin v4.63.2 && gh release create v4.63.2 --notes done && git checkout -q development && git log --oneline -1 main"
    assert app.container.get(Readers).choosing_parts(line)[0] == "git merge --ff-only development"
    assert app.container.get(CommandShape).command_name(line) == "git merge"


def test_a_reader_for_git_checkout_is_tried_on_the_git_checkout_part_alone(app: App, tmp_path: Path):
    line = "git checkout -q main && git push origin main"
    files = OutputFiles(tmp_path)
    files.split(line, Chain.parts(line), app.container.get(CommandClassifier))
    (tmp_path / "0.out").write_text("Switched to branch 'main'\n")
    (tmp_path / "1.out").write_text("....................\n")
    reader = Reader("branch-switch", "the branch switched to", pattern="^Switched", commands=ReaderCommands.parsed("git checkout"))
    assert app.container.get(ReaderJudge).read_lines(reader, files) == ["Switched to branch 'main'"]


def test_a_stored_release_chain_joined_by_newlines_is_offered_no_reader(app: App):
    line = "git checkout -q main\ngit merge --ff-only development\ngit push origin main\ngit tag v4.63.2\ngit checkout -q development\ngit log --oneline -1 main"
    output = app.container.get(CommandOutputs).save(CommandOutput(environment_id=MAIN, chain="release", command=line, session="s1", moved=True, ended=True), Actor.system())
    assert app.container.get(ReaderDrafts).draft(output, "s1", {}) is None, "version control never earns a reader"


def test_a_reader_is_offered_only_for_test_runs_builds_installs_and_long_processes_and_a_reader_that_reads_one_clears_it(app: App):
    drafts = app.container.get(ReaderDrafts)
    stored = [app.container.get(CommandOutputs).save(CommandOutput(environment_id=MAIN, chain=f"c{n}", command=line, session="s1", moved=True, ended=True), Actor.system())
              for n, line in enumerate(("while true; do git status; sleep 5; done", 'ssh prod "cd app && php artisan migrate"', "php -d memory_limit=-1 vendor/bin/phpunit"))]
    owed = [draft.part if (draft := drafts.draft(output, "s1", {})) else "" for output in stored]
    assert owed == ["", "", "php"], f"a git status loop and an ssh to production earn no reader; the php run of phpunit, a long process, does: {owed}"
    reader_file = app.config.root / ".journal" / "readers" / "phpunit-run.pattern"
    reader_file.write_text("# the phpunit run\n(FAILURES|Tests:|OK \\()\nprogress: (\\d+) / (\\d+)\nlabel: Running the tests\ncommands: php\nsummary: (Tests: .*)\n")
    assert drafts.draft(stored[2], "s1", {}) is None, "a reader that reads its part clears it"

PASSING_LINES = ["  ✓ it ships the order 0.02s", "Tests:    3 passed (5 assertions)"]
FAILING_LINES = ["  ⨯ it ships the order", "FAILED  Tests\\Unit\\OrderTest > it ships the order", "Tests:  1 failed, 2 passed (5 assertions)"]


def test_a_new_test_run_reader_shows_the_counts_of_a_passing_and_a_failing_run_and_a_reader_stored_before_is_never_refused_for_them(app: App):
    passing = stored_run(app, SUITE, PASSING_LINES)
    failing = stored_run(app, SUITE, FAILING_LINES, status=1)
    assert passing.status == 0 and failing.status != 0, (passing, failing)
    flags = ("--commands", SUITE, "--pattern", r"FAILED|⨯", "--finished", r"^Tests:", "--about", "the failures and the summary", "--label", "Running tests")
    refused = added(app, "suite-runs", *flags, "--failed", r"FAILED|⨯")
    assert refused.code != 0 and f"no counts of the failing run, output {failing.id}" in refused.error and "--failed pattern" in refused.error and "1 failed, 2 passed" in refused.error, refused.error
    assert added(app, "suite-runs", *flags, "--failed", r"FAILED|⨯|^Tests:").code == 0, "a reader that shows the counts of both runs is added"
    assert added(app, "suite-runs", "--failed", r"FAILED|⨯").code == 0, "a reader stored before is never refused by the checks of its kind"


def test_a_new_readers_progress_matches_the_run_it_was_written_from_unless_an_alias_names_the_reader(app: App):
    from journal.models.alias import Alias
    from journal.repositories.aliases import Aliases
    run = stored_run(app, "scripts/copy.sh", ["copied a.txt", "copied b.txt", "done in 2s"])
    flags = ("--commands", "scripts/copy.sh", "--pattern", "^copied|^done", "--progress", r"(\d+)/(\d+)", "--about", "the files copied", "--label", "Copying the files")
    refused = added(app, "copies", *flags)
    assert refused.code != 0 and f"its --progress matches no line of output {run.id}" in refused.error and "done in 2s" in refused.error, refused.error
    app.container.get(Aliases).save(Alias(name="copy", line="scripts/copy.sh", reader="copier"), Actor.system())
    assert added(app, "copier", *flags).code == 0, "a reader an alias names is left to the reader judge"


def test_the_shell_readers_section_counts_reader_runs_report_rate_suggestions_followed_and_suggestions_per_session(app: App):
    from journal.features.shell.shell_nudges import ShellNudges
    from journal.models.entry import Entry
    from journal.repositories.entries import Entries
    from tests.in_process import get_answer
    outputs = app.container.get(CommandOutputs)
    for reader, session in (("naps", "s1"), ("naps", "s1"), ("", "s1"), ("", "s2")):
        outputs.save(CommandOutput(environment_id=MAIN, command="sh test_naps.sh", session=session, moved=True, ended=True, watch_reader=reader), Actor.system())
    app.container.get(ReaderReports).save(ReaderReport(environment_id=MAIN, reader="naps", output=1, command="sh test_naps.sh", session="s1", findings=("x",), fixes=("y",)), Actor.system())
    for part in ("test_naps.sh", "make all"):
        app.container.get(Entries).save(Entry(environment_id=MAIN, entry_type="nudge", actor=Actor.system(), data={"session": "s1", "key": ShellNudges.READER_DRAFT.key, "values": {"part": part}, "line": f"no reader reads {part} yet"}), Actor.system())
    assert added(app, "naps", "--commands", "test_naps.sh", "--pattern", "FAILED|passed|failed", "--finished", "passed", "--failed", "failed", "--about", "the naps", "--label", "Taking a nap").code == 0
    status, measures = get_answer(app, "/journal/developer/readers", {"X-Journal-Env": "main"})
    assert status == 200 and (measures["background_runs"], measures["reader_runs"]) == (4, 2), "half the background runs were read by a project reader"
    assert measures["readers"] == [{"reader": "naps", "runs": 2, "reports": 1, "report_rate": 5.0}], "one report over two runs is five per ten runs"
    assert (measures["suggestions"], measures["followed_suggestions"], measures["sessions"]) == (2, 1, 2), "of two suggestions one is read by a reader now, over two sessions that moved a run"
