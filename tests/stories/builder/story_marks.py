from collections.abc import Callable

import pytest

from journal.support.option import Option


# the marker naming the state a story starts from
START_MARK = "starts_from"
# the marker naming the stack a story ends on
END_MARK = "ends_in"
# the marker naming a setting the user sets before the story's first step
SETTINGS_MARK = "settings"
# the marker naming the provider a story runs on, where the provider is what it tests
PROVIDER_MARK = "provider"


def setting(option: Option, value: object) -> pytest.MarkDecorator:
    return getattr(pytest.mark, SETTINGS_MARK).with_args(option, value)


def provider(program: type) -> pytest.MarkDecorator:
    return getattr(pytest.mark, PROVIDER_MARK).with_args(program)


def story(start: type, end: list[type] | None = None) -> Callable:
    marks = (getattr(pytest.mark, START_MARK).with_args(start), getattr(pytest.mark, END_MARK).with_args(*(end if end is not None else start.stack)))
    return lambda story: marks[0](marks[1](story))
