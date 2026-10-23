from pathlib import Path

from journal.config import Config
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.supervisor_link import SupervisorLink

WAITING_FOLDER = "restart-waiting"


class RestartQueue:
    """A restart of an environment's journal, done at once while none of its commands runs, else marked as waiting on the commands running then and done by RestartWait once the last of those ends, so a restart never cuts a running command off and never waits on one started after it was asked; the command asking for the restart is not counted."""

    def __init__(self, outputs: CommandOutputs, supervisor: SupervisorLink, config: Config) -> None:
        self.outputs, self.supervisor, self.config = outputs, supervisor, config

    def restart(self, environment_id: int, asking_folder: str) -> list[CommandOutput]:
        outputs = self.outputs.active_outputs(environment_id, asking_folder)
        if outputs:
            self.waiting_folder().mkdir(parents=True, exist_ok=True)
            (self.waiting_folder() / str(environment_id)).write_text(" ".join(str(output.id) for output in outputs))
            return outputs
        self.restarted(environment_id)
        return []

    def restarted(self, environment_id: int) -> None:
        (self.waiting_folder() / str(environment_id)).unlink(missing_ok=True)
        self.supervisor.restart_journal(environment_id)

    def waiting(self) -> list[int]:
        return sorted(int(waiting_file.name) for waiting_file in self.waiting_folder().glob("*")) if self.waiting_folder().is_dir() else []

    def release(self, environment_id: int) -> None:
        waited = [int(number) for number in (self.waiting_folder() / str(environment_id)).read_text().split() if number.isdigit()]
        if not self.outputs.running_among(waited):
            self.restarted(environment_id)

    def waiting_folder(self) -> Path:
        return self.config.home / "runtime" / WAITING_FOLDER
