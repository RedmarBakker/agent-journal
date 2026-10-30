from journal.features.questions.states.waiting import Waiting
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_question_names_the_agents_recommended_choice_first_and_marked(story):
    result = story.agent_runs(story.agents.subject, "question ask 'which footer?' --options 'The agent writes the short one' 'The agent writes the long one' --recommend 'The agent writes the long one'")
    result.expect_command_passed()
    result.expect_command_lines_in_order("1. The agent writes the long one (recommended)", "2. The agent writes the short one")
    result = story.user_opens("/journal/questions")
    result.expect_viewer_rows("rows", "recommended", ["The agent writes the long one"])
    result.expect_viewer_rows("rows", "options", [["The agent writes the long one", "The agent writes the short one"]])
    story.expect_stack(story.agents.subject, Ready, Waiting)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_a_recommendation_that_is_none_of_the_choices_is_refused(story):
    result = story.agent_runs(story.agents.subject, "question ask 'which footer?' --options 'The agent writes the short one' 'The agent writes the long one' --recommend 'The agent writes both'")
    result.expect_command_refused()
    result.expect_command_text("one of the choices")
    story.expect_stack(story.agents.subject, Ready)
