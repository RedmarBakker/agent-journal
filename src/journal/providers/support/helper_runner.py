import os
from pathlib import Path
import signal
import subprocess
import threading
import time
from typing import ClassVar

from journal.config import Config
from journal.models.helper import Helper
from journal.providers.providers import Providers
from journal.providers.support.helper_setup import HelperSetup
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.actor import Actor
from journal.support.actor_kind import ActorKind
from journal.support.agent_token import AgentToken
from journal.support.process_check import ProcessCheck


class HelperRunner[H: Helper]:
    """Runs an agent the journal sends itself, a verifier or a reviewer: its program headless on its brief in the project, a fresh session or the one it worked in last, its shell marked with its kind, its own number and token and the journal's hooks wired in; a process that ends, or runs past its limit, before its answer ends the agent, unless a newer run of the same agent has taken its row, and its answer stops its process. Its row is read under the write lock, since the sender may still hold the transaction that saved it, as a listener on the event that sent it does."""

    seconds: ClassVar[int]

    def __init__(self, config: Config, providers: Providers, setup: HelperSetup, rows: ScopedRepository[H], environments: Environments, agents: Agents, scope: Scope) -> None:
        self.config, self.providers, self.setup, self.rows = config, providers, setup, rows
        self.environments, self.agents, self.scope = environments, agents, scope

    def start(self, helper: H, resume: str) -> H:
        provider, token = self.providers.lookup(helper.provider), AgentToken.random()
        helper = self.rows.save(helper.with_(session=provider.worker_session(resume), token_hash=token.digest()), Actor.system())
        settings = self.setup.hook_settings(provider, self.config.root, self.output(helper).with_suffix(".settings.json"))
        command = [*provider.worker_command(helper.brief, helper.model, resume, helper.session), *provider.worker_settings_flags(settings)]
        environ = self.setup.variables(self.environments.find(helper.environment_id).name, Actor(ActorKind(helper.kind), str(helper.id)), token)
        threading.Thread(target=self.run, args=(helper, command, environ), name=f"{helper.kind}-{helper.id}", daemon=True).start()
        return helper

    def run(self, helper: H, command: list[str], environ: dict[str, str]) -> None:
        with self.scope.environment(helper.environment_id):
            output = self.output(helper)
            output.parent.mkdir(parents=True, exist_ok=True)
            try:
                with output.open("a") as log_file:
                    process = subprocess.Popen(command, cwd=self.config.root, env=environ, stdin=subprocess.DEVNULL, stdout=log_file, stderr=subprocess.STDOUT, text=True, start_new_session=True)
            except OSError:
                self.ended(helper)
                return
            self.rows.rewritten(helper, Actor.system(), lambda current: current.running_as(process.pid))
            try:
                process.wait(timeout=self.seconds)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            with self.rows.writing():
                current = self.rows.find(helper.row_id)
            if current.pid == process.pid:
                self.ended(current)

    def ended(self, helper: H) -> None:
        for agent in self.agents.active_session_agents(helper.session):
            self.agents.save(agent.retired(time.time()), Actor.system())
        self.rows.rewritten(helper, Actor.system(), lambda current: current.ended())

    def stop(self, helper: H) -> None:
        if helper.pid and ProcessCheck.is_running(helper.pid) and os.getpgid(helper.pid) == helper.pid:
            os.killpg(helper.pid, signal.SIGTERM)

    def output(self, helper: H) -> Path:
        return self.config.home / "runtime" / f"{helper.kind}s" / f"{helper.id}.out"
