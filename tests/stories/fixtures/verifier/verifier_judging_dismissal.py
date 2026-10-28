from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.support.reader_drafts import HAND_READS
from journal.features.tasks.states.ready import Ready
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class VerifierJudgingDismissal(StateFixture):
    """The agent searched a background run by hand until the journal read it with a reader of its own and raised a report on it, the agent dismissed the report with a reason, and the verifier the journal sent to judge that started: start.verifier."""

    stack = (Ready,)

    parent = WorkingAgent

    settings = ((FOREGROUND_OPTION, 1),)

    def steps(self, story) -> None:
        output = story.agent_runs_a_command("sh -c 'echo started; sleep 3'")
        for _ in range(HAND_READS):
            story.agent_runs_in_the_shell(f"journal output read {output} --grep started")
        story.background_run_ends(output)
        report = story.told_number(ShellNudges.REPORT_RAISED, "n")
        story.agent_runs(f"reader dismiss {report} --why 'the run printed one line, which the reader shows'")
        self.verifier = story.newest("verifiers")
        story.verifier_session_starts(self.verifier)

    def expected(self, story) -> None:
        story.expect_stack(Ready)
