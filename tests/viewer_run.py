# Runs the viewer's vitest as a process, so it is not in the default run: python3 -m pytest -q tests/viewer_run.py, or one set as tests/viewer_run.py::test_the_viewer_tests_pass[chat_marks]
"""The viewer's tests of one piece of work pass, run by vitest, which the suite's pytest cannot collect."""
import subprocess
from pathlib import Path

import pytest

WEB = Path(__file__).resolve().parents[1] / "src" / "web"
VITEST_SECONDS = 240
SETS = {
    "chat_marks": (
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
    ),
    "chat_scroll": (
        "tests/chatPointerHold.test.js",
        "tests/pointerScroll.test.js",
        "tests/following.test.js",
        "tests/chatFootFolding.test.js",
        "tests/threadFeedOptions.test.js",
    ),
    "reply_bar": (
        "tests/replyBar.test.js",
        "tests/composeInput.test.js",
    ),
    "open_in_place": (
        "tests/openInPlace.test.js",
        "tests/pressedTurn.test.js",
        "tests/subagentMarkFailed.test.js",
        "tests/chatFootFolding.test.js",
    ),
    "task_board": (
        "tests/tasksDialog.test.js",
        "tests/wholePlans.test.js",
    ),
    "figure_sleep": (
        "tests/figureState.test.js",
        "tests/figureVisible.test.js",
        "tests/figurePerches.test.js",
        "tests/figureParcels.test.js",
    ),
}


@pytest.mark.parametrize("name", SETS)
def test_the_viewer_tests_pass(name: str):
    run = subprocess.run([str(WEB / "node_modules" / ".bin" / "vitest"), "run", *SETS[name]], cwd=WEB, capture_output=True, text=True, timeout=VITEST_SECONDS)
    assert run.returncode == 0, "\n".join((run.stdout + run.stderr).splitlines()[-80:])
