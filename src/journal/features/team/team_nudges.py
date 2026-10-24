from journal.engine.nudge import Nudge


class TeamNudges:
    UPGRADE_NEEDED = Nudge("team", "journal_behind_the_team", "this journal is behind its team: {{line}}", "its changes wait here until it is upgraded; tell your user once and go on", repeat_interval=0)
