"""Reads every Bash command Claude Code ran from the session transcripts under ~/.claude/projects, leaving out the throwaway folders test runs make, anonymises each (emails, keys, tokens, passwords, addresses, home paths and the private words given made neutral) and writes the unique ones, one command a line, grouped by the command they run with a blank line between groups. Run with PYTHONPATH=src."""

import json
import re
import sys
from pathlib import Path

from journal.support.command_shape import CommandShape

PROJECTS = Path.home() / ".claude" / "projects"
HOME = str(Path.home())
USER = Path.home().name
THROWAWAY_FOLDERS = ("-private-var", "-var-folders")
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


def anonymised(line: str, private_words: list[str]) -> str:
    for pattern, stand_in in SECRETS:
        line = pattern.sub(stand_in, line)
    line = EMAIL.sub("someone@example.com", line)
    line = HOME_FOLDER.sub("~", ADDRESS.sub("10.0.0.1", line).replace(HOME, "~")).replace(USER, "user")
    for word in sorted(private_words, key=len, reverse=True):
        line = re.sub(re.escape(word), "project", line, flags=re.IGNORECASE)
    return line.strip()


def main(private_words: list[str], out: Path) -> None:
    folders = [folder for folder in PROJECTS.iterdir() if folder.is_dir() and not folder.name.startswith(THROWAWAY_FOLDERS)]
    unique = {anonymised(command, private_words) for folder in folders for transcript in folder.rglob("*.jsonl") for command in commands(transcript)} - {""}
    groups: dict[str, list[str]] = {}
    for command in unique:
        groups.setdefault(CommandShape.command_name(command) or command.split()[0], []).append(command.replace("\n", "\\n"))
    out.write_text("\n\n".join("\n".join(sorted(lines)) for _, lines in sorted(groups.items())) + "\n")
    print(f"{len(unique)} unique commands in {len(groups)} groups from {len(folders)} project folders written to {out}")


if __name__ == "__main__":
    main([word for word in sys.argv[1].split(",") if word], Path(sys.argv[2]))
