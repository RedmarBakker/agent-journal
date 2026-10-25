from journal.config import Config
from journal.features.health.support.bypass import Bypass

LOG = "bypass.log"
TAKEN = "bypass.log.taken"


class BypassLog:
    """The hooks and shell lines the hook script and the shell runner sent around a journal that did not answer, as they wrote them to runtime/bypass.log; taking them moves the file aside first, so a line written meanwhile waits in a new log for the next take."""

    def __init__(self, config: Config) -> None:
        self.runtime = config.home / "runtime"

    def taken(self) -> list[Bypass]:
        log, taken = self.runtime / LOG, self.runtime / TAKEN
        if not log.is_file():
            return []
        log.replace(taken)
        lines = taken.read_text(errors="replace").splitlines()
        taken.unlink()
        return [Bypass.parse(line) for line in lines if line.strip()]
