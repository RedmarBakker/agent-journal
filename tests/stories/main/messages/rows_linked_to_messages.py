from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.two_unread_messages import TwoUnreadMessages
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_tasks_filed_from_a_message_are_one_mark_naming_each_and_replies_naming_them_keep_it(story):
    message = story.user_sends_message("see the picture")
    story.agent_runs(f"task create 'look at the picture' --from {message}")
    story.expect_command_text(f"(from message {message})")
    first = story.task_number()
    story.agent_runs(f"task create 'crop it' --from {message}")
    second = story.task_number()
    story.expect_chat_marks("filed", f"Linked task {first}, task {second} from your message")
    story.agent_replies(message, f"filed it as task {first}, cropping next")
    story.expect_chat_marks("filed", f"Linked task {first}, task {second} from your message")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_created_right_after_a_reply_is_linked_to_the_message_it_answers(story):
    message = story.user_sends_message("please fix the footer")
    story.agent_creates_task("the menu")
    story.expect_chat_marks("filed")
    story.agent_replies(message, "on it")
    footer = story.agent_creates_task("the footer")
    story.expect_chat_marks("filed", f"Linked task {footer} from your message")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_priority_change_right_after_a_reply_is_never_put_down_to_the_message(story):
    menu = story.agent_creates_task("the menu")
    message = story.user_sends_message("please fix the footer")
    story.agent_replies(message, "on it")
    story.agent_runs(f"task edit {menu} --priority high")
    story.expect_chat_marks("filed")
    story.expect_stack(Ready)


@story(TwoUnreadMessages, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_made_from_one_message_and_edited_from_another_has_a_mark_under_each_and_one_mark_per_move(story):
    notes, tags = story.start.first_message, story.start.second_message
    story.agent_runs(f"task create 'write the notes' --from {notes}")
    task = story.task_number()
    story.agent_runs(f"task edit {task} --title 'write the notes and tags' --from {tags}")
    story.expect_chat_marks("filed", f"Linked task {task} from your message", f"Linked task {task} from your message")
    story.expect_chat_marks("task_moves", f"Created task {task}: write the notes", f"Edited task {task}: write the notes and tags")
    story.expect_stack(Ready)


@story(TwoUnreadMessages, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_task_created_with_from_right_after_a_reply_to_another_message_is_linked_to_the_one_it_names(story):
    footer, width = story.start.first_message, story.start.second_message
    story.agent_replies(footer, "noted")
    story.agent_runs(f"task create 'the width' --from {width}")
    story.expect_command_passed()
    story.expect_chat_marks("filed", f"Linked task {story.task_number()} from your message")
    story.expect_stack(Ready)
