from pathlib import Path

from journal.config import Config
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.pool_jobs import PoolJobs
from journal.supervisor_link import SupervisorLink

WAITING_FOLDER = "restart-waiting"
POOL_ENTRY = "pool"


class RestartQueue:
    """A restart of an environment's journal, done at once while none of its commands runs, else marked as waiting on the commands running then and done by RestartWait once the last of those ends, so a restart never cuts a running command off and never waits on one started after it was asked; the command asking for the restart is not counted. An update's restart also waits until no pool worker taken up here is running, so a raised pin never cuts one off."""

    def __init__(self, outputs: CommandOutputs, supervisor: SupervisorLink, config: Config, jobs: PoolJobs) -> None:
        self.outputs, self.supervisor, self.config, self.jobs = outputs, supervisor, config, jobs

    def restart(self, environment_id: int, asking_folder: str) -> list[CommandOutput]:
        outputs = self.outputs.active_outputs(environment_id, asking_folder)
        if outputs:
            self.record_wait(environment_id, [str(output.id) for output in outputs])
            return outputs
        self.restarted(environment_id)
        return []

    def update_restart(self, environment_id: int) -> list[CommandOutput]:
        if not self.jobs.started_count():
            return self.restart(environment_id, "")
        outputs = self.outputs.active_outputs(environment_id, "")
        self.record_wait(environment_id, [*(str(output.id) for output in outputs), POOL_ENTRY])
        return outputs

    def record_wait(self, environment_id: int, entries: list[str]) -> None:
        self.waiting_folder().mkdir(parents=True, exist_ok=True)
        (self.waiting_folder() / str(environment_id)).write_text(" ".join(entries))

    def restarted(self, environment_id: int) -> None:
        (self.waiting_folder() / str(environment_id)).unlink(missing_ok=True)
        self.supervisor.restart_journal(environment_id)

    def waiting(self) -> list[int]:
        return sorted(int(waiting_file.name) for waiting_file in self.waiting_folder().glob("*")) if self.waiting_folder().is_dir() else []

    def is_waiting(self, environment_id: int) -> bool:
        return (self.waiting_folder() / str(environment_id)).is_file()

    def release(self, environment_id: int) -> None:
        entries = (self.waiting_folder() / str(environment_id)).read_text().split()
        numbers = [int(entry) for entry in entries if entry.isdigit()]
        if self.outputs.running_among(numbers) or (POOL_ENTRY in entries and self.jobs.started_count()):
            return
        self.restarted(environment_id)

    def waiting_folder(self) -> Path:
        return self.config.home / "runtime" / WAITING_FOLDER
