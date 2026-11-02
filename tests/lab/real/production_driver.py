import json
import os
from pathlib import Path
import secrets
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import time
from typing import Mapping
from urllib.request import urlopen

from tests.lab.real.cap_event_server import CapEventServer
from tests.lab.real.isolated_journal import IsolatedJournal
from tests.lab.real.production_boundary import ProductionBoundary
from tests.lab.real.production_watchdog import ProductionWatchdog
from tests.lab.real.provider_proxy import ProviderProxy
from tests.lab.real.run_record import RunRecord
from tests.lab.real.run_record_store import RunRecordStore
from tests.lab.real.run_real_batch import RunRealBatch


class ProductionDriver:
    """Run a pinned journal and organization through a private, capped subscription runtime."""

    def __init__(self, run_id: str, spec: Mapping[str, object], manifest, checkout: Path,
                 organization_repository: Path, watchdog: ProductionWatchdog) -> None:
        self.run_id, self.spec, self.manifest = run_id, dict(spec), manifest
        self.checkout, self.organization_repository = checkout, organization_repository
        self.watchdog = watchdog
        self.journal_port, self.rig_port, self.cap_port, self.proxy_port, self.share_port = self.ports(5)
        virtual_environment = Path(sys.prefix).resolve()
        read_paths = [Path(sys.executable).resolve().parent, virtual_environment,
                      (virtual_environment / "bin").resolve(), Path(sys.base_prefix).resolve()]
        read_paths.extend(Path(path).resolve() for path in sys.path
                          if path and "site-packages" in path and Path(path).exists())
        self.cli_interpreters: dict[str, Path] = {}
        for program in (str(spec["provider"]), "rig"):
            if executable := self.executable(program):
                read_paths.append(executable.parent)
                if interpreter := self.cli_interpreter(executable):
                    name, path, uses_path = interpreter
                    read_paths.append(path)
                    if uses_path:
                        if name in self.cli_interpreters and self.cli_interpreters[name] != path:
                            raise ValueError(f"agent CLIs require different {name} interpreters")
                        self.cli_interpreters[name] = path
        self.boundary = ProductionBoundary(
            run_id,
            (self.journal_port, self.rig_port, self.cap_port, self.proxy_port, self.share_port),
            tuple(dict.fromkeys(read_paths)),
        )
        self.processes: list[subprocess.Popen] = []
        self.journal_process: subprocess.Popen | None = None
        self.event_server: CapEventServer | None = None
        self.proxy: ProviderProxy | None = None
        self.paths: Mapping[str, Path] = {}
        self.env: dict[str, str] = {}
        self.caps = None
        self.rig_started = False
        self.token = secrets.token_urlsafe(32)
        self.stopped = False
        self.watchdog.register(self)

    def materialize_project(self, spec: Mapping[str, object], paths: Mapping[str, Path]) -> dict[str, object]:
        project, organization = paths["project"], paths["runtime"] / "organization"
        self.git_snapshot(self.checkout, project, str(spec["journal_commit"]))
        self.git_snapshot(self.organization_repository, organization, str(spec["organization_commit"]))
        self.paths = {**paths, "organization": organization}
        self.install_cap_hook(project, paths)
        return {"journal_commit": self.head(project), "organization_commit": self.head(organization),
                "journal_port": self.journal_port}

    def start_journal(self, paths: Mapping[str, Path], _shim: Path, run_id: str, launch_id: str,
                      challenge: str, port: int, caps) -> dict[str, object]:
        self.caps = caps
        if caps is not None:
            self.event_server = CapEventServer(caps, self.token, self.cap_port)
            if self.event_server.start() != self.cap_port:
                raise ValueError("run cap event server did not bind its reserved port")
            self.proxy = ProviderProxy(self.proxy_port)
            self.proxy.start()
        self.install_share_port(paths)
        self.env = self.child_environment(paths, port)
        stdout = (paths["runtime"] / "journal.stdout.log").open("ab")
        stderr = (paths["runtime"] / "journal.stderr.log").open("ab")
        command = self.boundary.wrap([sys.executable, str(paths["project"] / "src" / "journal.py"), "serve"])
        process = subprocess.Popen(command, cwd=paths["project"], env=self.env, stdin=subprocess.DEVNULL,
                                   stdout=stdout, stderr=stderr, start_new_session=True)
        self.journal_process = process
        self.processes.append(process)
        return self.wait_identity(process, paths, run_id, launch_id, challenge, port)

    def install_share_port(self, paths: Mapping[str, Path]) -> None:
        home = paths["project"] / ".journal"
        home.mkdir(mode=0o700, exist_ok=True)
        sharing = home / "sharing.json"
        with sharing.open("x", encoding="utf-8") as record:
            json.dump({"port": self.share_port}, record)
        sharing.chmod(0o600)

    def load_scenario(self, scenario: str, paths: Mapping[str, Path]) -> dict[str, object]:
        expected = paths["project"] / "tests" / "lab" / "scenarios" / str(self.spec["business_type"]) / f"{scenario}.toml"
        if not expected.is_file() or expected.is_symlink():
            raise ValueError("scenario is absent from the pinned journal commit")
        return {"path": expected, "id": scenario}

    def child_environment(self, paths: Mapping[str, Path], port: int) -> dict[str, str]:
        provider = str(self.spec["provider"])
        cli, rig = self.executable(provider), self.executable("rig")
        if not cli or not rig:
            raise ValueError("the signed-in provider CLI and OpenRig CLI must be installed")
        for name, interpreter in self.cli_interpreters.items():
            self.install_executable(paths, name, interpreter)
        self.install_executable(paths, provider, cli)
        self.install_executable(paths, "rig", rig)
        path_entries = tuple(dict.fromkeys((cli.parent, rig.parent, Path("/usr/bin"),
                                            Path("/bin"), Path("/opt/homebrew/bin"))))
        env = IsolatedJournal(paths["root"], self.checkout).child_environment(
            paths, os.environ, ("PATH", "LANG", "LC_ALL", "TERM"), (), port,
            "agent", secrets.token_urlsafe(32), path_entries,
        )
        hook = paths["runtime"] / "cap-hook.py"
        source = Path(__file__).with_name("cap_hook.py")
        hook.write_text(f"#!{sys.executable}\n" + source.read_text(encoding="utf-8"), encoding="utf-8")
        hook.chmod(0o700)
        env.update({
            "JOURNAL_LAB_CAP_HOOK": str(hook),
            "JOURNAL_LAB_CAP_URL": f"http://127.0.0.1:{self.cap_port}/event",
            "JOURNAL_LAB_CAP_TOKEN": self.token,
            "OPENRIG_HOME": str(paths["runtime"] / "openrig"),
            "OPENRIG_URL": f"http://127.0.0.1:{self.rig_port}",
            "HTTPS_PROXY": f"http://127.0.0.1:{self.proxy_port}",
            "HTTP_PROXY": f"http://127.0.0.1:{self.proxy_port}",
            "NO_PROXY": "localhost,127.0.0.1",
            "TMUX_TMPDIR": str(paths["runtime"] / "tmux"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(paths["runtime"] / "gitconfig"),
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_TERMINAL_PROMPT": "0",
        })
        return env

    def probe_agent_cli(self, paths: Mapping[str, Path]) -> dict[str, str]:
        provider = str(self.spec["provider"])
        result = self.command([str(paths["bin"] / provider), "--version"], paths)
        if result.returncode:
            raise ValueError(result.stderr.strip() or f"{provider} CLI version probe failed")
        version = result.stdout.strip() or result.stderr.strip()
        if not version:
            raise ValueError(f"{provider} CLI version probe returned no version")
        return {"provider": provider, "version": version.splitlines()[0]}

    def prepare_plan(self, scenario: Mapping[str, object], paths: Mapping[str, Path]) -> str:
        setup = self.setup_scenario(scenario, paths)
        (paths["runtime"] / "openrig").mkdir(mode=0o700, exist_ok=True)
        (paths["runtime"] / "tmux").mkdir(mode=0o700, exist_ok=True)
        return str(setup["plan_id"])

    def start_plan(self, scenario: Mapping[str, object], paths: Mapping[str, Path], _caps) -> str:
        plan_id = self.prepare_plan(scenario, paths)
        rig = self.executable("rig")
        if not rig:
            raise ValueError("OpenRig CLI is required for an organization-mode run")
        start = self.command([str(rig), "daemon", "start", "--host", "127.0.0.1", "--port", str(self.rig_port),
                              "--db", str(paths["runtime"] / "openrig.db"), "--no-kernel"], paths)
        if start.returncode:
            raise ValueError(start.stderr.strip() or "private OpenRig daemon did not start")
        self.rig_started = True
        journal = [sys.executable, str(paths["project"] / "src" / "journal.py")]
        started = self.command([*journal, "plan", "start", plan_id], paths)
        if started.returncode:
            raise ValueError(started.stderr.strip() or "journal refused to start the approved plan")
        return plan_id

    def wait_for_end_or_cap(self, _run_id: str, plan_id: str, caps) -> str:
        while True:
            if caps.read().get("cap_reached"):
                return "capped"
            if self.journal_process and self.journal_process.poll() is not None:
                raise ValueError("isolated journal server stopped while the plan was running")
            result = self.command([sys.executable, str(self.paths["project"] / "src" / "journal.py"),
                                   "plan", "show", plan_id], self.paths)
            if result.returncode:
                raise ValueError(result.stderr.strip() or "journal could not read the active plan")
            line = result.stdout.splitlines()[0] if result.stdout.splitlines() else ""
            if line.startswith(f"plan {plan_id} done:"):
                return "completed"
            if line.startswith(f"plan {plan_id} cancelled:"):
                return "aborted"
            time.sleep(0.5)

    def read_record(self, run_id: str) -> RunRecord:
        if run_id != self.run_id:
            raise ValueError("isolated journal returned a different run id")
        return RunRecord(run_id, 1, str(self.spec["scenario"]), str(self.spec["business_type"]),
                         str(self.spec["design_digest"]), int(self.spec["seed"]), self.manifest.digest,
                         str(self.spec["journal_commit"]), str(self.spec["organization_commit"]),
                         str(self.spec["provider"]), str(self.spec["model"]),
                         str(self.spec["metric_schema_version"]), "completed", 0.0)

    @staticmethod
    def plan_commits_reached_main(_plan_id: str, _paths: Mapping[str, Path]) -> bool | None:
        return None

    @staticmethod
    def outside_worktree_changes(_paths: Mapping[str, Path]) -> tuple[str, ...]:
        return ()

    def stop_owned(self, _reason: str = "run finished") -> bool:
        if self.stopped:
            return True
        self.stopped = True
        confirmed = True
        if self.event_server:
            self.event_server.close()
            self.event_server = None
        if self.proxy:
            self.proxy.close()
            self.proxy = None
        rig = self.executable("rig") if self.rig_started else None
        if rig and self.env.get("OPENRIG_HOME"):
            stopped = subprocess.run(self.boundary.wrap([str(rig), "daemon", "stop"]), env=self.env,
                                     cwd=self.paths.get("project"), stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, timeout=10, check=False)
            confirmed = stopped.returncode == 0
            self.rig_started = not confirmed
        for process in self.processes:
            if process.poll() is not None:
                continue
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
                except (OSError, subprocess.TimeoutExpired):
                    confirmed = False
            if process.poll() is None:
                confirmed = False
        return confirmed

    def command(self, command: list[str], paths: Mapping[str, Path]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(self.boundary.wrap(command), cwd=paths["project"], env=self.env,
                              capture_output=True, text=True, timeout=60, check=False)

    def setup_scenario(self, scenario: Mapping[str, object], paths: Mapping[str, Path]) -> dict[str, object]:
        harness = self.stage_lab_harness(paths)
        script = '''import json, sys
from pathlib import Path
project, harness, scenario_path, organization = map(Path, sys.argv[1:5])
settings = json.loads(sys.argv[5])
sys.path[:0] = [str(project / "src"), str(harness), str(project)]
from journal.app import App
from journal.config import Config
from journal.models.plan_mode import PlanMode
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.plans.plans_options import PlansOptions
from journal.features.organization.support.organization import Organization
from tests.lab.business_type import BusinessType
from tests.lab.lab_scenario import LabScenario
from tests.lab.scenario_loader import ScenarioLoader
from tests.user_settings import user_set
app = App(Config.rooted(project))
business_type = harness / "tests" / "lab" / "business_types" / f"{scenario_path.parent.name}.toml"
business = BusinessType.read(business_type)
user_set(app, OrganizationOptions.FOLDER.key, str(organization))
user_set(app, PlansOptions.PLAN_AGENTS.key, True)
for key, value in settings.items():
    user_set(app, key, value)
scenario = LabScenario.read(scenario_path)
domain_map = business.organization_domain_map
contracts = app.container.get(Organization).contracts()
scenario_domains = {task["domain"] for phase in scenario.phases for task in phase["tasks"]}
for scenario_domain in scenario_domains:
    organization_domain = domain_map.get(scenario_domain)
    if not organization_domain:
        raise ValueError(f"scenario domain {scenario_domain!r} has no pinned organization mapping")
    if contracts.domain(organization_domain) is None:
        raise ValueError(f"scenario domain {scenario_domain!r} maps to {organization_domain!r}, absent from pinned organization")
plan = ScenarioLoader(app).load(scenario, PlanMode.ORGANIZATION, domain_map)
print(plan["plan_id"])
'''
        design = self.manifest.data().get("design", {})
        settings = design.get("settings", {}) if isinstance(design, Mapping) else {}
        if not isinstance(settings, Mapping):
            raise ValueError("approved manifest design settings must be a table")
        encoded_settings = json.dumps(dict(settings), separators=(",", ":"))
        result = subprocess.run(self.boundary.wrap([sys.executable, "-c", script,
                                 str(paths["project"]), str(harness), str(scenario["path"]),
                                 str(paths["runtime"] / "organization"), encoded_settings]),
                                cwd=paths["project"], env=self.env, capture_output=True,
                                text=True, timeout=60, check=False)
        if result.returncode:
            raise ValueError(result.stderr.strip() or "pinned journal could not load the approved scenario")
        plan_id = result.stdout.strip().splitlines()[-1]
        if not plan_id.isdecimal():
            raise ValueError("pinned journal did not return an approved plan id")
        return {"plan_id": int(plan_id)}

    def stage_lab_harness(self, paths: Mapping[str, Path]) -> Path:
        harness = paths["runtime"] / "driver-harness"
        tests = harness / "tests"
        tests.mkdir(mode=0o700, parents=True)
        source = self.checkout / "tests"
        shutil.copytree(source / "lab", tests / "lab", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in ("__init__.py", "in_process.py", "user_settings.py"):
            shutil.copy2(source / name, tests / name)
        return harness

    def install_cap_hook(self, project: Path, paths: Mapping[str, Path]) -> None:
        path = project / "src" / "journal" / "hooks" / "hook.sh"
        text = path.read_text(encoding="utf-8")
        event_line = 'event=$(sed -n \'s/.*"hook_event_name": *"\\([A-Za-z]*\\)".*/\\1/p\' "$sent" | head -1)'
        firing_line = 'firing="$$-$begun"'
        if event_line not in text:
            raise ValueError("pinned journal hook cannot identify run cap events")
        text = text.replace(event_line + "\n", "", 1)
        index = text.find(firing_line)
        if index < 0:
            raise ValueError("pinned journal hook cannot forward run cap events")
        end = text.find("\n", index) + 1
        forwarding = (
            event_line + "\n"
            'case "$event" in\n'
            '    SessionStart|SessionEnd|UserPromptSubmit)\n'
            '        "${JOURNAL_LAB_CAP_HOOK:?}" "$sent" "$firing" || { rm -f "$body" "$sent"; exit 2; } ;;\n'
            'esac\n'
        )
        path.write_text(text[:end] + forwarding + text[end:], encoding="utf-8")
        (paths["runtime"] / "gitconfig").write_text("[protocol]\n\tallow = never\n", encoding="utf-8")

    def wait_identity(self, process: subprocess.Popen, paths: Mapping[str, Path], run_id: str,
                      launch_id: str, challenge: str, port: int) -> dict[str, object]:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise ValueError("isolated journal server stopped during startup")
            try:
                with urlopen(f"http://127.0.0.1:{port}/journal/identity", timeout=1) as answer:
                    identity = json.load(answer)
                if identity.get("root") == str((paths["project"] / ".journal").resolve()) and identity.get("pid") == process.pid:
                    return {**identity, "run_id": run_id, "launch_id": launch_id, "challenge": challenge,
                            "host": "127.0.0.1", "port": port, "authenticated": True}
            except (OSError, ValueError):
                time.sleep(0.2)
        raise ValueError("isolated journal identity did not answer on its private loopback port")

    @staticmethod
    def ports(count: int) -> tuple[int, ...]:
        ports = []
        for _ in range(count):
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                ports.append(listener.getsockname()[1])
        return tuple(ports)

    @staticmethod
    def git_snapshot(source: Path, target: Path, commit: str) -> None:
        if not source.is_absolute() or not source.is_dir() or not (source / ".git").exists():
            raise ValueError(f"pinned source repository is unavailable: {source}")
        if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit.lower()):
            raise ValueError("approved repository revisions must be full commit ids")
        environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "GIT_CONFIG_NOSYSTEM": "1",
                       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0", "GIT_ALLOW_PROTOCOL": "file"}
        ProductionDriver.git(["init", "--quiet", str(target)], environment)
        ProductionDriver.git(["-C", str(target), "fetch", "--quiet", "--no-tags", "--no-recurse-submodules",
                              str(source), commit], environment)
        ProductionDriver.git(["-C", str(target), "checkout", "--quiet", "--detach", "FETCH_HEAD"], environment)
        if ProductionDriver.head(target) != commit:
            raise ValueError("materialized repository revision differs from the approved commit")
        remotes = ProductionDriver.git(["-C", str(target), "remote", "-v"], environment)
        if remotes.stdout.strip():
            raise ValueError("isolated repository unexpectedly has a configured git remote")

    @staticmethod
    def git(command: list[str], environment: Mapping[str, str]) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(["git", *command], env=dict(environment), capture_output=True, text=True, check=False)
        if result.returncode:
            raise ValueError(result.stderr.strip() or "pinned repository checkout failed")
        return result

    @staticmethod
    def head(repository: Path) -> str:
        result = subprocess.run(["git", "-C", str(repository), "rev-parse", "HEAD"], capture_output=True,
                                text=True, check=False)
        if result.returncode:
            raise ValueError("isolated repository has no checked-out commit")
        return result.stdout.strip()

    @staticmethod
    def executable(program: str) -> Path | None:
        selected = shutil.which(program)
        return Path(selected).resolve() if selected else None

    @staticmethod
    def cli_interpreter(executable: Path) -> tuple[str, Path, bool] | None:
        if not executable.is_file():
            return None
        with executable.open("rb") as source:
            first_line = source.readline().decode("utf-8", "replace").strip()
        if not first_line.startswith("#!"):
            return None
        command = shlex.split(first_line[2:])
        if not command:
            raise ValueError(f"agent CLI has an empty interpreter declaration: {executable}")
        if Path(command[0]).name == "env":
            if len(command) == 2:
                name = command[1]
            elif len(command) > 2 and command[1] == "-S":
                split_command = shlex.split(" ".join(command[2:]))
                if not split_command:
                    raise ValueError(f"agent CLI has an empty env interpreter declaration: {executable}")
                name = split_command[0]
            else:
                raise ValueError(f"agent CLI has an unsupported env interpreter declaration: {executable}")
            selected = shutil.which(name)
            if not selected:
                raise ValueError(f"agent CLI requires an installed {name} interpreter")
            return name, Path(selected).resolve(), True
        path = Path(command[0]).resolve()
        if not path.is_file():
            raise ValueError(f"agent CLI interpreter does not exist: {path}")
        return path.name, path, False

    @staticmethod
    def install_executable(paths: Mapping[str, Path], name: str, executable: Path) -> Path:
        link = paths["bin"] / name
        if link.exists() or link.is_symlink():
            raise ValueError(f"isolated executable already exists: {name}")
        link.symlink_to(executable)
        return link

    @staticmethod
    def default_organization_repository(checkout: Path) -> Path:
        repository = checkout.resolve()
        worktree_git_file = repository / ".git"
        if worktree_git_file.is_file():
            reference = worktree_git_file.read_text(encoding="utf-8").strip()
            if reference.startswith("gitdir: "):
                git_directory = Path(reference.removeprefix("gitdir: "))
                if not git_directory.is_absolute():
                    git_directory = repository / git_directory
                git_directory = git_directory.resolve()
                common_directory = git_directory / "commondir"
                if common_directory.is_file():
                    common_reference = Path(common_directory.read_text(encoding="utf-8").strip())
                    if not common_reference.is_absolute():
                        common_reference = git_directory / common_reference
                    common_directory = common_reference.resolve()
                    if common_directory.name == ".git":
                        repository = common_directory.parent
        return repository.parent / "agentic-organization-journal"


def build(manifest, approvals, batch_home: Path) -> RunRealBatch:
    checkout = Path(__file__).resolve().parents[3]
    organization_repository = Path(os.environ.get("JOURNAL_LAB_ORGANIZATION_REPOSITORY") or
                                    ProductionDriver.default_organization_repository(checkout)).expanduser().resolve()
    journal = IsolatedJournal(batch_home, checkout, (organization_repository, Path.home() / ".journal"))
    watchdog = ProductionWatchdog()
    drivers: dict[str, ProductionDriver] = {}

    def driver_factory(run_id: str, spec: Mapping[str, object]) -> ProductionDriver:
        driver = ProductionDriver(run_id, spec, manifest, checkout, organization_repository, watchdog)
        drivers[run_id] = driver
        return driver

    def boundary_factory(run_id: str) -> ProductionBoundary:
        return drivers[run_id].boundary

    return RunRealBatch(approvals, journal, driver_factory, boundary_factory, RunRecordStore(),
                        batch_home / "run-caps.json", watchdog)
