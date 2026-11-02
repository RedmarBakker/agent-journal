#!/usr/bin/env python3
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, "/opt/agent-journal/src")

from journal.app import App
from journal.config import Config
from journal.db.connection import Connection
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from journal.repositories.agents import Agents
from journal.repositories.checks import Checks
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.templates import Templates
from journal.repositories.workers import Workers
from journal.supervisor_authority import SupervisorAuthority
from journal.supervisor_link import SupervisorLink
from supervisor_bridge.proposal_evaluation import load_seed

ROOT = Path("/data/project")
API = "http://127.0.0.1:8421"
TOKEN_FILE = Path("/run/journal_supervisor_credential")
PLAN_TITLE = "Supervisor live smoke"
PLAN_BRIEF = "Run one bounded supervisor diagnosis of the deliberately failing smoke check."
PHASE_TITLE = "Bounded supervisor smoke"
PHASE_COMPLETION = "the bounded supervisor smoke has a verified receipt"
TASK_TITLE = "Diagnose the smoke failure before executing the seed task"
TASK_BRIEF = "The bounded supervisor diagnoses the deliberately failing smoke check before this seed task executes."
CHECK_TITLE = "Supervisor live smoke failure"
CHECK_BRIEF = "This smoke check intentionally fails so the supervisor has one current failure to diagnose."
TEMPLATE_TITLE = "Supervisor diagnostic"
TEMPLATE_BRIEF = "Read the deliberately failing smoke check and prepare one bounded diagnostic task for the current phase."
TEMPLATE_PURPOSE = "diagnose the failed service check"
CHECK_COMMAND = "false"
WAIT_SECONDS = 300
CASE_SEED_FILE = Path("/run/journal-proposal-case-seed.json")


class SetupFailure(Exception):
    pass


def request(path, body):
    request = Request(
        API + path,
        data=json.dumps(body, separators=(",", ":")).encode(),
        headers={"Content-Type": "application/json", "X-Journal-Env": "main"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, response.headers, json.load(response)
    except (HTTPError, URLError, TimeoutError) as error:
        raise SetupFailure("the staged journal did not accept the fixed setup request") from error


def command(*argv, expected_code=0):
    status, _headers, answer = request("/cli", {"argv": list(argv), "env": "main", "provider": "codex", "agent": False})
    if status != 200 or not isinstance(answer, dict) or answer.get("code") != expected_code:
        raise SetupFailure("the owner CLI refused a fixed supervisor setup command")
    return answer.get("text", "").strip()


def row_number(output, pattern):
    matched = re.fullmatch(pattern, output)
    if not matched:
        raise SetupFailure("the journal returned an unexpected row number for fixed setup")
    return int(matched.group(1))


def require_runtime(app):
    if os.environ.get("JOURNAL_ROOT") != str(ROOT):
        raise SetupFailure("the setup must run in the designated writer installation")
    if TOKEN_FILE.exists():
        raise SetupFailure("a supervisor setup credential already exists in this writer")
    scope = app.container.get(Scope)
    environments = app.container.get(Environments)
    agents = app.container.get(Agents)
    workers = app.container.get(Workers)
    supervisor = app.container.get(SupervisorLink)
    main = environments.existing("main")
    with scope.environment(main.row_id):
        owner_agent = agents.environment_main_agent(main.row_id)
    active_workers = workers.global_matching(state=WorkerState.DISPATCHED)
    if active_workers:
        raise SetupFailure("active workers need B10 filesystem and network denial probes before enrollment")
    if not owner_agent or owner_agent.provider != "codex" or not owner_agent.session or not supervisor.runs(main.row_id):
        raise SetupFailure("start the owner's real Codex session on the designated writer before setup")
    return main


def wait_for_owner_runtime(app):
    deadline = time.monotonic() + WAIT_SECONDS
    while time.monotonic() < deadline:
        app.container.get(Connection).cache.cleared()
        try:
            return require_runtime(app)
        except SetupFailure as error:
            if str(error) != "start the owner's real Codex session on the designated writer before setup":
                raise
            time.sleep(1)
    raise SetupFailure("the owner-started Codex session did not become live in the writer")


def setup_plan_matches(plan, phases, tasks, seed=None):
    if seed is not None:
        return (
            plan.title == seed["plan"]["title"]
            and plan.brief == seed["plan"]["brief"]
            and plan.state == PlanState.STARTED
            and plan.mode == PlanMode.SOLO
            and plan.mode_chosen
            and len(phases) == 1
            and phases[0].title == f"Evaluation phase {seed['case_id']}"
            and phases[0].completion_rule == PHASE_COMPLETION
            and smoke_tasks_match(tasks, seed)
        )
    return (
        plan.title == PLAN_TITLE
        and plan.brief == PLAN_BRIEF
        and plan.state == PlanState.STARTED
        and plan.mode == PlanMode.SOLO
        and plan.mode_chosen
        and len(phases) == 1
        and phases[0].title == PHASE_TITLE
        and phases[0].completion_rule == PHASE_COMPLETION
        and smoke_tasks_match(tasks)
    )


def smoke_tasks_match(tasks, seed=None):
    if len(tasks) != 1:
        return False
    task, = tasks
    if seed is not None:
        return (task.title == seed["tasks"]["title"] and task.brief == seed["tasks"]["brief"]
                and task.state == TaskState.OPEN and task.supervisor_reserved)
    return (task.title == TASK_TITLE and task.brief == TASK_BRIEF
            and task.state == TaskState.OPEN and task.supervisor_reserved)


def setup_check_id(app, seed=None):
    title = seed["checks"]["title"] if seed else CHECK_TITLE
    brief = seed["checks"]["brief"] if seed else CHECK_BRIEF
    command_text = seed["checks"]["command"] if seed else CHECK_COMMAND
    rows = [check for check in app.container.get(Checks).matching(title=title)
            if check.brief == brief and check.command == command_text
            and check.interval == 10 and not check.wait_target and not check.is_retired]
    if len(rows) != 1:
        raise SetupFailure("the staged supervisor setup check is missing or ambiguous")
    return rows[0].row_id


def setup_template_id(app):
    rows = [template for template in app.container.get(Templates).matching(title=TEMPLATE_TITLE)
            if template.brief == TEMPLATE_BRIEF and template.purpose == TEMPLATE_PURPOSE
            and template.targets == ("plan",)]
    if len(rows) != 1:
        raise SetupFailure("the staged supervisor setup template is missing or ambiguous")
    return str(rows[0].row_id)


def resume_plan(app, main, plan_id, seed=None):
    scope = app.container.get(Scope)
    plans = app.container.get(Plans)
    with scope.environment(main.row_id):
        plan = plans.find(plan_id)
        phases = plans.plan_phases(plan)
        tasks = plans.plan_tasks(plan)
    if seed is None:
        if not setup_plan_matches(plan, phases, tasks):
            raise SetupFailure("a supervisor live smoke plan already exists; revoke and reset this staging installation")
    elif not setup_plan_matches(plan, phases, tasks, seed):
        raise SetupFailure("a supervisor live smoke plan already exists; revoke and reset this staging installation")
    authority = app.container.get(SupervisorAuthority)
    if authority.has_enrollment_grant():
        raise SetupFailure("a supervisor enrollment grant already exists in this writer")
    check_id = setup_check_id(app, seed)
    return plan_id, check_id, setup_template_id(app)


def existing_plan_id(output, seed=None):
    title = seed["plan"]["title"] if seed else PLAN_TITLE
    matches = []
    for line in output.splitlines():
        fields = line.split(maxsplit=2)
        if len(fields) == 3 and fields[2] == title:
            if not fields[0].isdigit():
                raise SetupFailure("the journal returned an unexpected row number for the live smoke plan")
            matches.append(int(fields[0]))
    if len(matches) > 1:
        raise SetupFailure("more than one supervisor live smoke plan already exists")
    return matches[0] if matches else None


def make_plan(app, main, seed=None):
    existing = command("plan", "list")
    if seed is None:
        if plan_id := existing_plan_id(existing):
            return resume_plan(app, main, plan_id)
    elif plan_id := existing_plan_id(existing, seed):
        return resume_plan(app, main, plan_id, seed)
    if seed is not None:
        return make_case_plan(app, seed)
    plan_id = row_number(command("plan", "create", PLAN_TITLE, "--brief", PLAN_BRIEF), r"plan (\d+) draft")
    command("plan", "mode", str(plan_id), PlanMode.SOLO.value)
    command("plan", "phase", str(plan_id), PHASE_TITLE, "--when", PHASE_COMPLETION)
    task_id = row_number(command("plan", "add", str(plan_id), TASK_TITLE, "--brief", TASK_BRIEF, "--phase", "1"), r"task (\d+) added to plan .+")
    status, _headers, task = request(f"/journal/tasks/{task_id}", {"supervisor_reserved": True})
    if status != 200 or task.get("supervisor_reserved") is not True:
        raise SetupFailure("the owner could not reserve the smoke seed for supervisor diagnosis")
    check_id = row_number(command("check", "create", CHECK_TITLE, "--command", CHECK_COMMAND, "--brief", CHECK_BRIEF, "--every", "10"), r"check (\d+): .+")
    template_id = row_number(command("template", "create", TEMPLATE_TITLE, "--brief", TEMPLATE_BRIEF, "--applies-to", "plan", "--purpose", TEMPLATE_PURPOSE), r"template (\d+): .+")
    command("settings", "set", "plans.plan_agents", "on")
    command("plan", "ready", str(plan_id))
    command("plan", "approve", str(plan_id))
    command("plan", "start", str(plan_id))
    return plan_id, check_id, template_id


def make_case_plan(app, seed):
    plan_id = row_number(command("plan", "create", seed["plan"]["title"], "--brief", seed["plan"]["brief"]), r"plan (\d+) draft")
    command("plan", "mode", str(plan_id), PlanMode.SOLO.value)
    command("plan", "phase", str(plan_id), f"Evaluation phase {seed['case_id']}", "--when", PHASE_COMPLETION)
    task_id = row_number(command("plan", "add", str(plan_id), seed["tasks"]["title"], "--brief", seed["tasks"]["brief"], "--phase", "1"), r"task (\d+) added to plan .+")
    status, _headers, task = request(f"/journal/tasks/{task_id}", {"supervisor_reserved": True})
    if status != 200 or task.get("supervisor_reserved") is not True:
        raise SetupFailure("the owner could not reserve the evaluation task for supervisor diagnosis")
    check_id = row_number(command("check", "create", seed["checks"]["title"], "--command", seed["checks"]["command"], "--brief", seed["checks"]["brief"], "--every", "10"), r"check (\d+): .+")
    template_id = row_number(command("template", "create", TEMPLATE_TITLE, "--brief", TEMPLATE_BRIEF, "--applies-to", "plan", "--purpose", TEMPLATE_PURPOSE), r"template (\d+): .+")
    command("settings", "set", "plans.plan_agents", "on")
    command("plan", "ready", str(plan_id))
    command("plan", "approve", str(plan_id))
    command("plan", "start", str(plan_id))
    return plan_id, check_id, template_id


def ensure_smoke_task(app, main, plan_id, seed=None):
    app.container.get(Connection).cache.cleared()
    scope = app.container.get(Scope)
    plans = app.container.get(Plans)
    tasks_repo = app.container.get(Tasks)
    with scope.environment(main.row_id):
        plan = plans.find(plan_id)
        tasks = plans.plan_tasks(plan)
        rows_match = smoke_tasks_match(tasks) if seed is None else smoke_tasks_match(tasks, seed)
        task_unheld = (len(tasks) == 1 and tasks[0].state == TaskState.OPEN and tasks[0].supervisor_reserved and not tasks[0].delegated
                       and tasks_repo.holder(tasks[0]) is None
                       and not tasks_repo.unavailable_task_ids(tasks))
        no_task_in_hand = plans.started_task(plan) is None
    if not rows_match or not task_unheld or not no_task_in_hand:
        raise SetupFailure("the live Plan driver must stay idle with one open, unheld diagnostic task")


def run_bound_check(check_id, seed=None):
    output = command("check", "run", str(check_id), expected_code=1)
    if not output.startswith(f"check {check_id} failed:"):
        raise SetupFailure("the enrolled smoke check did not fail as designed")


def run_case_checks(check_id, seed):
    for verdict in seed["checks"]["results"]:
        output = command("check", "run", str(check_id), expected_code=1 if verdict == "failed" else 0)
        if not output.startswith(f"check {check_id} {verdict}:"):
            raise SetupFailure("the evaluation check did not produce its seeded result")


def wait_for_codex_plan(app, plan_id, environment_id):
    deadline = time.monotonic() + WAIT_SECONDS
    while time.monotonic() < deadline:
        app.container.get(Connection).cache.cleared()
        scope = app.container.get(Scope)
        plans = app.container.get(Plans)
        plan_agents = app.container.get(PlanAgents)
        with scope.environment(environment_id):
            plan = plans.find(plan_id)
        agent = plan_agents.agent(plan)
        environment = plan_agents.environment(plan)
        if (plan.mode == PlanMode.SOLO and agent and agent.provider == "codex" and agent.session
                and environment and plan_agents.is_running(environment)):
            return agent
        time.sleep(1)
    raise SetupFailure("the owner-started Codex Plan agent did not become live in the writer")


def enrollment(app, plan_id, check_id, template_id, seed=None):
    authority = app.container.get(SupervisorAuthority)
    context = authority.enrollment_context(plan_id, (check_id,), str(template_id))
    check_command = seed["checks"]["command"] if seed else CHECK_COMMAND
    return {
        "protocol_version": 1,
        "plan_id": plan_id,
        "current_phase": context["current_phase"],
        "expected_plan_revision": context["expected_plan_revision"],
        "expected_binding_revision": context["expected_binding_revision"],
        "checks": [{
            "check_id": check_id,
            "command_sha256": authority._command_hash(check_command),
            "baseline_interval_minutes": 10,
            "minimum_interval_minutes": 5,
            "expected_revision": context["check_revisions"][str(check_id)],
        }],
        "diagnostic_template_id": str(template_id),
        "diagnostic_template_revision": context["diagnostic_template_revision"],
        "capabilities": {
            "diagnostic_task": True,
            "plan_priorities": True,
            "check_interval": True,
            "sequence": False,
            "phrase_nudge": False,
            "project_reminder": False,
        },
        "limits": {
            "max_turns_per_day": 1,
            "max_input_tokens_per_turn": 80000,
            "max_output_tokens_per_turn": 8000,
            "max_provider_requests_per_turn": 8,
            "max_turn_seconds": 600,
            "max_cost_microusd_per_day": 1000000,
            "max_bundles_per_project_day": 20,
            "max_bundles_per_episode_day": 1,
            "max_new_diagnostics_per_episode": 1,
        },
        "mode": "bounded_write",
        "valid_until_ms": int((time.time() + 3600) * 1000),
    }


def write_token(token):
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,128}", token):
        raise SetupFailure("the enrollment route returned an invalid service credential")
    descriptor = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
    with os.fdopen(descriptor, "w", encoding="ascii") as output:
        output.write(token)
        output.flush()
        os.fsync(output.fileno())
    os.chmod(TOKEN_FILE, 0o400)


def revoke(grant_id):
    request("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": grant_id,
        "expected_grant_version": 1,
        "change": {"kind": "revoke"},
    })


def main():
    if len(sys.argv) != 1:
        raise SetupFailure("this setup program accepts no arguments")
    os.umask(0o077)
    case_id = os.environ.get("JOURNAL_SUPERVISOR_CASE_ID", "").strip()
    seed = load_seed(CASE_SEED_FILE, case_id) if case_id else None
    app = App(Config.rooted(ROOT))
    main = wait_for_owner_runtime(app)
    plan_id, check_id, template_id = make_plan(app, main, seed)
    wait_for_codex_plan(app, plan_id, main.row_id)
    ensure_smoke_task(app, main, plan_id, seed)
    status, headers, answer = request("/_supervisor/v1/enrollment", enrollment(app, plan_id, check_id, template_id, seed))
    token = headers.get("X-Journal-Supervisor-Token", "")
    grant_id = answer.get("grant_id", "") if isinstance(answer, dict) else ""
    if status != 201 or not grant_id or not token:
        if grant_id:
            revoke(grant_id)
        raise SetupFailure("the staged journal refused fixed local-owner enrollment")
    try:
        ensure_smoke_task(app, main, plan_id, seed)
        if seed is None:
            run_bound_check(check_id)
        else:
            run_case_checks(check_id, seed)
        ensure_smoke_task(app, main, plan_id, seed)
        write_token(token)
        if seed and (seed["plan"]["state"] == "started_paused" or seed["plan"]["owner_gate"] != "none"):
            command("plan", "pause", str(plan_id))
        if seed and seed["grant"] == "revoked":
            revoke(grant_id)
    except (OSError, SetupFailure) as error:
        revoke(grant_id)
        raise SetupFailure("the enrollment credential could not be stored safely; the grant was revoked") from error


if __name__ == "__main__":
    try:
        main()
    except SetupFailure as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
