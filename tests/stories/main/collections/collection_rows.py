from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_collection_holds_rows_of_any_type_refuses_one_that_is_not_there_and_lets_one_go(story):
    task = story.agent_creates_task(story.agents.subject, "the parser")
    story.agent_runs(story.agents.subject, "collection create 'The parser work' --abstract 'what the parser needs'")
    collection = story.created_number("collection")
    result = story.agent_runs(story.agents.subject, f"collection add {collection} tasks:{task}")
    result.expect_command_passed()
    result = story.agent_runs(story.agents.subject, f"collection add {collection} tasks:99")
    result.expect_command_text("not a row here: tasks:99")
    result = story.agent_runs(story.agents.subject, f"collection members {collection}")
    result.expect_command_text(f"tasks:{task}")
    story.agent_runs(story.agents.subject, f"collection remove {collection} tasks:{task}")
    story.agent_runs(story.agents.subject, f"collection rename {collection} Parser")
    result = story.agent_runs(story.agents.subject, "collection list")
    result.expect_command_text("Parser  (0 rows)")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_deleted_collection_is_gone_and_its_rows_stay(story):
    task = story.agent_creates_task(story.agents.subject, "the parser")
    story.agent_runs(story.agents.subject, "collection create 'The parser work'")
    collection = story.created_number("collection")
    story.agent_runs(story.agents.subject, f"collection add {collection} tasks:{task}")
    result = story.agent_runs(story.agents.subject, f"collection delete {collection}")
    result.expect_command_text(f"collection {collection} is deleted; its rows stay")
    result = story.agent_runs(story.agents.subject, "collection list")
    result.expect_command_text_without("The parser work")
    story.expect_task(task, title="the parser")
    story.expect_stack(story.agents.subject, Ready)
