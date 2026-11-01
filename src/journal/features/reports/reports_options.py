from journal.support.option import Option


class ReportsOptions:
    """The options of the reports feature."""

    UPDATE_INTERVAL = Option("reports.update_every", "Offer to write an update at most every", "Minutes between two offers to the agent, after a commit, to write you an update; the first commit after the last offer or update starts the count, and none is offered while an update you have not read waits; 0 offers none", 60, unit="minutes")
