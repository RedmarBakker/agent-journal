from journal.features.skills.feature import Skills
from journal.features.skills.skills_options import SkillsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.voices.feature import Voices
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.state_fixture import StateFixture


class SessionSkillsEnabled(StateFixture):
    """The environment has Voice and Skills enabled and no waiting messages."""

    stack = (Ready,)
    parent = NewSession
    settings = ((SkillsOptions.START_SKILLS, SkillsOptions.START_SKILLS.default),)

    def steps(self, story) -> None:
        story.user_switches_on(Voices)
        story.user_switches_on(Skills)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
