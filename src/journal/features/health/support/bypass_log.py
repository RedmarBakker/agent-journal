from journal.config import Config
from journal.features.health.support.bypass import Bypass

LOG = "bypass.log"
SECOND_LOG = "bypass.log.second"


class BypassLog:
    """The hooks and shell lines the hook script and the shell runner sent around a journal that did not answer, as they wrote them to runtime/bypass.log; removing them moves the file aside first, so a line written meanwhile waits in a new log for the next take."""

    def __init__(self, config: Config) -> None:
        self.runtime = config.home / "runtime"

    def waiting(self) -> list[Bypass]:
        current_log = self.runtime / LOG
        return [Bypass.parse(line) for line in current_log.read_text(errors="replace").splitlines() if line.strip()] if current_log.is_file() else []

    def removed(self) -> list[Bypass]:
        current_log, second_log = self.runtime / LOG, self.runtime / SECOND_LOG
        if not current_log.is_file():
            return []
        current_log.replace(second_log)
        lines = second_log.read_text(errors="replace").splitlines()
        second_log.unlink()
        return [Bypass.parse(line) for line in lines if line.strip()]
