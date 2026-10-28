from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

PLAN_CREATED = {"trigger_type": "row", "moment": "plan.created"}


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_shipped_sequence_shows_what_starts_it_and_its_triggers_are_locked(story):
    building = story.sequence_number("Building a plan")
    story.expect_row("sequences", building, {"triggers": [PLAN_CREATED]})
    story.user_sets_sequence_triggers(building, [])
    story.expect_viewer_refused("locked")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_sequence_made_with_triggers_says_what_starts_it(story):
    story.agent_runs("sequence create 'Ship it' --steps 'bump | tag' --trigger row:plan.created --trigger 'file-text:src/*.py:TODO'")
    ship = story.created_number("sequence")
    story.agent_runs(f"sequence show {ship}")
    story.expect_command_text("starts on row:plan.created, file-text:src/*.py:TODO")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_page_sets_a_phrase_trigger_and_the_users_words_start_the_sequence(story):
    story.agent_runs("sequence create 'Ship it' --steps 'bump | tag'")
    ship = story.created_number("sequence")
    story.user_sets_sequence_triggers(ship, [{"trigger_type": "phrase", "text": "ship it now"}])
    story.expect_viewer_passed()
    story.user_sends_message("ship it now")
    story.agent_reads()
    story.expect_stack(Ready, FollowingSequence)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_page_refuses_bad_triggers_in_plain_words(story):
    story.agent_runs("sequence create 'Ship it' --steps 'bump | tag'")
    ship = story.created_number("sequence")
    story.user_sets_sequence_triggers(ship, [{"trigger_type": "rows"}])
    story.expect_viewer_refused("is none of them")
    story.user_sets_sequence_triggers(ship, [{"trigger_type": "command", "pattern": "("}])
    story.expect_viewer_refused("not a regular expression")
    story.user_sets_sequence_triggers(ship, [{"trigger_type": "file"}])
    story.expect_viewer_refused("path glob")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_the_command_refuses_a_bad_trigger_in_plain_words(story):
    story.agent_runs("sequence create 'Ship it' --steps 'bump | tag'")
    ship = story.created_number("sequence")
    story.agent_runs(f"sequence edit {ship} --trigger row:plan")
    story.expect_command_text("such as plan.created")
    story.expect_stack(Ready)
