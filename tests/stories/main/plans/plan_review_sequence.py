from journal.features.plans.plans_nudges import PlansNudges
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.models.plan_state import PlanState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.agent_ready_plan import AgentReadyPlan
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER


@story(AgentReadyPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_plan_review_lets_edits_through_while_reviewers_are_out_holds_them_while_findings_go_in_and_ends_when_the_plan_is_readied(story):
    story.agent_runs(story.agents.subject, f"plan review {story.plans.first}")
    story.agent_runs(story.agents.subject, "sequence follow")
    story.agent_writes(story.agents.subject, "a.md")
    story.expect_allowed()
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, f"review plan {story.plans.first}", "a1")
    story.subagent_ends("a1")
    story.expect_agent_told(story.agents.subject, PlansNudges.REVIEW_ENTRY_REQUEST, n=story.plans.first)
    story.agent_runs(story.agents.subject, "sequence follow")
    story.agent_writes(story.agents.subject, "a.md")
    story.expect_refused(story.agents.subject, SequencesNudges.STEP_EDITS_WAIT)
    story.agent_runs(story.agents.subject, "sequence next")
    story.agent_runs(story.agents.subject, "sequence follow")
    story.agent_writes(story.agents.subject, "a.md")
    story.expect_allowed()
    story.agent_runs(story.agents.subject, f"plan ready {story.plans.first} --changed 'two gaps filled'")
    story.expect_plan(story.plans.first, state=PlanState.READY)
    story.expect_task(story.tasks.slab, state="open")
    story.expect_stack(story.agents.subject, Ready)


@story(AgentReadyPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagent_resumed_with_a_message_naming_the_plan_counts_as_its_reviewer_until_it_ends(story):
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, "read the design document", "a1")
    story.subagent_ends("a1")
    story.agent_runs(story.agents.subject, f"plan review {story.plans.first}")
    story.agent_runs(story.agents.subject, "sequence follow")
    story.agent_messages_subagent(story.agents.subject, "a1", f"now review plan {story.plans.first} against the design")
    story.expect_plan(story.plans.first, reviewers=1)
    story.agent_writes(story.agents.subject, "a.md")
    story.expect_allowed()
    story.subagent_ends("a1")
    story.expect_plan(story.plans.first, reviewers=0)
    story.expect_task(story.tasks.slab, state="open")
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)


@story(AgentReadyPlan, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_review_round_counts_only_the_reviewers_sent_in_it_and_a_subagent_that_ended_before_moves_nothing(story):
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, f"read plan {story.plans.first} early", "a1")
    story.subagent_ends("a1")
    story.agent_runs(story.agents.subject, f"plan review {story.plans.first}")
    story.expect_plan(story.plans.first, state=PlanState.REVIEWING, reviewers=0)
    story.agent_sends_subagent_in_the_background(story.agents.subject, "journal-plan-reviewer", f"review plan {story.plans.first}", "a2")
    story.expect_plan(story.plans.first, reviewers=1)
    story.subagent_ends("a2")
    story.expect_plan(story.plans.first, reviewers=0)
    story.expect_task(story.tasks.slab, state="open")
    story.expect_stack(story.agents.subject, Ready, FollowingSequence)
