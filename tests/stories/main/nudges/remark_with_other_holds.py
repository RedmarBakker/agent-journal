from journal.engine.states.demand_block import DemandBlock
from journal.features.etiquette.etiquette_nudges import EtiquetteNudges
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.build_wait import BuildWait
from tests.stories.fixtures.main.unanswered_message import UnansweredMessage

EM_DASHES = "The build — the one from last night — is green."


@story(UnansweredMessage, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_remark_waiting_rides_a_refused_tool_use_beside_the_refusal(story):
    story.agent_closes_its_turn(story.agents.subject, EM_DASHES)
    story.agent_writes(story.agents.subject, "src/app.py")
    story.expect_refused_by_anything()
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_stack(story.agents.subject, Ready, DemandBlock)


@story(BuildWait, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_remark_made_while_the_agent_waits_rides_the_tool_use_that_ends_the_wait(story):
    story.agent_closes_its_turn(story.agents.subject, EM_DASHES)
    story.agent_reads(story.agents.subject)
    story.expect_last_answer_carries(EtiquetteNudges.EM_DASH_WARNING)
    story.expect_stack(story.agents.subject, Ready, Working)
