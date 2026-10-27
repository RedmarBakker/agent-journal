from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class TeamNudges:
    UPGRADE_NEEDED = Nudge("team", "journal_behind_the_team", "this journal is behind its team: {{line|cap=200}}", "its changes wait for an upgrade. tell your user once", repeat=Timeout.seconds(0), longest_characters=297, longest_reason="it contains the upgrade instructions")
