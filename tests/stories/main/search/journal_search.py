from journal.features.search.support.search import SHOWN_ROWS
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_search_finds_the_rows_holding_every_word_in_any_case_and_no_row_missing_one(story):
    story.agent_creates_briefed_task("Scope the reads", "the base repository adds the environment")
    story.agent_runs("reminder create 'the base model is data only'")
    story.agent_runs("search base REPOSITORY")
    story.expect_command_text("Scope the reads")
    story.expect_command_text_without("the base model is data only")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_search_is_marked_in_the_chat_with_what_it_found(story):
    story.agent_creates_briefed_task("Scope the reads", "the base repository adds the environment")
    story.agent_runs("search base repository")
    story.expect_row("messages", story.newest("messages"), {"text": 'Searched for "base repository"'})
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_percent_sign_in_a_search_is_a_letter_and_the_verb_may_be_named(story):
    story.agent_creates_task("the whole of it")
    story.agent_runs("search find 100%")
    story.expect_command_text("nothing here holds all of: 100%")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_search_narrowed_to_models_finds_only_their_rows(story):
    story.agent_creates_briefed_task("Scope the reads", "the base repository adds the environment")
    story.agent_runs("check create 'Lint the base repository' --command true --every 0 --brief 'lints'")
    story.agent_runs("search base repository --model check")
    story.expect_command_text("Lint the base repository")
    story.expect_command_text_without("Scope the reads")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_search_shows_a_limited_number_of_rows_however_many_hold_the_words(story):
    story.repeat(SHOWN_ROWS + 5, lambda: story.agent_creates_task("needle"))
    story.agent_runs("search needle")
    story.expect_command_line_count(SHOWN_ROWS)
    story.expect_stack(Ready)
