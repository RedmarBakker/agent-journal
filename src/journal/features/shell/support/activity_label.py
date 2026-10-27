import re

from journal.support.chain import Chain
from journal.support.command_classifier import CommandClassifier
from journal.support.command_part import CommandPart
from journal.support.command_shape import TOKEN_PATTERN, CommandShape
from journal.support.part import Part


# the activities long enough to be watched through a reader as they run
LONG_RUNS = ("testing", "building")
# the activities that only read, search or list, which show no card of their own and are never owed a reader
READ_LABELS = frozenset({"searching", "reading", "listing", "reading history", "reading a diff", "checking git"})

# what a part that runs no command of its own is doing, as a loop's do or done is
IDLE = "running"

# the words that open a part running no program: a test in brackets, arithmetic, a group or a function's definition
SHELL_SYNTAX = re.compile(r"^(\[\[?|\(\(|\{|\}|\w+\(\)|test|#.*)$")

# the body of a loop or an if, which says what the part does
BODY = re.compile(r"^\s*(?:time\s+)?(?:for|while|until|if)\s+(.*?);\s*(?:do|then)\s+(.+?)(?:;\s*(?:done|fi)\b.*)?$", re.DOTALL)

# a loop body that only waits, whose loop is named for what it waits on
WAITING = re.compile(r"^\s*(sleep\b.*|true|:)\s*$")

# a script file a runner such as python3 or node is handed
SCRIPT_FILE = re.compile(r"\.(py|js|mjs|ts|sh|rb|pl|php)$")

# the activity of a command that runs tests
TESTING = "testing"


class ActivityLabel:
    """What one command is doing, in a word or two, as the bar and the chat show it, read from the label its classification carries: git commit is committing, pytest and php artisan test are testing; a wrapper is seen through, a loop is named for its body, a script by its runner."""

    def __init__(self, classifier: CommandClassifier, shapes: CommandShape) -> None:
        self.classifier, self.shapes = classifier, shapes

    def test_runs(self, parts: tuple[str, ...]) -> list[str]:
        return [part for part in parts if self.build(part) == TESTING]

    def is_reading(self, line: str) -> bool:
        parts = [part.text for part in Chain.parts(line)]
        return bool(parts) and all(self.build(part) in READ_LABELS or self.build(part) in (IDLE, "moving") for part in parts) and self.line_label(line) in READ_LABELS

    def line_label(self, line: str) -> str:
        labels = [label for label in (self.build(part.text) for part in Chain.parts(line)) if label not in (IDLE, "moving", "running sleep")]
        if labels[:2] == ["staging", "committing"]:
            return "committing"
        return labels[0] if labels else self.build(line)

    def chain_label(self, part: str, line: str) -> str:
        label = self.build(part)
        if label != IDLE:
            return label
        return self.build(self.shapes.chain_shape(tuple(chained.text for chained in Chain.parts(line))))

    def part_label(self, part: CommandPart) -> str:
        return part.classification.label or self.build(part.text)

    def build(self, part: str) -> str:
        shaped = self.shapes.inner(self.shapes.working(part))
        if (inner := self.classifier.unwrapped(shaped)) != shaped:
            script = self.unshelled(inner)
            return self.build(script) if script else self.classifier.row_classification(shaped).label or f"running {shaped.split()[0].rsplit('/', 1)[-1]}"
        command = shaped.split("<<", 1)[0]
        tokens = TOKEN_PATTERN.findall(command)
        arguments = [word for word in tokens if not word.startswith("-") and "=" not in word]
        runner = tokens[0].rsplit("/", 1)[-1] if tokens else ""
        is_runner = self.classifier.runs_script_file(runner)
        if is_runner and len(tokens) > 1 and (tokens[1] == "-" or CommandShape.is_inline_code(tokens[1:])):
            return f"running {runner}"
        label = self.classifier.row_classification(" ".join(tokens)).label
        if is_runner and len(arguments) > 1 and SCRIPT_FILE.search(arguments[1]):
            return label or "running a script"
        if (body := BODY.match(part)):
            return self.build(body[1]) if WAITING.match(body[2]) else self.build(body[2])
        arguments = arguments[1:] if is_runner and not label and len(arguments) > 1 else arguments
        if not arguments or SHELL_SYNTAX.match(arguments[0]):
            return IDLE
        if (redirected := self.classifier.redirected_label(runner)) and self.classifier.redirect_targets(Part(shaped).commands()[0]):
            return redirected
        return label or f"running {arguments[0]}"

    def unshelled(self, line: str) -> str:
        script = self.classifier.shell_script(line)
        if not script:
            return line
        return "" if ";" in script else script.split("&&")[-1].strip()
