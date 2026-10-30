from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_sequence_is_never_started_over_a_compaction_or_a_wait_and_starts_on_top_once_it_is_over(story):
    checking = story.agent_creates_sequence(story.agents.subject, "Checking", "check it")
    for state in ("compacting", "awaiting"):
        story.agent_runs(story.agents.subject, f"panic apply {state}")
        result = story.agent_runs(story.agents.subject, f"sequence run {checking}")
        result.expect_command_refused()
        result.expect_command_text("once that is over")
        story.agent_runs(story.agents.subject, "panic apply pop")
    result = story.agent_runs(story.agents.subject, f"sequence run {checking}")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
