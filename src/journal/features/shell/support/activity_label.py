import re

from journal.support.chain import Chain
from journal.support.command_shape import RUNNERS, TOKEN_PATTERN, CommandShape
from journal.features.shell.support.command_wrappers import CommandWrappers


# the activity of a linter, a formatter's check or a type checker
CHECKING = "checking code"
VERBS: dict[str, str | dict] = {"git": {"commit": "committing", "push": "pushing", "pull": "pulling", "add": "staging", "checkout": "switching branch", "merge": "merging", "rebase": "rebasing", "status": "checking git", "diff": "reading a diff", "show": "reading a diff", "log": "reading history", "rev-list": "reading history", "grep": "searching", "ls-files": "listing", "switch": "switching branch", "tag": "tagging", "branch": "listing", "fetch": "fetching", "ls-remote": "checking git", "rev-parse": "checking git"},
         "pytest": "testing", "phpunit": "testing", "pest": "testing", "php": {"artisan": {"test": "testing", "": "running artisan"}}, "npm": {"test": "testing", "run": {"build": "building", "test": "testing", "lint": CHECKING, "typecheck": CHECKING, "": "running a script"}, "install": "installing", "ci": "installing"}, "vitest": "testing", "vite": {"build": "building", "": "running vite"},
         "pip": "installing", "pip3": "installing", "make": {"test": "testing", "check": "testing", "lint": CHECKING, "install": "installing", "": "building"},
         "cargo": {"build": "building", "check": "building", "test": "testing", "nextest": "testing", "clippy": CHECKING, "fmt": CHECKING, "fetch": "installing", "run": "running cargo"}, "go": {"test": "testing", "build": "building", "vet": CHECKING, "mod": {"tidy": "installing", "download": "installing", "": "running go"}, "": "running go"}, "pnpm": {"test": "testing", "build": "building", "install": "installing", "i": "installing", "add": "installing", "run": {"build": "building", "test": "testing", "lint": CHECKING, "": "running a script"}, "vitest": "testing", "jest": "testing", "eslint": CHECKING, "lint": CHECKING, "": "running a script"}, "yarn": {"test": "testing", "build": "building", "install": "installing", "add": "installing", "lint": CHECKING, "tsc": CHECKING, "": "running a script"}, "docker": {"build": "building", "compose": {"build": "building", "": "running docker"}, "": "running docker"}, "gh": "on github", "journal": {"suite": "testing", "": "journalling"}, "cd": "moving", "ls": "listing", "cat": "reading", "cut": "reading", "less": "reading", "more": "reading", "sed": "reading", "head": "reading", "tail": "reading", "grep": "searching", "rg": "searching", "find": "searching", "curl": "fetching",
         "wget": "fetching", "gotestsum": "testing", "tox": "testing", "nox": "testing", "jest": "testing", "mocha": "testing", "ava": "testing", "karma": {"start": "testing", "": "running karma"},
         "cypress": {"run": "testing", "": "running cypress"}, "playwright": {"test": "testing", "": "running playwright"}, "rspec": "testing", "unittest": "testing", "ctest": "testing",
         "cmake": "building", "ninja": "building", "webpack": "building", "esbuild": "building", "rollup": "building", "tsup": "building", "gcc": "building", "g++": "building", "clang": "building", "javac": "building",
         "gradle": {"test": "testing", "check": "testing", "build": "building", "assemble": "building", "assembleDebug": "building", "assembleRelease": "building", "": "running gradle"},
         "gradlew": {"test": "testing", "check": "testing", "build": "building", "assemble": "building", "assembleDebug": "building", "assembleRelease": "building", "": "running gradle"},
         "mvn": {"test": "testing", "verify": "testing", "package": "building", "compile": "building", "install": "building", "clean": {"test": "testing", "verify": "testing", "": "building"}, "dependency:resolve": "installing", "": "running mvn"},
         "sbt": {"test": "testing", "testOnly": "testing", "compile": "building", "": "running sbt"}, "bazel": {"test": "testing", "build": "building", "": "running bazel"},
         "dotnet": {"build": "building", "publish": "building", "test": "testing", "restore": "installing", "format": CHECKING, "": "running dotnet"},
         "mix": {"test": "testing", "compile": "building", "deps.get": "installing", "format": CHECKING, "": "running mix"}, "rebar3": {"compile": "building", "eunit": "testing", "ct": "testing", "": "running rebar3"},
         "rake": {"test": "testing", "spec": "testing", "": "running rake"}, "rails": {"test": "testing", "test:system": "testing", "": "running rails"}, "bundle": {"install": "installing", "": "running bundle"},
         "composer": {"install": "installing", "require": "installing", "update": "installing", "": "running composer"}, "pipx": "installing", "gem": {"install": "installing", "": "running gem"},
         "uv": {"sync": "installing", "add": "installing", "lock": "installing", "pip": {"install": "installing", "": "running uv"}, "": "running uv"}, "poetry": {"install": "installing", "add": "installing", "": "running poetry"},
         "swift": {"build": "building", "test": "testing", "": "running swift"}, "xcodebuild": {"test": "testing", "": "building"},
         "flutter": {"build": "building", "test": "testing", "pub": {"get": "installing", "": "running flutter"}, "": "running flutter"}, "dart": {"compile": "building", "test": "testing", "analyze": CHECKING, "pub": {"get": "installing", "": "running dart"}, "": "running dart"},
         "deno": {"test": "testing", "compile": "building", "": "running deno"}, "bun": {"test": "testing", "install": "installing", "add": "installing", "build": "building", "run": {"build": "building", "test": "testing", "": "running a script"}, "": "running bun"},
         "zig": {"build": "building", "": "running zig"}, "nix": {"build": "building", "": "running nix"}, "just": {"test": "testing", "lint": CHECKING, "build": "building", "": "running just"}, "task": {"test": "testing", "lint": CHECKING, "build": "building", "": "running task"},
         "brew": {"install": "installing", "": "running brew"}, "apt-get": {"install": "installing", "update": "installing", "": "running apt-get"}, "apt": {"install": "installing", "update": "installing", "": "running apt"},
         "dnf": {"install": "installing", "": "running dnf"}, "yum": {"install": "installing", "": "running yum"},
         "ruff": CHECKING, "mypy": CHECKING, "pyright": CHECKING, "flake8": CHECKING, "pylint": CHECKING, "black": CHECKING, "isort": CHECKING, "bandit": CHECKING, "eslint": CHECKING, "prettier": CHECKING,
         "stylelint": CHECKING, "biome": CHECKING, "tsc": CHECKING, "shellcheck": CHECKING, "hadolint": CHECKING, "golangci-lint": CHECKING, "gofmt": CHECKING, "rubocop": CHECKING, "phpstan": CHECKING, "psalm": CHECKING,
         "php-cs-fixer": CHECKING, "swiftlint": CHECKING, "ktlint": CHECKING, "detekt": CHECKING, "yamllint": CHECKING, "markdownlint": CHECKING}


# the flags that take the word after them as their value, as npm --prefix src/web, so that word is no part of what the command does
VALUED_FLAGS = frozenset({"--prefix", "-C", "--cwd", "-pl", "--filter"})


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
WRITING = re.compile(r"^\s*(?:(?:cat|echo|printf)\b[^|]*(?<![0-9&])>(?!&|\s*/dev/null)|tee\s+(?!-)\S)")

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
        shaped = CommandShape.inner(CommandShape.working(part))
        if (inner := CommandWrappers.inner(shaped)) != shaped:
            return cls.build(inner)
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
            verb = verb.get(word.strip("'\""), verb.get(word.split(":")[0], verb.get("", fallback)))
        if isinstance(verb, dict):
            verb = verb.get("", fallback)
        return verb or fallback
