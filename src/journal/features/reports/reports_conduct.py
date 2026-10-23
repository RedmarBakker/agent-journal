from journal.engine.conduct import Conduct
from journal.support.timeout import Timeout
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.commit_detected import CommitDetected



class ReportsConduct(Conduct):
    """The reports feature's conduct in every state: after a commit the agent is offered to write an update, at most once in the set minutes, counted from the first commit after the last offer or update, and never while an update the user has not read waits."""

    def on_commit_detected(self, event: CommitDetected, settings: Settings) -> Transition:
        from journal.features.reports.feature import ReportsFeature
        data = event.data.part(ReportsFeature)
        minutes = settings.integer(ReportsFeature.UPDATE_INTERVAL)
        if data.unread_update or minutes <= 0 or not data.clock_start_at or not Timeout.minutes(minutes).started(data.clock_start_at).is_elapsed(event.time):
            return self.none()
        return self.none(ReportsFeature.UPDATE_SUGGESTION.create())
