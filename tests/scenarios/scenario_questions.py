from journal.features.questions.questions_nudges import QuestionsNudges
from tests.scenarios.builder.story_values import scenario
from tests.scenarios.state_fixtures.agent_at_work import AgentAtWork


@scenario(AgentAtWork)
def test_an_answered_question_is_told_to_the_agent(scenario):
    question = scenario.agent_asks("the footer in blue or grey?", "blue", "grey")
    scenario.user_answers(question, "grey")
    scenario.expect_agent_told(QuestionsNudges.QUESTION_ANSWERED, n=question)
