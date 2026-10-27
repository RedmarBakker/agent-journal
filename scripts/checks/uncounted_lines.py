import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREQUENCY_FILE = ROOT / "tests" / "nudge_frequency.json"
FREEZE = "NUDGE_FREQUENCY_FREEZE=1 python3 -m pytest tests/simulation_run.py -k frozen_with_their_class"


def uncounted() -> list[str]:
    """The keys of the lines the journal registers that the frozen frequency file has never counted, so their length budget is a guess until the long runs count them again."""
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
    from scripts.nudge_words import registered
    counted = json.loads(FREQUENCY_FILE.read_text()) if FREQUENCY_FILE.is_file() else {}
    return sorted(nudge.key for nudge in registered() if nudge.key not in counted)


if __name__ == "__main__":
    keys = uncounted()
    if keys:
        print(f"warning: {len(keys)} lines are not counted in tests/nudge_frequency.json, such as {', '.join(keys[:3])}; count them with: {FREEZE}")
