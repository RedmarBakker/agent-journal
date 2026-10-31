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
from journal.features.organization.support.rig_specs import MINIMUM_OPENRIG_VERSION, OWNER_ONLY, RigSpecs
from journal.features.organization.support.role import Role
from journal.features.organization.support.seat import Seat
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.organization.support.role_work_checks import RoleWorkChecks
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.models.plan import Plan
from journal.models.rig import Rig
from journal.providers.provider import Provider
from journal.providers.providers import Providers
from journal.repositories.organization_handoffs import OrganizationHandoffs
from journal.repositories.plans import Plans
from journal.repositories.rigs import Rigs
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from journal.support.caller import ACTOR
from journal.support.process_check import ProcessCheck
from journal.support.rejection import Rejection


class RigStaffing:
    """Start each plan's rig, keep shared journal Roles in one organization rig, and add only the seats each job needs."""

    def __init__(self, config: Config, organization: Organization, plans: Plans, rigs: Rigs, seats: RigSeats, specs: RigSpecs, runtime: SeatRuntime, providers: Providers, handoffs: OrganizationHandoffs, role_work_checks: RoleWorkChecks) -> None:
        self.organization = organization
        self.config, self.plans, self.rigs = config, plans, rigs
        self.seats, self.specs, self.runtime, self.providers = seats, specs, runtime, providers
        self.handoffs = handoffs
        self.role_work_checks = role_work_checks

    def start_plan(self, plan: Plan, environment: Environment, agent: Agent, actor: Actor) -> None:
        self.runtime.check_version()
        rig_id = self.plans.rig_id(plan)
        if rig_id:
            rig = self.find_rig(rig_id)
            if self.is_running(plan, agent.provider):
                return
            if not self.runtime.rig_exists(rig.name):
                raise Rejection(f"OpenRig rig {rig.name} for plan {plan.id} is not running")
            spec = self.specs.refresh_plan(rig.name, self.config.root, self.providers.lookup(agent.provider), self.organization.contracts())
            self.handoffs.reopen_domain_inboxes(plan, actor, self.role_work_checks.tasks_waiting_for_check(plan))
            self.runtime.replace_rig(rig.name, spec)
            return

        rig_name = f"plan-{plan.id}"
        provider = self.providers.lookup(agent.provider)
        path = self.specs.write(rig_name, self.organization.contracts(), (), self.config.root,
                                lambda seat: SeatWorker(Actor.agent(""), AgentToken.random(), environment.name, seat.qualified, rig_name), provider)
        self.runtime.start_rig(path)
        rig = self.rigs.save(Rig(environment_id=plan.environment_id, name=rig_name), actor)
        self.plans.rig_linked(plan, rig, actor)

    def place_domain(self, plan: Plan, domain_id: str, provider_name: str, environment: str) -> None:
        contracts = self.organization.contracts()
        domain = contracts.domain(domain_id)
        if domain is None:
            raise Rejection(f"OpenRig plan {plan.id} cannot place unknown Domain {domain_id}")
        rig_id = self.plans.rig_id(plan)
        if not rig_id:
            raise Rejection(f"plan {plan.id} has no OpenRig rig for Domain {domain_id}")
        rig = self.find_rig(rig_id)
        provider = self.providers.lookup(provider_name)
        plan_seat = self.seats.plan_agent(rig.name, provider)
        domain_seat = self.seats.domain_agent(domain, provider)
        links = self.seats.links(contracts, (plan_seat, domain_seat))
        self.add_domain_seat(rig, domain_seat, links, environment)

    def add_domain_seat(self, rig: Rig, seat: Seat, links: tuple[tuple[Seat, Seat], ...], environment: str) -> None:
        path, spec = self.specs.read_rig_spec(rig.name)
        pods = spec.setdefault("pods", [])
        pod = next((value for value in pods if value.get("id") == seat.pod), None)
        edges = spec.setdefault("edges", [])
        missing_links = tuple(
            (source, target)
            for source, target in links
            if source.pod != target.pod and self.specs.edge(source.logical_id(), target.logical_id()) not in edges
        )
        member_exists = pod is not None and any(member.get("id") == seat.member for member in pod.get("members", []))
        if member_exists and not missing_links:
            return
        running = self.runtime.rig_exists(rig.name)
        worker = lambda placed: SeatWorker(Actor.agent(""), AgentToken.random(), environment, placed.qualified, rig.name)
        expansion = None
        if pod is None:
            if running:
                self.runtime.check_expand_version(MINIMUM_OPENRIG_VERSION)
            fragment, pod = self.specs.pod_fragment(rig.name, seat.pod, (seat,), links, self.config.root, worker)
            pods.append(pod)
            expansion = fragment
        elif not any(member.get("id") == seat.member for member in pod.get("members", [])):
            fragment, member = self.specs.member_fragment(rig.name, seat, self.config.root, worker(seat))
            pod.setdefault("members", []).append(member)
            self.specs.write_pod_fragment(rig.name, pod)
            if running:
                self.runtime.add(rig.name, seat.pod, fragment, self.specs.spec_folder(rig.name))
        for source, target in missing_links:
            edges.append(self.specs.edge(source.logical_id(), target.logical_id()))
        self.specs.written(path, spec).chmod(OWNER_ONLY)
        if running and expansion:
            self.runtime.expand(rig.name, expansion, self.specs.spec_folder(rig.name))
        if running:
            for source, target in missing_links:
                self.runtime.edge(rig.name, source.logical_id(), target.logical_id())
        if running and expansion:
            self.launch_expanded_seats(rig, (seat,))

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

    def role_placement(self, plan: Plan, contracts: Contracts, role: Role, worker: int, provider_name: str, environment: str, cwd: Path) -> tuple[Rig, Seat]:
        domain = contracts.domain(role.domain)
        if domain is None:
            raise Rejection(f"Role {role.id} has no Domain {role.domain} in its contract")
        provider = self.providers.lookup(provider_name)
        domain_seat = self.seats.domain_agent(domain, provider)
        role_seat = self.worker_seat(role, domain, worker, provider)
        if role.cardinality is Cardinality.JOURNAL:
            rig = self.shared_rig(plan, contracts, domain_seat, role_seat, worker, environment, cwd)
            return rig, role_seat

        rig_id = self.plans.rig_id(plan)
        if not rig_id:
            raise Rejection(f"plan {plan.id} has no OpenRig linked for Role {role.id}")
        rig = self.find_rig(rig_id)
        plan_seat = self.seats.plan_agent(rig.name, provider)
        self.place_role(rig, plan, contracts, plan_seat, domain_seat, role_seat, worker, environment, cwd, True)
        return rig, role_seat

    def shared_rig(self, plan: Plan, contracts: Contracts, domain_seat: Seat, role_seat: Seat, worker: int, environment: str, cwd: Path) -> Rig:
        name = self.shared_rig_name(plan.environment_id)
        matches = self.rigs.global_matching(name=name, environment_id=plan.environment_id)
        if not matches:
            seats = (domain_seat, role_seat)
            links = self.seats.links(contracts, seats)
            path = self.specs.write_shared(name, seats, links, cwd,
                                           lambda seat: self.seat_worker(seat, role_seat, worker, environment, name))
            self.runtime.start_rig(path)
            return self.rigs.save(Rig(environment_id=plan.environment_id, name=name), Actor.system())

        rig = matches[0]
        path = self.specs.spec_folder(rig.name) / "rig.yaml"
        if not path.exists():
            seats = (domain_seat, role_seat)
            links = self.seats.links(contracts, seats)
            path = self.specs.write_shared(rig.name, seats, links, cwd,
                                           lambda seat: self.seat_worker(seat, role_seat, worker, environment, rig.name))
            self.runtime.start_rig(path)
            return rig

        running = self.runtime.rig_exists(rig.name)
        self.place_role(rig, plan, contracts, None, domain_seat, role_seat, worker, environment, cwd, running)
        if not running:
            self.runtime.start_rig(path)
        return rig

    @staticmethod
    def shared_rig_name(environment_id: int) -> str:
        return f"organization-{environment_id}"

    @staticmethod
    def rigs_for_plan(plan: Plan) -> tuple[str, str]:
        return f"plan-{plan.id}", RigStaffing.shared_rig_name(plan.environment_id)

    def place_role(self, rig: Rig, plan: Plan, contracts: Contracts, plan_seat: Seat | None, domain_seat: Seat, role_seat: Seat,
                   worker: int, environment: str, cwd: Path, running: bool) -> None:
        path = self.specs.spec_folder(rig.name) / "rig.yaml"
        try:
            spec = json.loads(path.read_text())
        except (OSError, ValueError) as failed:
            raise Rejection(f"OpenRig spec for plan {plan.id} cannot be read at {path}: {failed}") from failed

        seats = tuple(seat for seat in (plan_seat, domain_seat, role_seat) if seat is not None)
        links = self.seats.links(contracts, seats)
        pods = spec.setdefault("pods", [])
        pod = next((value for value in pods if value.get("id") == domain_seat.pod), None)
        role_fragment = None
        replace_role = False
        expansion = None
        if pod is None:
            if running:
                self.runtime.check_expand_version(MINIMUM_OPENRIG_VERSION)
            fragment, pod = self.specs.pod_fragment(
                rig.name, domain_seat.pod, (domain_seat, role_seat), links,
                lambda seat: cwd if seat.qualified == role_seat.qualified else self.config.root,
                lambda seat: self.seat_worker(seat, role_seat, worker, environment, rig.name),
            )
            expansion = fragment
            pods.append(pod)
        elif not any(member.get("id") == role_seat.member for member in pod.get("members", [])):
            fragment, member = self.specs.member_fragment(
                rig.name, role_seat, cwd,
                self.seat_worker(role_seat, role_seat, worker, environment, rig.name),
            )
            pod.setdefault("members", []).append(member)
            role_fragment = fragment
        else:
            index = next(index for index, member in enumerate(pod["members"]) if member.get("id") == role_seat.member)
            previous = pod["members"][index]
            assigned = self.seat_worker(role_seat, role_seat, worker, environment, rig.name)
            if previous.get("env", {}).get(ACTOR) != assigned.actor.stamp:
                fragment, member = self.specs.member_fragment(rig.name, role_seat, cwd, assigned)
                pod["members"][index] = member
                role_fragment = fragment
                replace_role = True

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
        if role_fragment:
            self.specs.write_pod_fragment(rig.name, pod)
        self.specs.written(path, spec).chmod(OWNER_ONLY)
        if running:
            if expansion:
                self.runtime.expand(rig.name, expansion, self.specs.spec_folder(rig.name))
            elif replace_role:
                self.runtime.remove_node(rig.name, role_seat.logical_id())
            if role_fragment and not expansion:
                self.runtime.add(rig.name, domain_seat.pod, role_fragment, self.specs.spec_folder(rig.name))
            for source, target in links:
                self.runtime.edge(rig.name, source.logical_id(), target.logical_id())
            if expansion:
                self.launch_expanded_seats(rig, (domain_seat, role_seat))

    def launch_expanded_seats(self, rig: Rig, seats: tuple[Seat, ...]) -> None:
        for seat in seats:
            member = self.runtime.member(rig.name, seat.pod, seat.member, seat.provider)
            self.runtime.launch(member, f"journal organization starts {seat.qualified} with its generated environment")

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
    def seat_worker(seat: Seat, role: Seat, worker: int, environment: str, rig: str) -> SeatWorker:
        actor = Actor.worker(worker) if seat.qualified == role.qualified else Actor.agent("")
        return SeatWorker(actor, AgentToken.random(), environment, seat.qualified, rig)

    def worker_seat(self, role: Role, domain: Domain, worker: int, provider: Provider) -> Seat:
        seat = self.seats.role_seat(role, domain, provider)
        return replace(seat, member=f"{role.id}-{worker}") if role.cardinality is Cardinality.MANY else seat

    def find_rig(self, rig_id: int) -> Rig:
        matches = self.rigs.global_matching(id=rig_id)
        if matches:
            return matches[0]
        return self.rigs.find(rig_id)
