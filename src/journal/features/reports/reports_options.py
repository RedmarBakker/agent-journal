from journal.support.option import Option


class ReportsOptions:
    """The options of the reports feature."""

    UPDATE_INTERVAL = Option("reports.update_every", "Offer to write an update at most every", "Minutes between two offers to the agent, after a commit, to write you an update; the first commit after the last offer or update starts the count, and none is offered while an update you have not read waits; 0 offers none", 60, unit="minutes")
    UNACTED_MINUTES = Option("reports.unacted_minutes", "Orchestrator: name a report or document never acted on after", "Minutes after a report or document is written, never read, linked, mentioned or changed and not signed off, after which the orchestrator is told of it, and again every 20 to 40 minutes, chosen anew each time, until it is acted on or signed off; 0 never tells", 60, unit="minutes")
