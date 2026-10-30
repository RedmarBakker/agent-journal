import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ("src/journal", "src/supervisor", "src/sync_server")
# the one file that turns a version into a release tag
TAG_MAKER = "src/journal/support/release.py"
HAND_WRITTEN_TAG = re.compile(r"""f["']v\{|["']v["']\s*\+|download/v\{|refs/tags/v\{""")


def problems() -> list[str]:
    """Every place a version is written into a release tag by hand, outside Release.tagged: a tag spelled without its v asks for a release or an image that does not exist."""
    found = []
    for package in PACKAGES:
        for path in sorted((ROOT / package).rglob("*.py")):
            name = str(path.relative_to(ROOT))
            if name == TAG_MAKER:
                continue
            found += [f"{name}:{number}: a release tag written by hand; make it with Release.tagged(version) or Release.major_prefix(major)"
                      for number, line in enumerate(path.read_text().splitlines(), 1) if HAND_WRITTEN_TAG.search(line)]
    return found


if __name__ == "__main__":
    lines = problems()
    print("\n".join(lines), file=sys.stderr)
    sys.exit(1 if lines else 0)
