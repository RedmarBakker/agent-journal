from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_journal_panic_pushes_pops_and_empties_the_stack_by_hand_naming_it_bottom_to_top(story):
    result = story.agent_runs(story.agents.subject, "panic working focus=parsing")
    result.expect_command_text("the stack, bottom to top: idle, working(focus=parsing)")
    result = story.agent_runs(story.agents.subject, "panic stuck reason=lost")
    result.expect_command_text("the stack, bottom to top: idle, working(focus=parsing), stuck(")
    result = story.agent_runs(story.agents.subject, "panic pop")
    result.expect_command_text("idle, working(focus=parsing)")
    result = story.agent_runs(story.agents.subject, "panic nowhere")
    result.expect_command_refused()
    result = story.agent_runs(story.agents.subject, "panic idle")
    result.expect_command_text("the stack, bottom to top: idle")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_panic_pause_holds_every_tool_but_a_panic_line_alone(story):
    story.agent_runs(story.agents.subject, "panic paused")
    result = story.agent_writes(story.agents.subject, "a.py")
    result.expect_refused_by_anything()
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal panic apply idle")
    result.expect_allowed()
    result = story.agent_runs_in_the_shell(story.agents.subject, "journal panic apply idle && rm -rf a")
    result.expect_refused_by_anything()
    story.agent_runs(story.agents.subject, "panic pop")
    story.expect_stack(story.agents.subject, Ready)
