from dataclasses import replace
import json
import shutil
from pathlib import Path

from journal.config import Config
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.domain import Domain
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.rig_seats import DOMAIN_AGENT, PLAN_AGENT, PLAN_POD, RigSeats
from journal.features.organization.support.rig_specs import OWNER_ONLY, RigSpecs
from journal.features.organization.support.role import Role
from journal.features.organization.support.seat import Seat
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.organization.support.seat_worker import SeatWorker
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.models.plan import Plan
from journal.models.rig import Rig
from journal.providers.provider import Provider
from journal.providers.providers import Providers
from journal.repositories.plans import Plans
from journal.repositories.rigs import Rigs
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from journal.support.process_check import ProcessCheck
from journal.support.rejection import Rejection


class RigStaffing:
    """Start an organization plan with its Plan seat, then grow only the domain pod and Role seat that gets a job."""

    def __init__(self, config: Config, organization: Organization, plans: Plans, rigs: Rigs, seats: RigSeats, specs: RigSpecs, runtime: SeatRuntime, providers: Providers) -> None:
        self.organization = organization
        self.config, self.plans, self.rigs = config, plans, rigs
        self.seats, self.specs, self.runtime, self.providers = seats, specs, runtime, providers

    def start_plan(self, plan: Plan, environment: Environment, agent: Agent, actor: Actor) -> None:
        self.runtime.check_version()
        rig_id = self.plans.rig_id(plan)
        if rig_id:
            rig = self.find_rig(rig_id)
            if self.is_running(plan, agent.provider):
                return
            if not self.runtime.rig_exists(rig.name):
                raise Rejection(f"OpenRig rig {rig.name} for plan {plan.id} is not running")
            self.runtime.launch_node(rig.name, f"{PLAN_POD}.{PLAN_AGENT}")
            return

        rig_name = f"plan-{plan.id}"
        provider = self.providers.lookup(agent.provider)
        path = self.specs.write(rig_name, self.organization.contracts(), (), self.config.root,
                                lambda _seat: SeatWorker(Actor.agent(""), AgentToken.random(), environment.name), provider)
        self.runtime.start_rig(path)
        rig = self.rigs.save(Rig(environment_id=plan.environment_id, name=rig_name), actor)
        self.plans.rig_linked(plan, rig, actor)

    def is_running(self, plan: Plan, provider: str) -> bool:
        rig_id = self.plans.rig_id(plan)
        if not rig_id:
            return False
        rig = self.find_rig(rig_id)
        try:
            seat = self.runtime.member(rig.name, PLAN_POD, PLAN_AGENT, provider)
            session = self.runtime.session(seat)
        except Rejection:
            return False
        return session is not None and ProcessCheck.is_running(session.pid)

    def stop_plan(self, plan: Plan, provider: str) -> None:
        rig_id = self.plans.rig_id(plan)
        if not rig_id:
            return
        rig = self.find_rig(rig_id)
        if self.is_running(plan, provider):
            self.runtime.stop(f"{PLAN_POD}-{PLAN_AGENT}@{rig.name}", f"plan {plan.id} stopped")

    def role(self, plan: Plan, contracts: Contracts, role: Role, worker: int, provider_name: str, environment: str, cwd: Path) -> Seat:
        rig_id = self.plans.rig_id(plan)
        if not rig_id:
            raise Rejection(f"plan {plan.id} has no OpenRig linked for Role {role.id}")
        rig = self.find_rig(rig_id)
        domain = contracts.domain(role.domain)
        if domain is None:
            raise Rejection(f"Role {role.id} has no Domain {role.domain} in its contract")
        path = self.specs.spec_folder(rig.name) / "rig.yaml"
        try:
            spec = json.loads(path.read_text())
        except (OSError, ValueError) as failed:
            raise Rejection(f"OpenRig spec for plan {plan.id} cannot be read at {path}: {failed}") from failed

        provider = self.providers.lookup(provider_name)
        plan_seat = self.seats.plan_agent(rig.name, provider)
        domain_seat = self.seats.domain_agent(domain, provider)
        role_seat = self.worker_seat(role, domain, worker, provider)
        links = self.seats.links(contracts, (plan_seat, domain_seat, role_seat))
        pods = spec.setdefault("pods", [])
        pod = next((value for value in pods if value.get("id") == domain.id), None)
        if pod is None:
            fragment, pod = self.specs.pod_fragment(
                rig.name, domain.id, (domain_seat, role_seat), links,
                lambda seat: cwd if seat.qualified == role_seat.qualified else self.config.root,
                lambda seat: self.seat_worker(seat, role_seat, worker, environment),
            )
            self.runtime.expand(rig.name, fragment, self.specs.spec_folder(rig.name))
            pods.append(pod)
        elif not any(member.get("id") == role_seat.member for member in pod.get("members", [])):
            fragment, member = self.specs.member_fragment(
                rig.name, role_seat, cwd,
                self.seat_worker(role_seat, role_seat, worker, environment),
            )
            self.runtime.add(rig.name, domain.id, fragment, self.specs.spec_folder(rig.name))
            pod.setdefault("members", []).append(member)

        edges = spec.setdefault("edges", [])
        for source, target in links:
            if source.pod == target.pod:
                edge = self.specs.edge(source.member, target.member)
                if edge not in pod.setdefault("edges", []):
                    pod["edges"].append(edge)
            else:
                edge = self.specs.edge(source.logical_id(), target.logical_id())
                if edge not in edges:
                    edges.append(edge)
        self.specs.written(path, spec).chmod(OWNER_ONLY)
        for source, target in links:
            self.runtime.edge(rig.name, source.logical_id(), target.logical_id())
        return role_seat

    def remove_role(self, plan: Plan, contracts: Contracts, role: Role, worker: int, provider_name: str) -> None:
        if role.cardinality is not Cardinality.MANY:
            return
        rig_id = self.plans.rig_id(plan)
        if not rig_id:
            return
        rig = self.find_rig(rig_id)
        domain = contracts.domain(role.domain)
        if domain is None:
            raise Rejection(f"Role {role.id} has no Domain {role.domain} in its contract")
        provider = self.providers.lookup(provider_name)
        seat = self.worker_seat(role, domain, worker, provider)
        path = self.specs.spec_folder(rig.name) / "rig.yaml"
        try:
            spec = json.loads(path.read_text())
        except (OSError, ValueError) as failed:
            raise Rejection(f"OpenRig spec for plan {plan.id} cannot be read at {path}: {failed}") from failed
        pod = next((value for value in spec.get("pods", []) if value.get("id") == seat.pod), None)
        if pod is None or not any(member.get("id") == seat.member for member in pod.get("members", [])):
            return
        if self.runtime.rig_exists(rig.name):
            self.runtime.remove_node(rig.name, seat.logical_id())
        pod["members"] = [member for member in pod["members"] if member.get("id") != seat.member]
        pod["edges"] = [edge for edge in pod.get("edges", []) if seat.member not in (edge.get("from"), edge.get("to"))]
        logical_id = seat.logical_id()
        spec["edges"] = [edge for edge in spec.get("edges", []) if logical_id not in (edge.get("from"), edge.get("to"))]
        self.specs.written(path, spec).chmod(OWNER_ONLY)
        shutil.rmtree(self.specs.spec_folder(rig.name) / "agents" / seat.agent())
        fragment = self.specs.spec_folder(rig.name) / "members" / f"{seat.pod}-{seat.member}.json"
        fragment.unlink(missing_ok=True)

    @staticmethod
    def seat_worker(seat: Seat, role: Seat, worker: int, environment: str) -> SeatWorker:
        actor = Actor.worker(worker) if seat.qualified == role.qualified else Actor.agent("")
        return SeatWorker(actor, AgentToken.random(), environment)

    def worker_seat(self, role: Role, domain: Domain, worker: int, provider: Provider) -> Seat:
        seat = self.seats.role_seat(role, domain, provider)
        return replace(seat, member=f"{role.id}-{worker}") if role.cardinality is Cardinality.MANY else seat

    def find_rig(self, rig_id: int) -> Rig:
        matches = self.rigs.global_matching(id=rig_id)
        if matches:
            return matches[0]
        return self.rigs.find(rig_id)
