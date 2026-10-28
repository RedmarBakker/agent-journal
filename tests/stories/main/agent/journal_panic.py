from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_journal_panic_pushes_pops_and_empties_the_stack_by_hand_naming_it_bottom_to_top(story):
    story.agent_runs("panic working focus=parsing")
    story.expect_command_text("the stack, bottom to top: idle, working(focus=parsing)")
    story.agent_runs("panic stuck reason=lost")
    story.expect_command_text("the stack, bottom to top: idle, working(focus=parsing), stuck(")
    story.agent_runs("panic pop")
    story.expect_command_text("idle, working(focus=parsing)")
    story.agent_runs("panic nowhere")
    story.expect_command_refused()
    story.agent_runs("panic idle")
    story.expect_command_text("the stack, bottom to top: idle")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_panic_pause_holds_every_tool_but_a_panic_line_alone(story):
    story.agent_runs("panic paused")
    story.agent_writes("a.py")
    story.expect_refused_by_anything()
    story.agent_runs_in_the_shell("journal panic apply idle")
    story.expect_allowed()
    story.agent_runs_in_the_shell("journal panic apply idle && rm -rf a")
    story.expect_refused_by_anything()
    story.agent_runs("panic pop")
    story.expect_stack(Ready)
