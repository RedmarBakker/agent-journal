from journal.features.search.support.search import SHOWN_ROWS
from journal.features.tasks.states.ready import Ready
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_search_finds_the_rows_holding_every_word_in_any_case_and_no_row_missing_one(story):
    story.agent_creates_briefed_task(story.agents.subject, "Scope the reads", "the base repository adds the environment")
    story.agent_runs(story.agents.subject, "reminder create 'the base model is data only'")
    result = story.agent_runs(story.agents.subject, "search base REPOSITORY")
    result.expect_command_text("Scope the reads")
    result.expect_command_text_without("the base model is data only")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_percent_sign_in_a_search_is_a_letter_and_the_verb_may_be_named(story):
    story.agent_creates_task(story.agents.subject, "the whole of it")
    result = story.agent_runs(story.agents.subject, "search find 100%")
    result.expect_command_text("nothing here holds all of: 100%")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_search_narrowed_to_models_finds_only_their_rows(story):
    story.agent_creates_briefed_task(story.agents.subject, "Scope the reads", "the base repository adds the environment")
    story.agent_runs(story.agents.subject, "check create 'Lint the base repository' --command true --every 0 --brief 'lints'")
    result = story.agent_runs(story.agents.subject, "search base repository --model check")
    result.expect_command_text("Lint the base repository")
    result.expect_command_text_without("Scope the reads")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_search_shows_a_limited_number_of_rows_however_many_hold_the_words(story):
    story.repeat(SHOWN_ROWS + 5, lambda: story.agent_creates_task(story.agents.subject, "needle"))
    result = story.agent_runs(story.agents.subject, "search needle")
    result.expect_command_line_count(SHOWN_ROWS)
    story.expect_stack(story.agents.subject, Ready)
