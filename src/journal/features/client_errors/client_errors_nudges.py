from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class ClientErrorsNudges:
    LOGGED = Nudge("client_errors", "logged", "the viewer logged {{errors}}", "read them with `journal developer client-errors`", repeat=Timeout.seconds(0))
    UNHANDLED = Nudge("client_errors", "unhandled", "{{errors}} in the viewer: `journal developer client-errors`, fix, then add `--clear`", "", repeat=Timeout.seconds(0))


    @staticmethod
    def errors(count: int) -> str:
        return "a console error" if count == 1 else f"{count} console errors"
