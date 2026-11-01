from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.draft_plan import DraftPlan


@story(DraftPlan, subject=AgentRole.MAIN)
def test_the_agent_writing_its_own_plan_cannot_pause_the_building_to_edit_files(story):
    story.agent_runs(story.agents.subject, "sequence follow")
    result = story.agent_runs(story.agents.subject, "sequence pause --why 'I fix a bug meanwhile'")
    result.expect_command_refused()
    result.expect_command_text("sequence delegate")
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, SequencesNudges.STEP_EDITS_WAIT)
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(DraftPlan, subject=AgentRole.MAIN)
def test_a_plan_whose_writing_is_handed_to_subagents_lets_the_agent_edit_meanwhile(story):
    story.agent_runs(story.agents.subject, "sequence follow")
    result = story.agent_runs(story.agents.subject, "sequence delegate --why 'two planners fill the phases'")
    result.expect_command_passed()
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_allowed()
    story.expect_plan(story.plans.first, state=PlanState.DRAFT)
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
