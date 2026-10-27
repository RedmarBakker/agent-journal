# Runs the viewer's vitest as a process, so it is not in the default run: python3 -m pytest -q tests/viewer_chat_marks_run.py
"""The chat marks' viewer tests pass: their weights, colours, quick action, stop, fold sign, closing line, grouped runs and task line."""
import subprocess
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "src" / "web"
VITEST_SECONDS = 240
FILES = (
    "tests/chatMarkSecondRound.test.js",
    "tests/chatMarkDesign.test.js",
    "tests/dockOpen.test.js",
    "tests/markLines.test.js",
    "tests/systemCard.test.js",
    "tests/subagentMarkFailed.test.js",
    "tests/watchDockOpen.test.js",
    "tests/watchCard.test.js",
    "tests/markBarTone.test.js",
    "tests/peerBubbles.test.js",
    "tests/agentMessageSides.test.js",
    "tests/chatPresets.test.js",
    "tests/docks.test.js",
    "tests/docksDelay.test.js",
    "tests/thread.test.js",
    "tests/cardTimer.test.js",
    "tests/testRunCard.test.js",
    "tests/fitnessCard.test.js",
)


def test_the_chat_marks_viewer_tests_pass():
    run = subprocess.run([str(WEB / "node_modules" / ".bin" / "vitest"), "run", *FILES], cwd=WEB, capture_output=True, text=True, timeout=VITEST_SECONDS)
    assert run.returncode == 0, "\n".join((run.stdout + run.stderr).splitlines()[-80:])
