from journal.engine.conduct import Conduct


class PlanLinesConduct(Conduct):
    def on_stop(self, event, settings):
        # @sin WorkModeAskedDetector
        if self.mode.delegates_work():
            return self.none()
        return self.none()


class PlanFocus:
    def focused(self, plans: list) -> list:
        # @righteous WorkModeAskedDetector
        return plans if self.mode.delegates_work() else plans[:1]
