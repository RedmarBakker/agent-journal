import re

from journal.support.chain import Chain
from journal.support.command_shape import RUNNERS, TOKEN_PATTERN, CommandShape


VERBS: dict[str, str | dict] = {"git": {"commit": "committing", "push": "pushing", "pull": "pulling", "add": "staging", "checkout": "switching branch", "merge": "merging", "rebase": "rebasing", "status": "checking git", "diff": "reading a diff", "show": "reading a diff", "log": "reading history", "rev-list": "reading history", "grep": "searching", "ls-files": "listing", "switch": "switching branch", "tag": "tagging", "branch": "listing", "fetch": "fetching", "ls-remote": "checking git", "rev-parse": "checking git"},
         "pytest": "testing", "phpunit": "testing", "pest": "testing", "php": {"artisan": {"test": "testing", "": "running artisan"}}, "npm": {"test": "testing", "run": {"build": "building", "test": "testing", "": "running a script"}, "install": "installing", "ci": "installing"}, "vitest": "testing", "vite": {"build": "building", "": "running vite"},
         "npx": {"vitest": "testing", "vite": {"build": "building", "": "running vite"}, "": "running npx"}, "pip": "installing", "pip3": "installing", "make": "building",
         "cargo": {"build": "building", "test": "testing", "run": "running"}, "go": {"test": "testing", "build": "building", "": "running go"}, "pnpm": {"test": "testing", "build": "building", "install": "installing", "": "running a script"}, "yarn": {"test": "testing", "build": "building", "install": "installing", "": "running a script"}, "docker": "running docker", "gh": "on github", "journal": {"suite": "testing", "": "journalling"}, "cd": "moving", "ls": "listing", "cat": "reading", "cut": "reading", "sed": "reading", "head": "reading", "tail": "reading", "grep": "searching", "rg": "searching", "find": "searching", "curl": "fetching"}


# the flags that take the word after them as their value, as npm --prefix src/web, so that word is no part of what the command does
VALUED_FLAGS = frozenset({"--prefix", "-C", "--cwd"})


# the activities long enough to be watched through a reader as they run
LONG_RUNS = ("testing", "building")



# what a part that runs no command of its own is doing, as a loop's do or done is
IDLE = "running"

# the words that open a part running no program: a test in brackets, arithmetic, a group or a function's definition
SHELL_SYNTAX = re.compile(r"^(\[\[?|\(\(|\{|\}|\w+\(\)|test|#.*)$")

# the body of a loop or an if, which says what the part does
BODY = re.compile(r"^\s*(?:time\s+)?(?:for|while|until|if)\s+(.*?);\s*(?:do|then)\s+(.+?)(?:;\s*(?:done|fi)\b.*)?$", re.DOTALL)

# a loop body that only waits, whose loop is named for what it waits on
WAITING = re.compile(r"^\s*(sleep\b.*|true|:)\s*$")

# a script whose name says it runs the tests
TEST_SCRIPT = re.compile(r"(^|/)(tests?|suite)[\w.-]*\.(sh|py)$")

# a script file a runner such as python3 or node is handed
SCRIPT_FILE = re.compile(r"\.(py|js|mjs|ts|sh|rb|pl|php)$")

# a sed that changes its files in place, and a cat that writes a file, which neither read
EDITING = re.compile(r"^\s*(sed\b.*\s-i\b|perl\b.*\s-\w*i)")

# a sed that only prints chosen lines, which reads its file; any other sed transforms what it is given
PRINTING_SED = re.compile(r"^\s*sed\b.*\s-n\b")
WRITING = re.compile(r"^\s*cat\b[^|]*(?<![0-9&])>(?!&|\s*/dev/null)")

# the activity of a command that runs tests
TESTING = "testing"
# a program that does a job of its own when it is given no word after it
BARE_RUNS = {"yarn": "installing"}

class ActivityLabel:
    """What one command is doing, in a word or two, as the bar and the chat show it: git commit is committing, pytest and php artisan test are testing; the words are followed as deep as the table names them."""

    @classmethod
    def test_runs(cls, parts: tuple[str, ...]) -> list[str]:
        return [part for part in parts if cls.build(part) == TESTING]

    @classmethod
    def line_label(cls, line: str) -> str:
        labels = [label for label in (cls.build(part.text) for part in Chain.parts(line)) if label not in (IDLE, "moving", "running sleep")]
        if labels[:2] == ["staging", "committing"]:
            return "committing"
        return labels[0] if labels else cls.build(line)

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
        runner = tokens[0].rsplit("/", 1)[-1] if tokens else ""
        if runner in RUNNERS and len(tokens) > 1 and tokens[1] in ("-c", "-"):
            return f"running {runner}"
        if runner in RUNNERS and len(arguments) > 1 and SCRIPT_FILE.search(arguments[1]):
            return TESTING if TEST_SCRIPT.search(arguments[1]) else "running a script"
        arguments = arguments[1:] if arguments and arguments[0].rsplit("/", 1)[-1] in RUNNERS and len(arguments) > 1 else arguments
        if arguments and TEST_SCRIPT.search(arguments[0]):
            return TESTING
        if (body := BODY.match(part)):
            return cls.build(body[1]) if WAITING.match(body[2]) else cls.build(body[2])
        if not arguments or SHELL_SYNTAX.match(arguments[0]):
            return IDLE
        if EDITING.match(part):
            return "editing"
        if arguments[0] == "sed" and not PRINTING_SED.match(part):
            return "running sed"
        if WRITING.match(part):
            return "writing a file"
        if len(arguments) == 1 and arguments[0] in BARE_RUNS:
            return BARE_RUNS[arguments[0]]
        fallback = f"running {arguments[0]}"
        verb = VERBS.get(arguments[0].rsplit("/", 1)[-1])
        for word in arguments[1:]:
            if not isinstance(verb, dict):
                break
            verb = verb.get(word, verb.get("", fallback))
        if isinstance(verb, dict):
            verb = verb.get("", fallback)
        return verb or fallback
