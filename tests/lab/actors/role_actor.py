import random
from collections.abc import Mapping

from journal.features.organization.support.role import Role
from journal.support.caller import Caller
from tests.lab.behaviour_profile import BehaviourProfile
from tests.observation import Observation
from tests.simulation.agent_session import AgentSession
from tests.simulation.simulator import Simulator


class RoleActor:
    """A simulated writing Role edits, commits and proves its work while a non-writing Role sends a report."""

    def __init__(self, simulator: Simulator, role: Role, caller: Caller, profile: BehaviourProfile, seed: int) -> None:
        if profile.agent_kind != "role":
            raise ValueError("a Role needs a role behaviour profile")
        self.simulator, self.role, self.profile, self.chance = simulator, role, profile, random.Random(seed)
        self.session = AgentSession(simulator, caller)
        self.missed_inputs: tuple[str, ...] = ()

    @property
    def session_id(self) -> str:
        return self.session.caller.agent_session

    def session_start(self) -> Observation:
        return self.session.session_start()

    def clock_in(self) -> Observation:
        return self.session.command(["clock-in"])

    def receive_handoff(self, inputs: Mapping[str, str]) -> dict[str, str]:
        received = dict(inputs)
        self.missed_inputs = ()
        if received and self.profile.misses_handoff(self.chance):
            missed = self.chance.choice(tuple(received))
            self.missed_inputs = (missed,)
            del received[missed]
        return received

    def write_path(self, path: str) -> str:
        if self.profile.writes_outside_worktree(self.chance):
            return f"../{path.lstrip('/')}"
        return path

    def write(self, path: str, content: str) -> Observation:
        if not self.role.writes or not self.role.allows_call("Write"):
            raise RuntimeError(f"Role {self.role.id} does not write with the editor")
        path = self.write_path(path)
        result = self.session.tool("Write", {"file_path": path, "content": content}, {"type": "create"})
        if not result.is_refused():
            self.simulator.ledger.wrote(path, len(content.splitlines()))
        return result

    def commit(self, subject: str) -> Observation:
        if not self.role.writes:
            raise RuntimeError(f"Role {self.role.id} does not commit writing work")
        self.simulator.ledger.committed(subject, int(self.simulator.source.seconds()))
        return self.simulator.observe()

    def prove(self, point: int, proof: str) -> Observation:
        if not self.role.writes:
            raise RuntimeError(f"Role {self.role.id} does not prove writing work")
        return self.session.command(["proof", str(point), proof])

    def report(self, text: str) -> Observation:
        if self.role.writes:
            raise RuntimeError(f"Role {self.role.id} returns its work with proofs")
        return self.session.command(["message", "send", text])

