from journal.engine.nudge import Nudge
from journal.engine.nudge_kind import NudgeKind
from journal.support.timeout import Timeout


class ClientErrorsNudges:
    LOGGED = Nudge("client_errors", "logged", "the viewer logged {{errors|cap=51}}", "read them with `journal developer client-errors`", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    UNHANDLED = Nudge("client_errors", "unhandled", "{{errors|cap=30}} in the viewer: read `journal developer client-errors`, fix, then run it with `--clear`", "", repeat=Timeout.seconds(0))


    @staticmethod
    def errors(count: int) -> str:
        return "a console error" if count == 1 else f"{count} console errors"
