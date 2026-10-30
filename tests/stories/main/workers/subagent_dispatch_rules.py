from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.subagent.started_subagent import RESEARCHER

JOB = {"description": "map the hooks", "prompt": "read the hooks"}


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagent_dispatch_without_a_model_is_held_before_it_starts_and_never_listed(story):
    result = story.agent_sends_subagent_with(story.agents.subject, subagent_type=RESEARCHER, **JOB)
    result.expect_refused_by_anything()
    result.expect_refusal_text("name a model in the dispatch")
    result = story.user_opens("/journal/subagents")
    result.expect_viewer_rows("rows", "task", [])
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_generic_subagent_is_refused_and_offered_the_projects_reading_profiles_only(story):
    result = story.agent_sends_subagent_with(story.agents.subject, model="fast", subagent_type="general-purpose", **JOB)
    result.expect_refusal_text("has no profile of this project")
    result.expect_refusal_text("researcher")
    result.expect_refusal_without("senior")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_subagent_dispatch_without_a_job_is_refused_and_one_with_its_job_goes_through(story):
    result = story.agent_sends_subagent_with(story.agents.subject, model="fast", subagent_type=RESEARCHER, prompt="read")
    result.expect_refusal_text("no concrete job")
    result = story.agent_sends_subagent_with(story.agents.subject, model="fast", subagent_type=RESEARCHER, **JOB)
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)
