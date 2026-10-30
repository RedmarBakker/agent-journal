from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.support.reader_drafts import HAND_READS
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class VerifierJudgingDismissal(StateFixture):
    """The agent searched a background run by hand until the journal read it with a reader of its own and raised a report on it, the agent dismissed the report with a reason, and the verifier the journal sent to judge that started: story.agents.verifiers.first()."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        output = story.agent_has_a_background_run_printing(story.agents.main, "./scripts/serve.sh", "started")
        for _ in range(HAND_READS):
            story.agent_runs_in_the_shell(story.agents.main, f"journal output read {output} --grep started")
        story.background_run_ends(story.agents.main, output)
        report = story.told_number(ShellNudges.REPORT_RAISED, "n")
        story.agent_runs(story.agents.main, f"reader dismiss {report} --why 'the run printed one line, which the reader shows'")
        self.verifiers.first = story.newest("verifiers")
        story.agent_starts_a_session(story.agents.verifiers.first())

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
