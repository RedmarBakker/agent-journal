import glob
import os
import re
import shlex
from pathlib import Path
from dataclasses import dataclass, replace

# the programs that shape a command's output at the end of a pipe, taken off so the whole output is kept and the shaping applies to what is shown
FILTERS = {"tail", "head", "grep", "egrep", "fgrep", "rg", "ag", "ack", "cut", "sort", "uniq", "wc", "tr", "column", "fold", "fmt", "nl", "less", "more", "cat", "rev", "expand", "unexpand", "paste", "colrm", "pr", "strings", "jq", "yq", "sed", "awk", "gawk", "perl"}
# a filter that writes the file in place is a command of its own, never a shaping of the output
IN_PLACE_FILTERS = {"sed", "perl", "awk", "gawk"}
IN_PLACE = re.compile(r"\s(-[a-zA-Z]*i|--in-place)")
CODE = re.compile(r"\.(py|pyi|vue|js|mjs|cjs|jsx|ts|tsx|cs|go|rs|swift|kt|kts|java|scala|php|rb|ex|exs|erl|hs|ml|clj|c|h|cc|cpp|hpp|m|mm|lua|dart|r|jl|sh|bash|zsh|fish|ps1|sql|css|scss|sass|less|html|htm|svelte|astro|json|jsonl|yaml|yml|toml|ini|cfg|xml|gradle|tf|proto|graphql|md|txt)\b")
VENDOR_FOLDERS = {"node_modules", "dist", "build", ".venv", "venv", "__pycache__", ".git", ".journal"}
JOURNAL_OWNED = (".claude/skills", ".agents/skills", ".journal")
WORKTREES = ".journal/worktrees"
LOCKS = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock", "uv.lock", "Pipfile.lock", "composer.lock"}
# a quoted word, in single quotes or in double quotes with its escapes
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")
# a word in single quotes, which the shell runs nothing inside
SINGLE_QUOTED = re.compile(r"'[^']*'")
# the operators that join the commands of one part: a pipe, a pipe of both outputs, and an or
JOINTS = ("||", "|&", "|")
SEPARATOR = re.compile(r"&&|\|\||;")


@dataclass(frozen=True)
class Part:
    """One command of a chain: whether it is the agent's own, recorded, or the shell's own wrapping, run silently; whether it runs whatever the part before it returned (after a ;) or only after a success (after a &&); whether a && follows it, so that its failure must not end a shell under set -e; and whether it is a read of the project's code that runs whole, its tail never cut. It reads its own tokens as the shell would: quotes removed, a leading comment and env assignments skipped."""

    text: str
    recorded: bool = True
    unconditional: bool = True
    guarded: bool = False
    reads_code: bool = False

    def kind(self) -> str:
        return ("R" if self.recorded else "S") + (";" if self.unconditional else "&") + ("&" if self.guarded else ";")

    def tokens(self) -> list[str]:
        try:
            split = shlex.split(self.command_text(), posix=True)
        except ValueError:
            split = self.command_text().split()
        return self.leads(split)

    def command_text(self) -> str:
        lines = self.text.split("\n")
        return "\n".join(lines[next((i for i, line in enumerate(lines) if not line.lstrip().startswith("#")), len(lines)):])

    def unquoted(self) -> str:
        return QUOTED.sub(" ", self.command_text())

    def blanked(self) -> str:
        return QUOTED.sub(" '' ", self.command_text())

    def unexpanded(self) -> str:
        return SINGLE_QUOTED.sub(" ", self.text)

    @staticmethod
    def leads(tokens: list[str]) -> list[str]:
        while tokens and "=" in tokens[0] and not tokens[0].startswith("-"):
            tokens = tokens[1:]
        return tokens

    def program(self) -> str:
        tokens = self.tokens()
        return tokens[0].rsplit("/", 1)[-1] if tokens else ""

    def is_project_cd(self) -> bool:
        tokens = self.tokens()
        return len(tokens) == 2 and tokens[0] == "cd" and self.is_project_file(tokens[1])

    def names_project_code(self, is_search: bool) -> bool:
        paths = [word for word in self.tokens()[1:] if CODE.search(word) or self.is_project_path(word) or self.is_journal_owned(word)]
        return all(self.is_project_file(word) for word in paths) and (bool(paths) or is_search and not self.touches_foreign_folder())

    def touches_foreign_folder(self) -> bool:
        return any(word.startswith(("/", "~", "..", "$")) for word in self.tokens()[1:] if not word.startswith("-"))

    def tails_forever(self) -> bool:
        return self.program() == "tail" and any(w in ("-f", "-F") or w.startswith("-") and "f" in w[1:] and not w.startswith("--") for w in self.tokens()[1:])

    @staticmethod
    def is_project_path(word: str) -> bool:
        if word.startswith(("-", "$")):
            return False
        expanded = os.path.expanduser(word)
        return Path(expanded).exists() or any(ch in word for ch in "*?{") and bool(glob.glob(expanded))

    @classmethod
    def is_code_target(cls, target: str) -> bool:
        name = os.path.basename(target.rstrip("/"))
        return cls.is_project_file(target) and (bool(CODE.search(target)) or "." not in name.lstrip("."))

    @staticmethod
    def is_journal_owned(path: str) -> bool:
        normal = os.path.normpath(path)
        return not (normal + "/").startswith(WORKTREES + "/") and any((normal + "/").startswith(owned + "/") for owned in JOURNAL_OWNED)

    @classmethod
    def is_project_file(cls, word: str) -> bool:
        if word.startswith("$"):
            return False
        root = Path.cwd().resolve()
        path = Path(os.path.normpath(os.path.expanduser(word)))
        if path.is_absolute():
            if path != root and root not in path.parents:
                return False
            parts = path.relative_to(root).parts
        else:
            if path.parts[:1] == ("..",):
                return False
            parts = path.parts
        if parts[:2] == (".journal", "worktrees"):
            parts = parts[3:]
        return not any(part in VENDOR_FOLDERS for part in parts) and not (parts and parts[-1] in LOCKS)

    def cut(self) -> str:
        if not self.recorded or self.reads_code or "<<" in self.text or self.tails_forever():
            return ""
        level, end = (1, self.text.rstrip().rindex(")")) if self.is_subshell() else (0, len(self.text))
        pipes = self.pipe_positions(level)
        first = len(pipes)
        while first > 0 and self.is_filter(self.text[pipes[first - 1] + 1:pipes[first] if first < len(pipes) else end]):
            first -= 1
        return self.text[pipes[first]:end].strip() if first < len(pipes) else ""

    @staticmethod
    def is_filter(command: str) -> bool:
        program = command.split()[:1]
        return bool(program) and program[0] in FILTERS and "-f" not in command.split() and not SEPARATOR.search(command) and not (program[0] in IN_PLACE_FILTERS and IN_PLACE.search(command))

    def is_subshell(self) -> bool:
        text = self.text.strip()
        return text.startswith("(") and text.endswith(")") and self.closing_paren(text) == len(text) - 1

    @staticmethod
    def closing_paren(text: str) -> int:
        quote, depth = "", 0
        for i, c in enumerate(text):
            if quote:
                quote = "" if c == quote else quote
            elif c in "'\"`":
                quote = c
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if not depth:
                    return i
        return -1

    def stages(self) -> list[str]:
        cuts = [-1, *self.pipe_positions(0), len(self.text)]
        return [self.text[start + 1:end].lstrip("&").strip() for start, end in zip(cuts, cuts[1:])]

    def commands(self) -> list[str]:
        joints = [(position, joint) for position, joint in self.joints(0) if self.text[position - 1:position] != ">"]
        starts = [0, *(position + len(joint) for position, joint in joints)]
        ends = [*(position for position, _ in joints), len(self.text)]
        return [self.text[start:end].lstrip("&").strip() for start, end in zip(starts, ends)]

    def pipe_positions(self, level: int) -> list[int]:
        return [position for position, joint in self.joints(level) if joint != "||"]

    def joints(self, level: int) -> list[tuple[int, str]]:
        found, quote, depth, passed = [], "", 0, -1
        for i, c in enumerate(self.text):
            if i <= passed or self.text[i - 1:i] == "\\" and quote != "'":
                continue
            if quote:
                quote = "" if c == quote else quote
            elif c in "'\"`":
                quote = c
            elif c in "({":
                depth += 1
            elif c in ")}":
                depth = max(depth - 1, 0)
            elif c == "|" and depth == level:
                joint = next(symbol for symbol in JOINTS if self.text.startswith(symbol, i))
                found, passed = [*found, (i, joint)], i + len(joint) - 1
        return found

    def cut_command(self) -> str:
        return self.cut().lstrip("| ").strip()

    def uncut(self) -> "Part":
        cut = self.cut()
        if not cut:
            return self
        position = self.text.rindex(cut)
        return replace(self, text=self.text[:position].rstrip() + self.text[position + len(cut):].strip())
