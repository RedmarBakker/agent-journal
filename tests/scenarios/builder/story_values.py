from collections.abc import Callable

import pytest

from journal.support.option import Option


# the marker naming the state a story starts from
STARTS_FROM_MARK = "starts_from"
# the marker naming the stack a story ends on
ENDS_IN_MARK = "ends_in"
# the marker naming a setting the user sets before the story's first step
SETTINGS_MARK = "settings"
# the marker naming the provider a story runs on, where the provider is what it tests
PROVIDER_MARK = "provider"


def starts_from(fixture: type) -> pytest.MarkDecorator:
    """The state a story starts from, seeded through the real path before the story's first step."""
    return getattr(pytest.mark, STARTS_FROM_MARK).with_args(fixture)


def settings(option: Option, value: object) -> pytest.MarkDecorator:
    """A setting the user sets through the viewer's route before the story's first step; the story fails when the journal never reads it."""
    return getattr(pytest.mark, SETTINGS_MARK).with_args(option, value)


def provider(program: type) -> pytest.MarkDecorator:
    """The provider a story runs on, Claude or Codex, only where the provider changes what the story tests; every other story runs on the VoidProvider."""
    return getattr(pytest.mark, PROVIDER_MARK).with_args(program)


def ends_in(*stack: str) -> pytest.MarkDecorator:
    """The stack a story ends on, bottom first, checked after its last step."""
    return getattr(pytest.mark, ENDS_IN_MARK).with_args(*stack)


def scenario(start: type, end: list[str] | None = None) -> Callable:
    """The state a story starts from and the stack it ends on, bottom first; with no end, the stack its start leaves the agent in."""
    marks = (getattr(pytest.mark, STARTS_FROM_MARK).with_args(start), getattr(pytest.mark, ENDS_IN_MARK).with_args(*(end if end is not None else start.stack)))
    return lambda story: marks[0](marks[1](story))
