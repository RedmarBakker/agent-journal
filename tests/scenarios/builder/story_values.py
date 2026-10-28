import os
import random
from collections.abc import Callable, Iterable

import pytest

from journal.support.option import Option

# the seed a drawn sample starts from unless SCENARIO_SEED names another, so a run can be played again exactly
SEED_VARIABLE = "SCENARIO_SEED"
DEFAULT_SEED = 7
# the option type of a setting that is on or off
SWITCH = "switch"


def values(choices: Iterable) -> pytest.MarkDecorator:
    """A story run once for each value, each run from a fresh journal, the value handed to the story as value."""
    chosen = list(choices)
    return pytest.mark.parametrize("value", chosen, ids=[str(choice) for choice in chosen])


# the marker naming the state a story starts from
STARTS_FROM_MARK = "starts_from"
# the marker naming the stack a story ends on
ENDS_IN_MARK = "ends_in"


def values_of(option: Option) -> pytest.MarkDecorator:
    """A story run for the values of a setting worth trying: a switch off and on, a whole number none, one, a middle and its default."""
    if option.option_type == SWITCH:
        return values([False, True])
    default = int(option.default)
    return values(sorted({0, 1, default // 2, default}))


def sample(population: Iterable[int], count: int) -> list[int]:
    """Values drawn from a range from the run's seed, the same each run until SCENARIO_SEED names another."""
    return sorted(random.Random(int(os.environ.get(SEED_VARIABLE, DEFAULT_SEED))).sample(list(population), count))


def starts_from(fixture: type) -> pytest.MarkDecorator:
    """The state a story starts from, seeded through the real path before the story's first step."""
    return getattr(pytest.mark, STARTS_FROM_MARK).with_args(fixture)


def ends_in(*stack: str) -> pytest.MarkDecorator:
    """The stack a story ends on, bottom first, checked after its last step."""
    return getattr(pytest.mark, ENDS_IN_MARK).with_args(*stack)


def scenario(start: type, end: list[str] | None = None) -> Callable:
    """The state a story starts from and the stack it ends on, bottom first; with no end, the stack its start leaves the agent in."""
    marks = (getattr(pytest.mark, STARTS_FROM_MARK).with_args(start), getattr(pytest.mark, ENDS_IN_MARK).with_args(*(end if end is not None else start.stack)))
    return lambda story: marks[0](marks[1](story))
