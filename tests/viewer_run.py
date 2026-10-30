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
    "task_menus": (
        "tests/taskMoreMenu.test.js",
        "tests/tasksDialog.test.js",
        "tests/taskWorkerMark.test.js",
        "tests/wholePlans.test.js",
    ),
    "mark_groups": (
        "tests/thread.test.js",
        "tests/agentBrief.test.js",
        "tests/systemCard.test.js",
        "tests/markLines.test.js",
        "tests/chatMarkSecondRound.test.js",
        "tests/chatMarkDesign.test.js",
    ),
    "dock_runs": (
        "tests/watchDockOpen.test.js",
        "tests/docks.test.js",
        "tests/docksDelay.test.js",
        "tests/chatMarkSecondRound.test.js",
    ),
    "terminal": (
        "tests/terminalRefused.test.js",
    ),
    "memory_inspector": (
        "tests/memoryInspector.test.js",
    ),
    "questions": (
        "tests/questionClose.test.js",
    ),
    "developer": (
        "tests/developerPanel.test.js",
    ),
    "services": (
        "tests/settingsServices.test.js",
    ),
    "settings_organization": (
        "tests/settingsOrganization.test.js",
        "tests/organizationRoutes.test.js",
        "tests/organizationStates.test.js",
        "tests/route.test.js",
        "tests/settingsCatalog.test.js",
        "tests/settingsSave.test.js",
    ),
    "figure_sleep": (
        "tests/figureState.test.js",
        "tests/figureVisible.test.js",
        "tests/figurePerches.test.js",
        "tests/figureParcels.test.js",
    ),
    "worker_stopped_card": (
        "tests/workerStoppedCard.test.js",
    ),
    "hidden_tab": (
        "tests/poll.test.js",
        "tests/hiddenTab.test.js",
    ),
    "flowchart": (
        "tests/flowchart.test.js",
    ),
    "organization_counts": ("tests/organizationCounts.test.js",),
    "organization_page": ("tests/organizationPage.test.js", "tests/organizationSidebar.test.js"),
    "organization_communication": ("tests/planCommunicationTimeline.test.js", "tests/organizationPage.test.js"),
    "organization_home": ("tests/homePlanBoard.test.js", "tests/organizationBoard.test.js", "tests/homeBoard.test.js"),
    "board_page": ("tests/boardPage.test.js", "tests/organizationSidebar.test.js", "tests/organizationBoard.test.js"),
    "chat_page": (
        "tests/chatPage.test.js",
        "tests/activeCards.test.js",
        "tests/composeInput.test.js",
        "tests/docks.test.js",
        "tests/homePlanBoard.test.js",
        "tests/organizationSidebar.test.js",
        "tests/planAgentChats.test.js",
        "tests/planAgentSection.test.js",
        "tests/phoneHomeBoard.test.js",
        "tests/thread.test.js",
        "tests/teamPages.test.js",
    ),
    "organization_sidebar": ("tests/organizationSidebar.test.js",),
    "organization_role_sidebar": (
        "tests/organizationRoutes.test.js",
        "tests/organizationSidebar.test.js",
        "tests/rolePage.test.js",
    ),
    "organization_board": ("tests/organizationBoard.test.js",),
    "plan_agent_chat": ("tests/planAgents.test.js", "tests/planAgentChats.test.js", "tests/planAgentSection.test.js"),
    "plan_role_history": ("tests/planRoleHistory.test.js",),
    "plan_team": ("tests/planTeam.test.js",),
    "organization_scale": (
        "tests/organizationBoard.test.js",
        "tests/organizationSidebar.test.js",
        "tests/homeBoard.test.js",
        "tests/taskGraphAccess.test.js",
    ),
    "worker_cell": (
        "tests/agentCell.test.js",
    ),
    "approvals": (
        "tests/approvals.test.js",
        "tests/approvalPhone.test.js",
    ),
    "role_page": (
        "tests/rolePage.test.js",
        "tests/organizationRoutes.test.js",
        "tests/organizationSidebar.test.js",
        "tests/agentTalk.test.js",
        "tests/thread.test.js",
        "tests/workerHome.test.js",
        "tests/workerInspector.test.js",
        "tests/transcript.test.js",
    ),
    "phone_navigation": (
        "tests/phone.test.js",
        "tests/phoneHomeBoard.test.js",
    ),
    "figure_home_return": (
        "tests/figureHomeReturn.test.js",
    ),
    "update_path": (
        "tests/updatePath.test.js",
        "tests/updating.test.js",
        "tests/otherServer.test.js",
        "tests/forceUpdate.test.js",
    ),
}


@pytest.mark.parametrize("name", SETS)
def test_the_viewer_tests_pass(name: str):
    run = subprocess.run([str(WEB / "node_modules" / ".bin" / "vitest"), "run", *SETS[name]], cwd=WEB, capture_output=True, text=True, timeout=VITEST_SECONDS)
    assert run.returncode == 0, "\n".join((run.stdout + run.stderr).splitlines()[-80:])
