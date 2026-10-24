"""Refuses staged lines that name a word of the private list or an IP address outside the documentation, private and loopback ranges: python3 scripts/checks/private_data.py, run by the commit guard on what is staged."""
import ipaddress
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# the list lives outside the repository, so the words themselves are never published
WORDS = Path(os.environ.get("AGENT_JOURNAL_PRIVATE_WORDS", Path.home() / ".config" / "agent-journal" / "private-words"))
# an address stands apart: numbers run on from a minus sign, a point or a digit are drawing coordinates, as in an SVG path's -3.3.7.7-3.3
ADDRESS = re.compile(r"(?<![\w.-])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
DOCUMENTATION = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]


def is_public(text: str) -> bool:
    try:
        address = ipaddress.ip_address(text)
    except ValueError:
        return False
    return address.is_global and not any(address in network for network in DOCUMENTATION)


def staged_lines() -> list[tuple[str, int, str]]:
    diff = subprocess.run(["git", "diff", "--cached", "-U0", "--no-color"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    lines, name, number = [], "", 0
    for row in diff.splitlines():
        if row.startswith("+++ "):
            name = row[6:] if row.startswith("+++ b/") else ""
        elif row.startswith("@@"):
            number = int(re.search(r"\+(\d+)", row).group(1))
        elif row.startswith("+") and name:
            lines.append((name, number, row[1:]))
            number += 1
    return lines


def problems(lines: list[tuple[str, int, str]], words: list[str]) -> list[str]:
    found = []
    for name, number, text in lines:
        lowered = text.lower()
        for index, word in enumerate(words, 1):
            if word and word.lower() in lowered:
                found.append(f"{name}:{number}: private word {index} of {WORDS}")
        found += [f"{name}:{number}: the address {address} is a real machine's; use a documentation address such as 203.0.113.5" for address in ADDRESS.findall(text) if is_public(address)]
    return found


if __name__ == "__main__":
    words = [line.strip() for line in WORDS.read_text().splitlines()] if WORDS.is_file() else []
    found = problems(staged_lines(), words)
    print("\n".join(found), file=sys.stderr)
    sys.exit(1 if found else 0)
