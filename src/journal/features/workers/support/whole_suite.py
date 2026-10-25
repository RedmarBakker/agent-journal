from journal.features.workers.support.tool_use_counts import TEST_COMMANDS

# words that run a part of the suite, by name or by what failed last
SELECTING_WORDS = ("-k", "-m", "--deselect", "--lf", "--last-failed")


class WholeSuite:
    """Whether a command runs the project's whole test suite: one of the test commands followed by flags alone, with no test file, test id or -k naming a part of it."""

    @staticmethod
    def is_run(command: str) -> bool:
        line = next(iter(command.strip().splitlines()), "")
        prefix = next((test for test in TEST_COMMANDS if line == test or line.startswith(f"{test} ")), None)
        return prefix is not None and not any(word in SELECTING_WORDS or not (word.startswith("-") or word.isdigit()) for word in line[len(prefix):].split())
