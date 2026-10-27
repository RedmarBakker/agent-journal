import json

from journal.config import Config
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.support.process_check import ProcessCheck


class LaunchFiles:
    """What the launch of each environment's agent was: the file the launcher writes under runtime/launches, read for the flags the agent runs with, the id the launch is named by, and whether the launcher that wrote it still runs."""

    def __init__(self, config: Config, environments: Environments, providers: Providers) -> None:
        self.config, self.environments, self.providers = config, environments, providers

    def skips_prompts(self, environment_id: int) -> bool:
        command = self.launch(self.environments.find(environment_id).name).get("front", {}).get("command", [])
        return any(flag in command for provider in self.providers.all() for flag in provider.prompt_flags)

    def is_launch(self, environment: str, launch_id: str | None) -> bool:
        current = self.launch(environment).get("launch", "")
        return not current or launch_id == current

    def is_abandoned(self, environment: str) -> bool:
        owner = int(self.launch(environment).get("owner", 0))
        return owner > 0 and not ProcessCheck.is_running(owner)

    def folder(self, environment: str) -> str:
        return self.launch(environment).get("front", {}).get("folder", "")

    def launch(self, environment: str) -> dict:
        path = self.config.home / "runtime" / "launches" / f"{environment}.json"
        return json.loads(path.read_text()) if path.is_file() else {}
