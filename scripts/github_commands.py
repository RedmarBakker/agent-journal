"""Gathers shell commands from public GitHub projects for the classification corpus, weighted to the languages and tooling the corpus lacks: the run steps of .github/workflows files with their runs-on and shell, Dockerfile RUN lines, Makefile and justfile recipes, package.json scripts, and shell, PowerShell and batch code blocks in READMEs. Repositories are found by language through the GitHub API with the gh token, their files read from raw.githubusercontent.com; the search and API limits are waited out, and a run stopped at any point goes on where it left off. Each command is split with the journal's own splitter, secrets placeholders such as ${{ secrets.TOKEN }} kept as written, deduplicated against the corpus and against itself, and stored with its repository, language, operating system, shell and source, one JSON object a line, in github_commands.jsonl beside the corpus. measure classifies the gathered commands and prints what the classifier misses. Run with PYTHONPATH=src: python3 scripts/github_commands.py harvest <corpus folder> [count] [minutes] | measure <corpus folder>; a run given minutes stops after the query it is on when they are up, and the next goes on from there."""

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from journal.config import Config
from journal.support.chain import Chain
from journal.support.classification import UNKNOWN
from journal.support.classification_table import ClassificationTable
from journal.support.command_classifier import CommandClassifier
from journal.support.command_shape import CommandShape
from journal.support.table_schema import TableSchema

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
OUT_FILE = "github_commands.jsonl"
STATE_FILE = "github_state.json"
MEASURE_FILE = "github_measure.json"
# words that only continue a block or a list, never begin a command, and the word that closes each block a line may open
CONTINUING_WORDS = {"then", "elif", "else", "fi", "do", "done", "esac", "}", "{", "|", "-", "*", "#", "//", "&&", "||", ";;", ")"}
BLOCK_CLOSERS = {"if": "fi", "for": "done", "while": "done", "until": "done", "case": "esac"}
# the corpus files whose lines are JSON strings, one command each, deduplicated against
CORPUS_FILES = ("commands.txt", "new_commands.jsonl")
# each language with its share of the repositories searched: the ones the corpus lacks first
LANGUAGES = (("PowerShell", 6), ("C#", 6), ("Rust", 6), ("Go", 6), ("Batchfile", 4), ("Elixir", 4), ("Haskell", 4), ("Kotlin", 4), ("Swift", 4), ("Dart", 4), ("Zig", 3), ("R", 3), ("Julia", 3),
             ("F#", 2), ("Scala", 2), ("Clojure", 2), ("OCaml", 2), ("Erlang", 2), ("Nim", 2), ("Crystal", 2), ("Lua", 2), ("Perl", 2), ("C++", 3), ("C", 3), ("Java", 3), ("Ruby", 2),
             ("Nix", 2), ("Fortran", 1), ("Objective-C", 1), ("Groovy", 1), ("Python", 1), ("TypeScript", 1), ("PHP", 1))
# star ranges searched per language, so small projects are read beside the famous ones
STAR_RANGES = ("1000..*", "200..999", "50..199", "15..49")
PAGES_PER_RANGE = 2
SEARCH_PAUSE_SECONDS = 2.2
# what is left of the hourly API limit when the run waits for its reset
API_RESERVE = 40
FILES_PER_REPOSITORY = 14
# the most commands one repository gives, so no one project fills the corpus
COMMANDS_PER_REPOSITORY = 120
RAW_THREADS = 8
LONGEST_COMMAND = 2000
WORKFLOW = re.compile(r"^\.github/workflows/[^/]+\.ya?ml$")
DOCKERFILE = re.compile(r"(^|/)Dockerfile[^/]*$|\.dockerfile$", re.I)
MAKEFILE = re.compile(r"^(GNUmakefile|Makefile|makefile)$")
JUSTFILE = re.compile(r"^(justfile|Justfile|\.justfile)$")
README = re.compile(r"^README(\.md|\.markdown)?$", re.I)
# a README code block's language and the shell it stands for
BLOCK_SHELLS = {"sh": "sh", "bash": "bash", "shell": "sh", "console": "sh", "zsh": "zsh", "shell-session": "sh", "powershell": "pwsh", "pwsh": "pwsh", "ps1": "pwsh", "ps": "pwsh", "bat": "cmd", "batch": "cmd", "cmd": "cmd", "doscon": "cmd", "fish": "fish"}
FENCE = re.compile(r"^(\s*)(```|~~~)\s*([\w+-]*)")
PROMPT = re.compile(r"^(\$|>|PS [^>]*>|C:\\[^>]*>|❯|%)\s+")
WORKFLOW_KEY = re.compile(r"^(\s*)(-\s+)?([\w-]+):\s*(.*)$")
RUN_PLACEHOLDER = re.compile(r"\$\{\{.*?\}\}")
CONTINUATIONS = {"pwsh": "`", "powershell": "`", "cmd": "^"}


def token() -> str:
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=30, check=True).stdout.strip()


def fetched(url: str, headers: dict[str, str]) -> tuple[bytes, dict[str, str]]:
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
                return response.read(), dict(response.headers)
        except urllib.error.HTTPError as failure:
            if failure.code in (403, 429) and failure.headers.get("X-RateLimit-Remaining") == "0":
                wait_until(float(failure.headers.get("X-RateLimit-Reset", time.time() + 60)))
                continue
            if failure.code in (404, 409, 451):
                return b"", {}
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    return b"", {}


def wait_until(reset: float) -> None:
    seconds = max(reset - time.time(), 0) + 5
    print(f"waiting {round(seconds)} s for the API limit to reset", flush=True)
    time.sleep(seconds)


class Api:
    """The GitHub API as this script uses it: its limit read from each answer and waited out before it runs dry."""

    def __init__(self, key: str) -> None:
        self.headers = {"Authorization": f"Bearer {key}", "Accept": "application/vnd.github+json", "User-Agent": "agent-journal-corpus"}
        self.remaining, self.reset = 5000, 0.0

    def get(self, path: str) -> dict:
        if self.remaining < API_RESERVE:
            wait_until(self.reset)
        body, headers = fetched(API + path, self.headers)
        self.remaining = int(headers.get("X-RateLimit-Remaining", self.remaining))
        self.reset = float(headers.get("X-RateLimit-Reset", self.reset))
        return json.loads(body) if body else {}


def raw(repository: str, branch: str, path: str) -> str:
    body, _ = fetched(f"{RAW}/{repository}/{urllib.parse.quote(branch)}/{urllib.parse.quote(path)}", {"User-Agent": "agent-journal-corpus"})
    return body.decode(errors="replace")


# every language's first page before any language's second, so the languages share the corpus from the start
def queries() -> list[str]:
    rounds = [(stars, page) for stars in range(len(STAR_RANGES)) for page in range(1, PAGES_PER_RANGE + 1)]
    return [f"language:\"{language}\" stars:{STAR_RANGES[stars]} fork:false archived:false|{page}" for stars, page in rounds for language, share in LANGUAGES if stars < share]


def repositories(api: Api, query: str) -> list[tuple[str, str, str]]:
    text, page = query.rsplit("|", 1)
    time.sleep(SEARCH_PAUSE_SECONDS)
    found = api.get(f"/search/repositories?q={urllib.parse.quote(text)}&sort=updated&per_page=100&page={page}")
    return [(item["full_name"], item.get("default_branch") or "main", item.get("language") or "") for item in found.get("items", [])]


def chosen_files(api: Api, repository: str, branch: str) -> list[str]:
    tree = api.get(f"/repos/{repository}/git/trees/{urllib.parse.quote(branch)}?recursive=1").get("tree", [])
    paths = [entry["path"] for entry in tree if entry.get("type") == "blob"]
    wanted = [path for path in paths if WORKFLOW.match(path)][:8]
    wanted += [path for path in paths if DOCKERFILE.search(path)][:3]
    wanted += [path for path in paths if MAKEFILE.match(path) or JUSTFILE.match(path) or path == "package.json" or README.match(path)]
    return wanted[:FILES_PER_REPOSITORY]


def file_commands(path: str, text: str) -> list[tuple[str, str, str, str]]:
    if WORKFLOW.match(path):
        return workflow_commands(text)
    if DOCKERFILE.search(path):
        return dockerfile_commands(text)
    if MAKEFILE.match(path):
        return [(line, "linux", "sh", "makefile") for line in recipe_lines(text, "\t")]
    if JUSTFILE.match(path):
        return [(line, "", "sh", "justfile") for line in recipe_lines(text, " ")]
    if path == "package.json":
        return package_scripts(text)
    return readme_commands(text)


def workflow_commands(text: str) -> list[tuple[str, str, str, str]]:
    lines, found, runs_on, default_shell = text.splitlines(), [], "", ""
    for index, line in enumerate(lines):
        key = WORKFLOW_KEY.match(line)
        if not key:
            continue
        indent, name, value = len(key.group(1)) + len(key.group(2) or ""), key.group(3), key.group(4).strip()
        if name == "runs-on":
            runs_on = value or " ".join(item.strip("- ").strip() for item in lines[index + 1:index + 3])
        elif name == "shell" and "defaults" in "".join(lines[max(0, index - 3):index]):
            default_shell = value
        elif name == "run":
            shell = shell_name(step_shell(lines, index, indent) or default_shell or ("pwsh" if "windows" in runs_on.lower() else "bash"))
            body = block(lines, index, indent) if value[:1] in ("|", ">") else [value]
            found += [(command, operating_system(runs_on), shell, "workflow") for command in script_commands(body, shell)]
    return found


def shell_name(shell: str) -> str:
    return "matrix" if "${{" in shell else shell.split()[0].rsplit("/", 1)[-1] if shell.split() else ""


def step_shell(lines: list[str], index: int, indent: int) -> str:
    for line in lines[max(0, index - 12):index + 30]:
        key = WORKFLOW_KEY.match(line)
        if key and key.group(3) == "shell" and len(key.group(1)) + len(key.group(2) or "") == indent:
            return key.group(4).strip()
    return ""


def block(lines: list[str], index: int, indent: int) -> list[str]:
    body = []
    for line in lines[index + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        body.append(line)
    margin = min((len(line) - len(line.lstrip()) for line in body if line.strip()), default=0)
    return [line[margin:] for line in body]


def operating_system(runs_on: str) -> str:
    lowered = runs_on.lower()
    return next((name for name in ("windows", "macos", "ubuntu") if name in lowered), "matrix" if "${{" in lowered else "other" if lowered else "")


def script_commands(lines: list[str], shell: str) -> list[str]:
    continuation, commands, pending = CONTINUATIONS.get(shell.split()[0].lower() if shell else "", "\\"), [], ""
    for line in lines:
        stripped = line.rstrip()
        if not pending and (not stripped.strip() or stripped.lstrip().startswith(("#", "::", "REM ", "rem "))):
            continue
        if stripped.endswith(continuation):
            pending += stripped[:-1] + " "
            continue
        commands.append((pending + stripped).strip())
        pending = ""
    return [command for command in commands + ([pending.strip()] if pending.strip() else []) if kept(command)]


def kept(command: str) -> bool:
    return 1 < len(command) <= LONGEST_COMMAND and bool(RUN_PLACEHOLDER.sub("", command).strip())


def dockerfile_commands(text: str) -> list[tuple[str, str, str, str]]:
    windows = bool(re.search(r"(?im)^FROM\s+mcr\.microsoft\.com/windows", text))
    lines = [line[4:] for line in "\n".join(text.replace("\\\n", " ").splitlines()).splitlines() if line[:4].upper() == "RUN "]
    named = re.search(r'(?im)^SHELL\s+\[\s*"([^"]+)"', text)
    shell = shell_name(named.group(1)) if named else "pwsh" if windows else "sh"
    return [(command, "windows" if windows else "linux", shell, "dockerfile") for line in lines if not line.lstrip().startswith("[") for command in script_commands([line], shell)]


def recipe_lines(text: str, indent: str) -> list[str]:
    body = [line.strip().lstrip("@-+").strip() for line in text.replace("\\\n", " ").splitlines() if line.startswith(indent) and line.strip()]
    return [line for line in body if kept(line) and not line.startswith("#")]


def package_scripts(text: str) -> list[tuple[str, str, str, str]]:
    try:
        scripts = json.loads(text).get("scripts") or {}
    except (json.JSONDecodeError, AttributeError):
        return []
    return [(command, "", "sh", "package.json") for command in scripts.values() if isinstance(command, str) and kept(command)]


def readme_commands(text: str) -> list[tuple[str, str, str, str]]:
    found, shell, body = [], "", []
    for line in text.splitlines():
        fence = FENCE.match(line)
        if fence and shell == "" and not body and fence.group(3).lower() in BLOCK_SHELLS:
            shell, body = BLOCK_SHELLS[fence.group(3).lower()], []
        elif fence and shell:
            found += [(command, "windows" if shell in ("pwsh", "cmd") else "", shell, "readme") for command in script_commands(prompted(body), shell)]
            shell, body = "", []
        elif shell:
            body.append(line)
    return found


def prompted(lines: list[str]) -> list[str]:
    prompts = [PROMPT.sub("", line.strip(), count=1) for line in lines if PROMPT.match(line.strip())]
    return prompts if prompts else lines


def corpus_lines(folder: Path) -> set[str]:
    seen = set()
    for name in CORPUS_FILES:
        path = folder / name
        if path.is_file():
            seen.update(json.loads(line) for line in path.read_text(errors="replace").splitlines() if line.startswith('"'))
    out = folder / OUT_FILE
    if out.is_file():
        seen.update(json.loads(line)["line"] for line in out.read_text().splitlines() if line.strip())
    return seen


def harvest(folder: Path, wanted: int, minutes: float) -> None:
    deadline = time.time() + minutes * 60
    state_path, out = folder / STATE_FILE, folder / OUT_FILE
    state = json.loads(state_path.read_text()) if state_path.is_file() else {"queries": [], "repositories": []}
    seen, api, done = corpus_lines(folder), Api(token()), set(state["repositories"])
    written = sum(1 for _ in out.open()) if out.is_file() else 0
    with out.open("a") as stream, ThreadPoolExecutor(RAW_THREADS) as pool:
        for query in queries():
            if written >= wanted or time.time() > deadline:
                break
            if query in state["queries"]:
                continue
            for repository, branch, language in repositories(api, query):
                if repository in done or written >= wanted:
                    continue
                paths, taken = chosen_files(api, repository, branch), 0
                for path, text in zip(paths, pool.map(lambda path: raw(repository, branch, path), paths)):
                    for command, system, shell, source in file_commands(path, text):
                        if command in seen or taken >= COMMANDS_PER_REPOSITORY:
                            continue
                        taken += 1
                        seen.add(command)
                        stream.write(json.dumps({"line": command, "parts": Chain.split(command), "repository": repository, "language": language, "os": system, "shell": shell, "source": source}, ensure_ascii=False) + "\n")
                        written += 1
                done.add(repository)
                state["repositories"].append(repository)
                stream.flush()
            state["queries"].append(query)
            state_path.write_text(json.dumps(state))
            print(f"{written} commands from {len(done)} repositories after {query.split('|')[0]} page {query.split('|')[1]}, {api.remaining} API calls left this hour", flush=True)
    state_path.write_text(json.dumps(state))
    print(f"{written} commands from {len(done)} repositories written to {out}", flush=True)


def measure(folder: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    table = ClassificationTable(Config.rooted(root), TableSchema())
    classifier = CommandClassifier(table, CommandShape(table))
    rows = [json.loads(line) for line in (folder / OUT_FILE).read_text().splitlines() if line.strip()]
    parts = [(part, row) for row in rows for part in row["parts"] if not is_fragment(part)]
    unknown = [(part, row) for part, row in parts if classifier.classify(part).command_type == UNKNOWN]
    programs = Counter(program(part) for part, _ in unknown)
    shares = {key: share([row[key] for _, row in parts], [row[key] for _, row in unknown]) for key in ("language", "os", "shell", "source")}
    report = {"commands": len(rows), "parts": len(parts), "unknown_parts": len(unknown), "known_share": round(1 - len(unknown) / max(len(parts), 1), 4), "unknown_programs": programs.most_common(80), "known_share_by": shares}
    (folder / MEASURE_FILE).write_text(json.dumps(report, indent=1))
    print(f"{len(rows)} commands, {len(parts)} parts: {report['known_share']:.1%} classified; the programs most often unknown: {', '.join(f'{name} {count}' for name, count in programs.most_common(25))}")
    for key, values in shares.items():
        print(f"classified by {key}: " + ", ".join(f"{value or '?'} {known:.0%} of {count}" for value, (known, count) in sorted(values.items(), key=lambda item: -item[1][1])[:12]))


def is_fragment(part: str) -> bool:
    """A piece of a multi-line block cut out by line, or prose from a README, which no shell runs on its own: a line opening on a word that only continues a block, or opening a block it never closes."""
    words = part.split()
    if not words or words[0] in CONTINUING_WORDS:
        return True
    closing = BLOCK_CLOSERS.get(words[0])
    return closing is not None and closing not in words


def program(part: str) -> str:
    words = part.split()
    return words[0].rsplit("/", 1)[-1].rsplit("\\", 1)[-1] if words else ""


def share(all_values: list[str], unknown_values: list[str]) -> dict[str, tuple[float, int]]:
    counts, misses = Counter(all_values), Counter(unknown_values)
    return {value: (round(1 - misses[value] / count, 3), count) for value, count in counts.items()}


if __name__ == "__main__":
    corpus = Path(sys.argv[2])
    if sys.argv[1] == "harvest":
        harvest(corpus, int(sys.argv[3]) if len(sys.argv) > 3 else 100_000, float(sys.argv[4]) if len(sys.argv) > 4 else float("inf"))
    else:
        measure(corpus)
