"""Sets each old test beside the stories: an old test whose every line told and every stack move some story also makes is covered, and is named so it can go; one that made neither is named to be read by hand; the others are named with the lines and moves no story makes, which says the story to write first. Reads the last story run's merged record and a behaviour record of the old tests, written by a run with JOURNAL_BEHAVIOUR_RECORD=<folder>, one file per process."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORY_RECORD_FILE = ROOT / ".journal" / "runtime" / "story-record.json"


def main(behaviour_folder: str) -> int:
    stories = json.loads(STORY_RECORD_FILE.read_text())
    story_lines, story_moves = set(stories["nudge_keys"]), set(stories["walked"])
    covered, open_tests, silent = [], [], []
    recorded = {nodeid: made for path in sorted(Path(behaviour_folder).glob("*.json")) for nodeid, made in json.loads(path.read_text()).items()}
    for nodeid, made in sorted(recorded.items()):
        if not made["lines"] and not made["moves"]:
            silent.append(nodeid)
            continue
        missing = sorted({f"line {key}" for key in made["lines"]} - {f"line {key}" for key in story_lines} | set(made["moves"]) - story_moves)
        (open_tests.append((nodeid, missing)) if missing else covered.append(nodeid))
    print(f"covered by the stories: {len(covered)}")
    for nodeid in covered:
        print(f"  {nodeid}")
    print(f"made the journal tell no line and move no stack, so read by hand: {len(silent)}")
    for nodeid in silent:
        print(f"  {nodeid}")
    print(f"not covered: {len(open_tests)}")
    for nodeid, missing in open_tests:
        print(f"  {nodeid}: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
