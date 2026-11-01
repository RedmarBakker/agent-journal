from journal.features.tasks.states.ready import Ready
from journal.features.templates.shipped import FIND_MISTAKES, PLAN_SCOPED_TESTS
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

OLDER_BRIEF = "Run the tests of each task when it is done."


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_shipped_template_an_older_journal_wrote_is_brought_to_what_this_journal_ships_at_its_next_start(story):
    story.an_older_journal_wrote_the_template(PLAN_SCOPED_TESTS.title, OLDER_BRIEF)
    story.journal_starts_again()
    result = story.user_types(f"template show {story.template_number(PLAN_SCOPED_TESTS.title)}")
    result.expect_command_text(PLAN_SCOPED_TESTS.brief)
    result.expect_command_text_without(OLDER_BRIEF)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_an_older_copy_of_a_shipped_template_never_changed_is_taken_away_at_the_next_start_leaving_the_one_this_journal_ships(story):
    story.an_older_journal_left_a_copy_of_the_template(FIND_MISTAKES.title, OLDER_BRIEF)
    story.journal_starts_again()
    result = story.user_types("template list")
    result.expect_command_lines_holding(FIND_MISTAKES.title, 1)
    result = story.user_types(f"template show {story.template_number(FIND_MISTAKES.title)}")
    result.expect_command_text(FIND_MISTAKES.brief)
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_a_template_an_older_journal_shipped_and_this_one_no_longer_ships_is_taken_away_at_the_next_start(story):
    story.an_older_journal_shipped_the_template("Check the old way", OLDER_BRIEF)
    story.journal_starts_again()
    result = story.user_types("template list")
    result.expect_command_text_without("Check the old way")
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, subject=AgentRole.MAIN)
def test_the_users_own_template_stays_through_every_start(story):
    story.user_types("template create 'Our release check' --brief 'Read the changelog first.'")
    story.journal_starts_again()
    result = story.user_types("template list")
    result.expect_command_text("Our release check")
    story.expect_stack(story.agents.subject, Ready)
