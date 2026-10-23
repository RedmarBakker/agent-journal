from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class ThreadSample:
    """What a sampler saw: how often each working thread was in each function, how often each function was on a working stack with what it calls, and how many looks it took."""

    busy_functions: Counter
    stack_functions: Counter
    sample_count: int
