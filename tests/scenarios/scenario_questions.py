from journal.features.questions.questions_nudges import QuestionsNudges
from tests.scenarios.builder.story_values import starts_from
from tests.scenarios.state_fixtures.task_in_hand import TaskInHand


@starts_from(TaskInHand)
def test_an_answered_question_is_told_to_the_agent(scenario):
    question = scenario.agent_asks("the footer in blue or grey?", "blue", "grey")
    scenario.user_answers(question, "grey")
    scenario.expect_agent_told(QuestionsNudges.QUESTION_ANSWERED, n=question)
