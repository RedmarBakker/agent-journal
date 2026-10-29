import json
from dataclasses import dataclass

from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.hub_routes import HubRoutes
from journal.features.organization.support.organization import Organization
from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.support.rejection import Rejection


@dataclass(frozen=True)
class HubTrafficFinding:
    """One OpenRig queue item whose source seat sent outside its hub route, with the transition's actor and identity provenance."""

    item_id: str
    source: str
    destination: str
    actor_session: str
    identity_provenance: object


class HubTrafficAudit:
    """Compares OpenRig's retained queue transitions and queue items with the organization's containment routes."""

    def __init__(self, organization: Organization, routes: HubRoutes, runtime: SeatRuntime) -> None:
        self.organization, self.routes, self.runtime = organization, routes, runtime

    def findings(self) -> tuple[HubTrafficFinding, ...]:
        contracts = self.organization.contracts()
        nodes = {edge.source for edge in contracts.containment()} | {edge.target for edge in contracts.containment()}
        aliases, role_prefixes = self.identities(contracts, nodes)
        transitions = {}
        for transition in self.runtime.queue_transitions():
            item_id = str(transition.get("qitemId", "")).strip()
            if item_id:
                transitions[item_id] = transition
        findings = []
        for item in self.runtime.queue_items():
            item_id = str(item.get("qitemId", item.get("id", ""))).strip()
            transition = transitions.get(item_id, {})
            source_value, destination_value = item.get("source"), item.get("destination")
            if not item_id or not isinstance(source_value, str) or not source_value.strip() or not isinstance(destination_value, str) or not destination_value.strip():
                continue
            source = self.canonical(source_value, aliases, role_prefixes, nodes)
            if source is None:
                continue
            destination = self.canonical(destination_value, aliases, role_prefixes, nodes) or destination_value.strip()
            if self.routes.allowed(source, destination):
                continue
            provenance = transition.get("identityProvenance", "not reported")
            actor = transition.get("actorSession")
            actor_session = str(actor).strip() if actor else "not reported"
            findings.append(HubTrafficFinding(item_id, source, destination, actor_session, provenance))
        return tuple(findings)

    def identities(self, contracts: Contracts, nodes: set[str]) -> tuple[dict[str, str], tuple[tuple[str, str], ...]]:
        names: dict[str, set[str]] = {node: {node} for node in nodes}
        role_prefixes = []
        for role in contracts.roles:
            identity = Contracts.role_id(role)
            if identity in nodes:
                role_prefixes.append((f"{role.domain}-{role.id}-", identity))
        folder = self.runtime.config.home / "runtime" / "rigs"
        for path in sorted(folder.glob("*/rig.yaml")):
            try:
                spec = json.loads(path.read_text())
            except (OSError, ValueError) as failed:
                raise Rejection(f"OpenRig spec {path} cannot be read for the hub traffic audit: {failed}") from failed
            if not isinstance(spec, dict) or not isinstance(spec.get("pods", []), list):
                raise Rejection(f"OpenRig spec {path} has no readable pod list for the hub traffic audit")
            rig = path.parent.name
            for pod in spec.get("pods", []):
                if not isinstance(pod, dict):
                    continue
                pod_id = str(pod.get("id", ""))
                for member in pod.get("members", []):
                    if not isinstance(member, dict):
                        continue
                    member_id = str(member.get("id", ""))
                    identity = self.member_identity(pod_id, member_id, contracts)
                    if not identity or identity not in nodes:
                        continue
                    aliases = (member_id, f"{pod_id}.{member_id}", f"{pod_id}-{member_id}", f"{pod_id}-{member_id}@{rig}", str(member.get("agent_ref", "")))
                    for alias in aliases:
                        if alias:
                            names.setdefault(alias, set()).add(identity)
        return ({name: next(iter(values)) for name, values in names.items() if len(values) == 1}, tuple(sorted(role_prefixes, key=lambda pair: len(pair[0]), reverse=True)))

    @staticmethod
    def member_identity(pod: str, member: str, contracts: Contracts) -> str:
        if pod == "plan" and member == "plan-agent":
            return "plan"
        if member == "domain-agent" and contracts.domain(pod):
            return Contracts.domain_id(pod)
        matches = [role for role in contracts.roles_of(pod) if member == role.id or member.startswith(f"{role.id}-")]
        return Contracts.role_id(max(matches, key=lambda role: len(role.id))) if matches else ""

    @staticmethod
    def canonical(value: str, aliases: dict[str, str], role_prefixes: tuple[tuple[str, str], ...], nodes: set[str]) -> str | None:
        identity = value.strip()
        if identity in nodes:
            return identity
        if identity in aliases:
            return aliases[identity]
        return next((role for prefix, role in role_prefixes if identity.startswith(prefix)), None)
