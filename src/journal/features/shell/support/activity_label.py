import re

from journal.support.chain import Chain
from journal.support.command_shape import RUNNERS, TOKEN_PATTERN, CommandShape


VERBS: dict[str, str | dict] = {"git": {"commit": "committing", "push": "pushing", "pull": "pulling", "add": "staging", "checkout": "switching branch", "merge": "merging", "rebase": "rebasing", "status": "checking git", "diff": "reading a diff", "log": "reading history"},
         "pytest": "testing", "phpunit": "testing", "pest": "testing", "php": {"artisan": {"test": "testing", "": "running artisan"}}, "npm": {"test": "testing", "run": {"build": "building", "test": "testing", "": "running a script"}, "install": "installing", "ci": "installing"}, "vitest": "testing", "vite": {"build": "building", "": "running vite"},
         "npx": {"vitest": "testing", "vite": {"build": "building", "": "running vite"}, "": "running npx"}, "pip": "installing", "pip3": "installing", "make": "building",
         "cargo": {"build": "building", "test": "testing", "run": "running"}, "docker": "running docker", "gh": "on github", "journal": {"suite": "testing", "": "journalling"}, "cd": "moving", "ls": "listing", "cat": "reading", "sed": "reading", "grep": "searching", "rg": "searching", "find": "searching", "curl": "fetching"}


# the flags that take the word after them as their value, as npm --prefix src/web, so that word is no part of what the command does
VALUED_FLAGS = frozenset({"--prefix", "-C", "--cwd"})


# the activities long enough to be watched through a reader as they run
LONG_RUNS = ("testing", "building")


# what a part that runs no command of its own is doing, as a loop's do or done is
IDLE = "running"

# the activity of a command that runs tests
TESTING = "testing"

class ActivityLabel:
    """What one command is doing, in a word or two, as the bar and the chat show it: git commit is committing, pytest and php artisan test are testing; the words are followed as deep as the table names them."""

    @classmethod
    def test_runs(cls, parts: tuple[str, ...]) -> list[str]:
        return [part for part in parts if cls.build(part) == TESTING]

    @classmethod
    def chain_label(cls, part: str, line: str) -> str:
        label = cls.build(part)
        if label != IDLE:
            return label
        return cls.build(CommandShape.chain_shape(tuple(chained.text for chained in Chain.parts(line))))

    @classmethod
    def build(cls, part: str) -> str:
        tokens = TOKEN_PATTERN.findall(CommandShape.inner(CommandShape.working(part)).split("<<", 1)[0])
        arguments = [w for index, w in enumerate(tokens) if not w.startswith("-") and "=" not in w and (index == 0 or tokens[index - 1] not in VALUED_FLAGS)]
        arguments = arguments[1:] if arguments and arguments[0] in RUNNERS and len(arguments) > 1 else arguments
        if not arguments:
            return IDLE
        fallback = f"running {arguments[0]}"
        verb = VERBS.get(arguments[0].rsplit("/", 1)[-1])
        for word in arguments[1:]:
            if not isinstance(verb, dict):
                break
            verb = verb.get(word, verb.get("", fallback))
        if isinstance(verb, dict):
            verb = verb.get("", fallback)
        return verb or fallback
