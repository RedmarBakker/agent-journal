import pytest

from journal.support.agent_role import AgentRole
from journal.support.option import Option


# the marker naming the state a story starts from and whose point of view it takes
START_MARK = "starts_from"
# the marker naming a setting the user sets before the story's first step
SETTINGS_MARK = "settings"
# the marker naming the provider a story runs on, where the provider is what it tests
PROVIDER_MARK = "provider"
def setting(option: Option, value: object) -> pytest.MarkDecorator:
    return getattr(pytest.mark, SETTINGS_MARK).with_args(option, value)


def provider(program: type) -> pytest.MarkDecorator:
    return getattr(pytest.mark, PROVIDER_MARK).with_args(program)


def story(fixture: type, subject: AgentRole) -> pytest.MarkDecorator:
    return getattr(pytest.mark, START_MARK).with_args(fixture, subject)
