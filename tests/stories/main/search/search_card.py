from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_search_is_one_mark_naming_its_result_count_with_a_child_per_row_newest_first(story):
    scoped = story.agent_creates_briefed_task(story.agents.subject, "Scope the reads", "the base repository adds the environment")
    paged = story.agent_creates_briefed_task(story.agents.subject, "Page the lists", "the base repository bounds every list")
    story.agent_runs(story.agents.subject, "search base repository")
    story.expect_row("messages", story.newest("messages"), {"text": 'Searched for "base repository", 2 results'})
    story.expect_search_result_rows(story.newest("messages"), f"tasks:{paged}", f"tasks:{scoped}")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_search_with_one_result_names_one_result(story):
    story.agent_creates_briefed_task(story.agents.subject, "Scope the reads", "the base repository adds the environment")
    story.agent_runs(story.agents.subject, "search environment")
    story.expect_row("messages", story.newest("messages"), {"text": 'Searched for "environment", 1 result'})
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_search_that_finds_nothing_is_marked_with_no_results_to_open(story):
    story.agent_creates_task(story.agents.subject, "the whole of it")
    story.agent_runs(story.agents.subject, "search zebra")
    story.expect_row("messages", story.newest("messages"), {"text": 'Searched for "zebra", no results'})
    story.expect_search_result_rows(story.newest("messages"))
    story.expect_stack(story.agents.subject, Ready)
