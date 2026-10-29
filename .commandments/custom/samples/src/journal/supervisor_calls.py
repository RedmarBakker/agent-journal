# @sin SupervisorImportOutsideLauncherDetector
from supervisor.service import Service


class Restart:
    """A sample for the supervisor rules: the journal starting a service of the supervisor's itself."""

    def __init__(self, supervisor, service: Service) -> None:
        self.supervisor, self.service = supervisor, service

    def restarted(self) -> None:
        # @sin SupervisorServiceVerbDetector
        self.supervisor.start_child(self.service)
