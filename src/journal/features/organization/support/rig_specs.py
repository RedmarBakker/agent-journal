import json
import os
import shlex
import shutil
from pathlib import Path
from typing import Callable

from journal.config import Config
from journal.features.organization.support.contract_folder import ContractFolder
from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.edge_kind import EdgeKind
from journal.features.organization.support.rig_seats import RigSeats
from journal.features.organization.support.seat import Seat
from journal.features.organization.support.seat_worker import SeatWorker
from journal.features.organization.support.skill_ids import SKILL_FILE, SkillIds
from journal.features.skills.skills_options import SkillsOptions
from journal.features.skills.support.skill_files import SkillFiles
from journal.providers.provider import Provider
from journal.providers.providers import Providers
from journal.providers.support.helper_setup import JOURNAL_ACTIVE, HelperSetup
from journal.repositories.setting_rows import SettingRows
from journal.support.caller import ACTOR, ACTOR_TOKEN, AGENT_SHELL, ORGANIZATION_RIG, ORGANIZATION_SEAT

OPENRIG_VERSION = "0.7.5"
RIG_SPEC_VERSION = "0.2"
AGENT_SPEC_VERSION = "1.0"
PROFILE = "default"
GUIDANCE = "guidance/role.md"
HOOKS = "journal-hooks"
SEAT_VARIABLES = (AGENT_SHELL, JOURNAL_ACTIVE, ACTOR, ACTOR_TOKEN, "JOURNAL_ENV", "JOURNAL_ROOT")
DENIED = ("Bash(git *)", "Bash(rig send *)", "Bash(rig queue *)")
WORKER_COMMANDS = ("Bash(rig context *)", "Bash(nohup *)")
CODEX_ROUTE_RULES = '''prefix_rule(
    pattern = ["rig", "send"],
    decision = "forbidden",
    justification = "Organization seats route messages through their pod hub.",
    match = [["rig", "send", "role:alpha/builder@plan-1", "message"]],
    not_match = [["rig", "sendx", "role:alpha/builder@plan-1", "message"]],
)

prefix_rule(
    pattern = ["rig", "queue", ["create", "handoff", "inbox-drop"]],
    decision = "forbidden",
    justification = "Organization seats route queue changes through their pod hub.",
    match = [
        ["rig", "queue", "create", "--rig", "plan-1"],
        ["rig", "queue", "handoff", "--rig", "plan-1"],
        ["rig", "queue", "inbox-drop", "--rig", "plan-1"],
    ],
    not_match = [["rig", "queue", "list", "--rig", "plan-1"]],
)
'''
EDIT_TOOLS = ("Edit", "Write")
OWNER_ONLY = 0o600


class RigSpecs:
    """Writes pinned OpenRig specs for organization plan rigs and the shared rig for journal-cardinality Roles, with provider runtimes, hooks, models, permissions, guidance and skills."""

    def __init__(self, config: Config, providers: Providers, setup: HelperSetup, seats: RigSeats, skills: SkillIds, files: SkillFiles, folder: ContractFolder, settings: SettingRows) -> None:
        self.config, self.providers, self.setup, self.seats = config, providers, setup, seats
        self.skills, self.files, self.folder, self.settings = skills, files, folder, settings

    def write(self, rig: str, contracts: Contracts, domains: tuple[str, ...], cwd: Path, workers: Callable[[Seat], SeatWorker], provider: Provider | None = None) -> Path:
        provider = provider or self.providers.shell_provider(os.environ)
        seats = self.seats.seats(rig, contracts, domains, provider)
        links = self.seats.links(contracts, seats)
        return self.write_seats(rig, seats, links, cwd, workers, f"The journal's organization plan {rig}.")

    def write_shared(self, rig: str, seats: tuple[Seat, ...], links: tuple[tuple[Seat, Seat], ...], cwd: Path, workers: Callable[[Seat], SeatWorker]) -> Path:
        return self.write_seats(rig, seats, links, cwd, workers, f"The journal's shared organization Roles in {rig}.")

    def write_seats(self, rig: str, seats: tuple[Seat, ...], links: tuple[tuple[Seat, Seat], ...], cwd: Path, workers: Callable[[Seat], SeatWorker], summary: str) -> Path:
        folder = self.spec_folder(rig)
        if folder.exists():
            shutil.rmtree(folder)
        for seat in seats:
            self.agent(folder / "agents" / seat.agent(), seat)
        path = self.written(folder / "rig.yaml", self.spec(rig, seats, links, cwd, workers, summary))
        path.chmod(OWNER_ONLY)
        return path

    def member_fragment(self, rig: str, seat: Seat, cwd: Path, worker: SeatWorker) -> tuple[Path, dict]:
        folder = self.spec_folder(rig)
        agent = folder / "agents" / seat.agent()
        if not agent.exists():
            self.agent(agent, seat)
        member = self.member(seat, cwd, worker)
        path = folder / "members" / f"{seat.pod}-{seat.member}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.written(path, member).chmod(OWNER_ONLY)
        return path, member

    def pod_fragment(self, rig: str, pod: str, seats: tuple[Seat, ...], links: tuple[tuple[Seat, Seat], ...], cwd: Path | Callable[[Seat], Path], workers: Callable[[Seat], SeatWorker]) -> tuple[Path, dict]:
        folder = self.spec_folder(rig)
        for seat in seats:
            agent = folder / "agents" / seat.agent()
            if not agent.exists():
                self.agent(agent, seat)
        value = self.pod(pod, seats, links, cwd, workers)
        return self.write_pod_fragment(rig, value), value

    def write_pod_fragment(self, rig: str, pod: dict) -> Path:
        path = self.spec_folder(rig) / "pods" / f"{pod['id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.written(path, pod).chmod(OWNER_ONLY)
        return path

    def spec_folder(self, rig: str) -> Path:
        return self.config.home / "runtime" / "rigs" / rig

    def spec(self, rig: str, seats: tuple[Seat, ...], links: tuple[tuple[Seat, Seat], ...], cwd: Path, workers: Callable[[Seat], SeatWorker], summary: str = "") -> dict:
        cwd = cwd.resolve()
        pods = [self.pod(pod, tuple(seat for seat in seats if seat.pod == pod), links, cwd, workers) for pod in dict.fromkeys(seat.pod for seat in seats)]
        return {"version": RIG_SPEC_VERSION, "name": rig, "summary": summary or f"The journal's organization plan {rig}.", "pods": pods,
                "edges": [self.edge(source.logical_id(), target.logical_id()) for source, target in links if source.pod != target.pod]}

    def pod(self, pod: str, seats: tuple[Seat, ...], links: tuple[tuple[Seat, Seat], ...], cwd: Path | Callable[[Seat], Path], workers: Callable[[Seat], SeatWorker]) -> dict:
        folder = lambda seat: cwd(seat) if callable(cwd) else cwd
        return {"id": pod, "label": pod, "members": [self.member(seat, folder(seat), workers(seat)) for seat in seats],
                "edges": [self.edge(source.member, target.member) for source, target in links if source.pod == target.pod == pod]}

    @staticmethod
    def edge(source: str, target: str) -> dict:
        return {"kind": EdgeKind.DELEGATES_TO.value, "from": source, "to": target}

    def member(self, seat: Seat, cwd: Path, worker: SeatWorker) -> dict:
        provider = self.providers.lookup(seat.provider)
        if provider.openrig_permissions_field == "codex_permissions":
            self.codex_route_rules(cwd)
        member = {"id": seat.member, "agent_ref": f"local:agents/{seat.agent()}", "runtime": provider.openrig_runtime, "profile": PROFILE, "cwd": str(cwd), "model": seat.model,
                  "env": self.variables(worker), provider.openrig_permissions_field: self.permissions(provider, seat, cwd)}
        if seat.effort:
            member["effort"] = seat.effort
        return member

    @staticmethod
    def codex_route_rules(cwd: Path) -> Path:
        """Write the route deny rules into the trusted project's active Codex rules layer."""
        path = cwd.resolve() / ".codex" / "rules" / "journal-organization-route.rules"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(CODEX_ROUTE_RULES)
        return path

    def variables(self, worker: SeatWorker) -> dict[str, str]:
        launched = self.setup.variables(worker.environment, worker.actor, worker.token)
        path = (str(self.command().parent), *filter(None, (os.environ.get("PATH", ""),)))
        shell_path_command = self.shell_path_command()
        prompt_command = "; ".join(filter(None, (launched.get("PROMPT_COMMAND", ""), shell_path_command)))
        routed = {ORGANIZATION_SEAT: worker.organization_seat, ORGANIZATION_RIG: worker.organization_rig}
        return {**{name: launched[name] for name in SEAT_VARIABLES}, **{name: value for name, value in routed.items() if value}, "PATH": os.pathsep.join(path),
                "BASH_ENV": str(self.shell_path_file()), "PROMPT_COMMAND": prompt_command}

    def shell_path_command(self) -> str:
        """Put this project's journal bin first after OpenRig's login shell startup."""
        command_folder = shlex.quote(str(self.command().parent))
        return f'PATH={command_folder}${{PATH:+":$PATH"}}; export PATH'

    def shell_path_file(self) -> Path:
        """Restore this project's journal bin in noninteractive Bash shells."""
        path = self.config.home / "runtime" / "journal-shell-path.sh"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{self.shell_path_command()}\n")
        path.chmod(OWNER_ONLY)
        return path

    def permissions(self, provider: Provider, seat: Seat, cwd: Path) -> dict:
        if provider.openrig_permissions_field == "codex_permissions":
            return {"sandbox": "workspace-write" if seat.writes else "read-only", "approval": "never", **({"network_access": True} if seat.writes else {})}
        if provider.openrig_permissions_field != "claude_permissions":
            raise ValueError(f"OpenRig permissions are not configured for {provider.name}")
        allow = [f"Read({cwd.resolve()}/**)"] if "Read" in seat.tools else []
        journal_command = os.path.relpath(self.command(), cwd.resolve())
        journal_commands = tuple(dict.fromkeys(("journal", str(self.command()), journal_command)))
        worker_verbs = ("send", "check", "merge")
        worker_commands = tuple(f"Bash({command} worker {verb} *)" for command in journal_commands for verb in worker_verbs)
        scoped_commands = tuple(f"JOURNAL_ENV=* {command}" for command in journal_commands)
        scoped_worker_commands = tuple(f"Bash({command} worker {verb} *)" for command in scoped_commands for verb in worker_verbs)
        scoped_task_commands = tuple(f"Bash({command} task *)" for command in scoped_commands)
        scoped_proof_commands = tuple(
            f"Bash({command} {noun} *)" for command in scoped_commands for noun in ("proof", "clock-out")
        )
        allow.extend((
            *WORKER_COMMANDS, f"Bash({self.command()} *)", "Bash(journal *)", *worker_commands,
            *scoped_worker_commands, *scoped_task_commands, *scoped_proof_commands,
            *(tool for tool in seat.tools if tool != "Read"),
        ))
        return {"allow": allow, "deny": [*DENIED, *(() if seat.writes else EDIT_TOOLS)]}

    def command(self) -> Path:
        return self.config.home / "bin" / "journal"

    def agent(self, folder: Path, seat: Seat) -> None:
        (folder / GUIDANCE).parent.mkdir(parents=True)
        (folder / GUIDANCE).write_text(seat.guidance)
        provider = self.providers.lookup(seat.provider)
        hooks = self.hook_resource(provider, folder)
        self.written(folder / "agent.yaml", self.agent_spec(seat, self.skills_written(folder / "skills", seat), provider, folder, hooks))

    def hook_resource(self, provider: Provider, folder: Path) -> Path:
        path = folder / provider.openrig_hook_resource_path
        if provider.openrig_hook_resource_type == "codex_config_fragment":
            path.parent.mkdir(parents=True, exist_ok=True)
            command = provider.hook_command(self.config.root)
            path.write_text(self.codex_hook_fragment(provider, command))
            return path
        return self.setup.hook_settings(provider, folder, path)

    @staticmethod
    def codex_hook_fragment(provider: Provider, command: str) -> str:
        lines = []
        hooks = provider.hook_block(command)
        for event, groups in hooks.items():
            for group in groups:
                lines.extend((f"[[hooks.{event}]]", f"matcher = {json.dumps(group.get('matcher', ''))}"))
                for hook in group["hooks"]:
                    lines.append(f"[[hooks.{event}.hooks]]")
                    lines.extend(f"{key} = {RigSpecs.toml_value(value)}" for key, value in hook.items())
        for key, digest in provider.openrig_hook_trust_records(hooks):
            lines.extend((f"[hooks.state.{json.dumps(key)}]", f"trusted_hash = {json.dumps(digest)}"))
        return "\n".join(lines) + "\n"

    @staticmethod
    def toml_value(value: str | int | bool) -> str:
        if isinstance(value, str):
            return json.dumps(value)
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

    def skills_written(self, folder: Path, seat: Seat) -> tuple[str, ...]:
        root = self.folder.path()
        organization = self.skills.folders(root) if root else {}
        catalogue = {skill.name: skill for skill in self.files.catalogue()}
        written = []
        for name in dict.fromkeys((*self.settings.texts(SkillsOptions.START_SKILLS), *seat.skills)):
            if name in organization:
                shutil.copytree(organization[name], folder / name)
                written.append(name)
            elif name in catalogue:
                (folder / catalogue[name].folder).mkdir(parents=True)
                (folder / catalogue[name].folder / SKILL_FILE).write_text(catalogue[name].text())
                written.append(catalogue[name].folder)
        return tuple(written)

    @staticmethod
    def agent_spec(seat: Seat, skills: tuple[str, ...], provider: Provider, folder: Path, hooks: Path) -> dict:
        return {"name": seat.agent(), "version": AGENT_SPEC_VERSION, "description": f"The journal's {seat.qualified}", "defaults": {"runtime": provider.openrig_runtime},
                "profiles": {PROFILE: {"uses": {"skills": list(skills), "guidance": [], "subagents": [], "plugins": [], "runtime_resources": [HOOKS]}}},
                "resources": {"skills": [{"id": skill, "path": f"skills/{skill}"} for skill in skills], "guidance": [{"id": "role", "path": GUIDANCE}],
                              "runtime_resources": [{"id": HOOKS, "path": hooks.relative_to(folder).as_posix(), "runtime": provider.openrig_runtime, "type": provider.openrig_hook_resource_type}]},
                "startup": {"files": [{"path": GUIDANCE, "orientation": "role", "delivery_hint": "send_text", "required": True}], "actions": []}}

    @staticmethod
    def written(path: Path, spec: dict) -> Path:
        path.write_text(json.dumps(spec, indent=2) + "\n")
        return path
