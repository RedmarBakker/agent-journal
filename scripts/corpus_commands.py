"""Reads every Bash command Claude Code ran from the session transcripts under ~/.claude/projects and every shell command Codex ran from its sessions under ~/.codex/sessions, its bash -lc wrapper taken off, leaving out the throwaway folders test runs make, anonymises each (emails, keys, tokens, passwords, addresses, home paths and the private words given made neutral) and writes the unique ones, one command a line as a JSON string, so a typed \\n and a real newline stay apart, grouped by the command they run with a blank line between groups. Run with PYTHONPATH=src."""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from journal.providers.codex import Codex
from journal.support.chain import Chain
from journal.config import Config
from journal.support.classification_table import ClassificationTable
from journal.support.table_schema import TableSchema
from journal.support.command_shape import CommandShape
from journal.support.part import Part

PROJECTS = Path.home() / ".claude" / "projects"
HOME = str(Path.home())
USER = Path.home().name
THROWAWAY_FOLDERS = ("-private-var", "-var-folders")
PROJECT_COUNTS = "projects.json"
SUBCOMMAND_WORD = re.compile(r"[a-z][a-z-]{1,19}")
CODEX_SESSIONS = Path.home() / ".codex" / "sessions"
CODEX_THROWAWAY_FOLDERS = ("/private/var", "/var/folders", "/private/tmp", "/tmp")
# Codex's exec tool runs a script whose tools.exec_command({cmd: "..."}) calls hold the shell lines, as JavaScript string literals
CODEX_SCRIPT_COMMAND = re.compile(r'exec_command\(\{\s*cmd:\s*("(?:\\.|[^"\\])*")')
# a JavaScript escape JSON reads too keeps its backslash; any other, such as \$ or \', stands for its character
ESCAPE = re.compile(r"\\(.)", re.S)
JSON_ESCAPES = set('"\\/bfnrtu')
# each pattern of a secret and what stands in for it
SECRETS = (
    (re.compile(r"\b(gh[pousr]_)[A-Za-z0-9]{20,}"), r"\1EXAMPLE"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "github_pat_EXAMPLE"),
    (re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}"), "sk-EXAMPLE"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "xoxb-EXAMPLE"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AKIAEXAMPLE"),
    (re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{8,}"), r"\1 EXAMPLE-TOKEN"),
    (re.compile(r"(?i)\b((?:[A-Z0-9_]*_)?(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key|client[_-]?secret)[A-Z0-9_]*)(\s*[=:]\s*|\s+)(['\"]?)[^\s'\"&|;]+\3"), r"\1\2\3EXAMPLE\3"),
    (re.compile(r"(--(?:password|token|secret|api-key|key))(=|\s+)(['\"]?)[^\s'\"]+\3"), r"\1\2\3EXAMPLE\3"),
    (re.compile(r"(://[^/\s:@]+):[^@\s/]+@"), r"\1:EXAMPLE@"),
    (re.compile(r"-----BEGIN [A-Z ]*KEY-----.*?-----END [A-Z ]*KEY-----", re.S), "-----BEGIN KEY-----EXAMPLE-----END KEY-----"),
    (re.compile(r"\b(?=[A-Za-z0-9+/_-]*[a-z])(?=[A-Za-z0-9+/_-]*[A-Z])(?=[A-Za-z0-9+/_-]*\d)[A-Za-z0-9+/_-]{40,}={0,2}"), "EXAMPLE-KEY"),
)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ADDRESS = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
# a home folder of any user, which the HOME of the one who ran the corpus does not cover
HOME_FOLDER = re.compile(r"/(?:Users|home)/[^/\s'\"]*")


def commands(transcript: Path) -> list[str]:
    found = []
    for raw in transcript.read_text(errors="replace").splitlines():
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        found.extend(block["input"]["command"] for block in content if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Bash" and isinstance(block.get("input", {}).get("command"), str))
    return found


# the folder a Codex session ran in and the shell lines it ran; none for a session in a throwaway folder
def codex_session(session: Path) -> tuple[str, list[str]]:
    found, folder = [], ""
    for raw in session.read_text(errors="replace").splitlines():
        try:
            payload = json.loads(raw).get("payload") or {}
        except json.JSONDecodeError:
            continue
        folder = str(payload.get("cwd", "")) if payload.get("type") == "session_meta" else folder
        if folder.startswith(CODEX_THROWAWAY_FOLDERS):
            return folder, []
        found += codex_call_commands(payload) if payload.get("type") in ("function_call", "custom_tool_call") else []
    return folder, found


def codex_call_commands(payload: dict) -> list[str]:
    script = str(payload.get("arguments") or payload.get("input") or "")
    if payload.get("name") == "exec":
        return [json.loads(ESCAPE.sub(lambda escape: escape.group(0) if escape.group(1) in JSON_ESCAPES else escape.group(1), literal)) for literal in CODEX_SCRIPT_COMMAND.findall(script)]
    if payload.get("name") in ("exec_command", "shell"):
        arguments = json.loads(script)
        return [Codex.shell_line(arguments.get("cmd", arguments.get("command", "")))]
    return []


def anonymised(line: str, private_words: list[str]) -> str:
    for pattern, stand_in in SECRETS:
        line = pattern.sub(stand_in, line)
    line = EMAIL.sub("someone@example.com", line)
    line = HOME_FOLDER.sub("~", ADDRESS.sub("10.0.0.1", line).replace(HOME, "~")).replace(USER, "user")
    for word in sorted(private_words, key=len, reverse=True):
        line = re.sub(re.escape(word), "project", line, flags=re.IGNORECASE)
    return line.strip()


def refused_inside_repository(out: Path) -> None:
    repository, journal = Path(__file__).resolve().parents[1], Path(__file__).resolve().parents[1] / ".journal"
    target = out.resolve()
    if target.is_relative_to(repository) and not target.is_relative_to(journal):
        raise SystemExit(f"the corpus holds commands from every project on this machine and never enters the repository: write it under {journal}, not {target}")


def main(private_words: list[str], out: Path) -> None:
    refused_inside_repository(out)
    folders = [folder for folder in PROJECTS.iterdir() if folder.is_dir() and not folder.name.startswith(THROWAWAY_FOLDERS)]
    by_project: dict[str, list[str]] = defaultdict(list)
    for folder in folders:
        by_project[folder.name] += [command for transcript in folder.rglob("*.jsonl") for command in commands(transcript)]
    codex = [codex_session(session) for session in CODEX_SESSIONS.rglob("*.jsonl")]
    for project, found in codex:
        by_project[project] += found
    unique = {anonymised(command, private_words) for found in by_project.values() for command in found} - {""}
    groups: dict[str, list[str]] = {}
    table = ClassificationTable(Config.rooted(Path(__file__).resolve().parents[1]), TableSchema())
    shapes = CommandShape(table)
    for command in unique:
        groups.setdefault(shapes.command_name(command) or command.split()[0], []).append(json.dumps(command, ensure_ascii=False))
    out.write_text("\n\n".join("\n".join(sorted(lines)) for _, lines in sorted(groups.items())) + "\n")
    out.with_name(PROJECT_COUNTS).write_text(json.dumps(project_counts(by_project, table), indent=1, sort_keys=True) + "\n")
    print(f"{len(unique)} unique commands in {len(groups)} groups from {len(folders)} project folders and {sum(len(found) for _, found in codex)} Codex commands written to {out}")


# how many projects ran each program, and each program with its first word after it, read from every part of every command; a fixture
# ships only what several projects ran, since a project's own scripts, make targets and npm script names give the project away
def project_counts(by_project: dict[str, list[str]], table: ClassificationTable) -> dict[str, int]:
    counts: Counter = Counter()
    for found in by_project.values():
        counts.update({key for command in found for part in Chain.split(command) for key in program_keys(part, table)})
    return dict(counts)


def program_keys(part: str, table: ClassificationTable) -> list[str]:
    words = table.unwrapped(Part(part).tokens())
    program = words[0].rsplit("/", 1)[-1] if words else ""
    subcommand = words[1] if len(words) > 1 and SUBCOMMAND_WORD.fullmatch(words[1]) else ""
    return [key for key in (program, f"{program} {subcommand}" if subcommand else "") if key]


if __name__ == "__main__":
    main([word for word in sys.argv[1].split(",") if word], Path(sys.argv[2]))
