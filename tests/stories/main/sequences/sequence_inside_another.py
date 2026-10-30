from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.sequence_run import SequenceRun


@story(SequenceRun, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_sequence_started_inside_another_is_followed_first_holds_work_until_taken_up_and_the_outer_one_comes_back_after(story):
    story.agent_runs(story.agents.subject, "sequence follow")
    story.agent_runs_in_the_shell(story.agents.subject, "make build")
    story.expect_allowed()
    inner = story.agent_creates_sequence(story.agents.subject, "inner", "check it")
    story.agent_runs(story.agents.subject, f"sequence run {inner}")
    story.expect_command_text("step 1: check it")
    story.expect_stack(story.agents.subject, Ready, FollowingSequence, FollowingSequence)
    story.agent_runs_in_the_shell(story.agents.subject, "make build")
    story.expect_refused_by_anything()
    story.agent_runs(story.agents.subject, "sequence follow")
    story.agent_runs(story.agents.subject, "sequence next")
    story.expect_agent_told(story.agents.subject, SequencesNudges.PENDING_STEP, n=story.sequences.first, step=1)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
