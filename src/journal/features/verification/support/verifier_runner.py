import os
from pathlib import Path
import signal
import subprocess
import threading
import time

from journal.config import Config
from journal.models.verifier import Verifier
from journal.providers.providers import Providers
from journal.providers.support.helper_setup import HelperSetup
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.verifiers import Verifiers
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from journal.support.process_check import ProcessCheck

VERIFIER_SECONDS = 600


class VerifierRunner:
    """Runs a verifier the journal sent: its program headless on its brief in the project, its shell marked a verifier's with its own number and token and the journal's hooks wired in; a process that ends, or runs past its ten minutes, without a verdict ends the verifier, and a verdict stops its process."""

    def __init__(self, config: Config, providers: Providers, setup: HelperSetup, verifiers: Verifiers, environments: Environments, agents: Agents, scope: Scope) -> None:
        self.config, self.providers, self.setup, self.verifiers = config, providers, setup, verifiers
        self.environments, self.agents, self.scope = environments, agents, scope

    def start(self, verifier: Verifier) -> Verifier:
        provider, token = self.providers.lookup(verifier.provider), AgentToken.random()
        verifier = self.verifiers.save(verifier.with_(session=provider.worker_session(""), token_hash=token.digest()), Actor.system())
        settings = self.setup.hook_settings(provider, self.config.root, self.output(verifier).with_suffix(".settings.json"))
        command = [*provider.worker_command(verifier.brief, verifier.model, "", verifier.session), *provider.worker_settings_flags(settings)]
        environ = self.setup.variables(self.environments.find(verifier.environment_id).name, Actor.verifier(verifier.id), token)
        threading.Thread(target=self.run, args=(verifier, command, environ), name=f"verifier-{verifier.id}", daemon=True).start()
        return verifier

    def run(self, verifier: Verifier, command: list[str], environ: dict[str, str]) -> None:
        with self.scope.environment(verifier.environment_id):
            output = self.output(verifier)
            output.parent.mkdir(parents=True, exist_ok=True)
            try:
                with output.open("w") as log_file:
                    process = subprocess.Popen(command, cwd=self.config.root, env=environ, stdin=subprocess.DEVNULL, stdout=log_file, stderr=subprocess.STDOUT, text=True, start_new_session=True)
            except OSError:
                self.ended(verifier)
                return
            self.verifiers.save(self.verifiers.find(verifier.row_id).running_as(process.pid), Actor.system())
            try:
                process.wait(timeout=VERIFIER_SECONDS)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            self.ended(self.verifiers.find(verifier.row_id))

    def ended(self, verifier: Verifier) -> None:
        for agent in self.agents.active_session_agents(verifier.session):
            self.agents.save(agent.retired(time.time()), Actor.system())
        self.verifiers.save(self.verifiers.find(verifier.row_id).ended(), Actor.system())

    def stop(self, verifier: Verifier) -> None:
        if verifier.pid and ProcessCheck.is_running(verifier.pid) and os.getpgid(verifier.pid) == verifier.pid:
            os.killpg(verifier.pid, signal.SIGTERM)

    def output(self, verifier: Verifier) -> Path:
        return self.config.home / "runtime" / "verifiers" / f"{verifier.id}.out"
