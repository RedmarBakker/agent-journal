import os
import random
from collections.abc import Callable, Iterable

import pytest

from journal.support.option import Option

# the seed a drawn sample starts from unless SCENARIO_SEED names another, so a run can be played again exactly
SEED_VARIABLE = "SCENARIO_SEED"
DEFAULT_SEED = 7


def values(choices: Iterable) -> pytest.MarkDecorator:
    """A story run once for each value, each run from a fresh journal, the value handed to the story as value."""
    chosen = list(choices)
    return pytest.mark.parametrize("value", chosen, ids=[str(choice) for choice in chosen])


# the marker of a story that must see the journal read a setting after it set it
SETTING_READ_MARK = "setting_read"
# the marker naming the state a story starts from
STARTS_FROM_MARK = "starts_from"


def values_of(option: Option) -> Callable:
    """A story run for the values of a whole-number setting worth trying, none, one, a middle and its default, and failed at its end when the journal never read the setting after the story set it."""
    default = int(option.default)
    marks = (values(sorted({0, 1, default // 2, default})), getattr(pytest.mark, SETTING_READ_MARK)(option.key))
    return lambda story: marks[1](marks[0](story))


def sample(population: Iterable[int], count: int) -> list[int]:
    """Values drawn from a range from the run's seed, the same each run until SCENARIO_SEED names another."""
    return sorted(random.Random(int(os.environ.get(SEED_VARIABLE, DEFAULT_SEED))).sample(list(population), count))


def starts_from(fixture: type) -> pytest.MarkDecorator:
    """The state a story starts from, seeded through the real path before the story's first step."""
    return getattr(pytest.mark, STARTS_FROM_MARK).with_args(fixture)
