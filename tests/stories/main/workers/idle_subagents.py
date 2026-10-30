from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_worker_list_shows_the_subagents_and_a_job_on_their_files_goes_back_to_the_idle_ones_never_a_retired_one(story):
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, "map src/journal/features/shell/chain.py", "r1")
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, "map the parts of src/journal/features/shell/chain.py", "r2")
    story.agent_sends_subagent_in_the_background(story.agents.subject, RESEARCHER, "map src/journal/hooks/hook.sh", "r3")
    story.subagent_ends("r1")
    story.subagent_ends("r2")
    story.agent_runs(story.agents.subject, "worker list")
    story.expect_command_text("session: r1")
    story.expect_command_text("running")
    story.agent_sends_subagent(story.agents.subject, RESEARCHER, "find the edge cases of chain.py")
    story.expect_refusal_text("2 idle subagents")
    story.agent_runs(story.agents.subject, "subagent retire 2")
    story.expect_command_passed()
    story.agent_sends_subagent(story.agents.subject, RESEARCHER, "find the edge cases of chain.py")
    story.expect_refusal_text("1 idle subagents")
    story.expect_stack(story.agents.subject, Ready)
