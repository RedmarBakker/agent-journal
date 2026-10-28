from journal.features.skills.feature import Skills
from journal.features.skills.skills_options import SkillsOptions
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.state_fixture import StateFixture


class SessionOpening(StateFixture):
    """The main agent's session has just started, with the start skills the journal ships unread and the overview not run."""

    stack = (Ready,)

    settings = ((SkillsOptions.START_SKILLS, SkillsOptions.START_SKILLS.default),)

    def steps(self, story) -> None:
        story.user_switches_on(Skills)
        story.agent_starts_a_session()

    def expected(self, story) -> None:
        story.expect_stack(Ready)
