import json
import os
from pathlib import Path

from journal.config import Config
from journal.providers.provider import Provider
from journal.providers.providers import Providers
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from journal.support.caller import ACTOR, ACTOR_TOKEN, AGENT_SHELL

JOURNAL_ACTIVE = "AGENT_JOURNAL_ACTIVE"
EXCLUDED_VARIABLES = ("JOURNAL_SESSION", "JOURNAL_LAUNCH")


class HelperSetup:
    """What a sent agent's program runs with, a worker's and a verifier's alike: the variables of its shell, its actor and the token that proves it, and the settings file that wires the journal's hooks into its run."""

    def __init__(self, config: Config, providers: Providers) -> None:
        self.config, self.providers = config, providers

    def variables(self, environment: str, actor: Actor, token: AgentToken) -> dict[str, str]:
        excluded = (*EXCLUDED_VARIABLES, *self.providers.inherited_markers(), *self.providers.session_variables())
        return {**{k: v for k, v in os.environ.items() if k not in excluded}, AGENT_SHELL: "1", JOURNAL_ACTIVE: "1", ACTOR: actor.stamp, ACTOR_TOKEN: token.text, "JOURNAL_ENV": environment, "JOURNAL_ROOT": str(self.config.root)}

    def hook_settings(self, provider: Provider, folder: Path, runtime: Path) -> Path:
        path = provider.worker_hook_file(folder, runtime)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"hooks": provider.hook_block(provider.hook_command(self.config.root))}, indent=2) + "\n")
        return path
