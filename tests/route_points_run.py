"""Outside the default run, since it loads the saved full project: the commit gate runs it before each commit. Every route the server registers, each list with its list parameters, and every hook kind is generated from the router and the hook kinds and answered in-process against the saved full project (tests/full_project.py), counting points, not time: a row loaded, a write and a started kilobyte loaded are a point each, and any answer over its 30 points fails the run, whatever the machine is doing."""

import json
import time
from dataclasses import replace
from pathlib import Path

import pytest

from journal.app import App
from journal.features.faults.support.slow_requests import UNMEASURED_PATHS, SlowRequests
from journal.models.support.request_loads import RequestLoads
from journal.repositories.load_tally import LoadTally
from journal.http.controllers.controller import Controller
from journal.http.router import Router
from journal.http.support.identity import Identity
from journal.http.support.json_out import JsonOut
from journal.http.support.request_reading import RequestReading
from journal.http.support.route import Route
from journal.support.hook_kind import HookKind
from journal.support.response import Response
from tests.full_project import unpacked

MAIN = {"X-Journal-Env": "main"}
JSON, RAW = "application/json", "application/octet-stream"
HOOK_PATH = "/hooks/claude"
SPARE_ENVIRONMENT = 2
# routes that leave the process: they ask the team server, the tunnel program, the supervisor or the network, run a program, or never end; each is named here with why, and one no longer registered fails the run
LEFT_OUT = {
    "POST /hooks/{agent}": "timed once per hook kind instead",
    "GET /journal/entries/stream": "a stream that answers until the viewer leaves",
    "POST /shell/run": "runs a shell command",
    "POST /sign-in": "asks the team server",
    "GET /open": "asks the team server",
    "GET /journal/team/people": "asks the team server",
    "GET /journal/team/devices": "asks the team server",
    "GET /journal/team-chat": "asks the team server",
    "POST /journal/updates": "fetches and installs an update",
    "POST /journal/team/join": "asks the team server",
    "POST /journal/team/check": "asks the team server",
    "POST /journal/team/leave": "asks the team server",
    "POST /journal/team/invite": "asks the team server",
    "POST /journal/team/open": "asks the team server",
    "POST /journal/team/password": "asks the team server",
    "POST /journal/team/people/{id}/password": "asks the team server",
    "POST /journal/team/pool/{id}/stop": "asks the team server",
    "POST /journal/team/devices/{id}/revoke": "asks the team server",
    "POST /journal/team-chat/claim": "asks the team server",
    "POST /journal/team-chat/release": "asks the team server",
    "POST /journal/phones/connect": "asks the team server",
    "POST /journal/environments/{id}/launch": "starts an agent through the supervisor",
    "POST /journal/environments/{id}/stop": "stops an agent through the supervisor",
    "POST /journal/agents/{id}/shell": "types into the agent's terminal through the supervisor",
    "POST /journal/agents/{id}/control": "types into the agent's terminal through the supervisor",
    "POST /journal/workers/{id}/send": "starts the worker's program",
    "POST /journal/workers/{id}/merge": "merges the worker's branch with git",
    "POST /journal/checks/{id}/run": "runs the check's command",
    "POST /journal/secrets/{id}/login": "opens a login window",
    "POST /journal/plugins/{id}/upgrade-preview": "fetches the plugin's source",
    "POST /journal/plugins/{id}/purge": "deletes the plugin's folders",
    "POST /journal/tunnel/check": "runs the tunnel program",
    "POST /journal/tunnel/restart": "runs the tunnel program",
    "POST /journal/tunnel/login": "runs the tunnel program",
    "POST /journal/tunnel/logout": "runs the tunnel program",
    "POST /journal/tunnel/install": "downloads the tunnel program",
    "POST /journal/tunnel/update": "downloads the tunnel program",
    "POST /journal/tunnel/release": "runs the tunnel program",
    "POST /journal/tunnel/readdress": "runs the tunnel program",
    "POST /journal/mcp/install": "installs an MCP server",
    "POST /journal/mcp/check": "starts an MCP server",
    "POST /journal/mcp/{name}/key": "writes an MCP server's configuration",
    "POST /journal/mcp/{name}/remove": "writes an MCP server's configuration",
    "POST /journal/mcp/{name}/sign-in": "signs in to an MCP server",
}
PARAMETERS = {"id": "1", "table": "tasks", "name": "journal", "provider": "claude", "session": "s1", "key": "k", "job": "j"}
# the body a route needs to do its work, the shim's own words and environment for the command routes; every other write is sent an empty one
BODIES = {"/cli": (JSON, json.dumps({"argv": ["task", "list"], "env": "main", "session": None}).encode()), "/cli/run": (RAW, b"JOURNAL_ENV=main\0\0task\0list\0")}
EMPTY = (JSON, b"{}")
LIST_PARAMETERS = ("limit=50", "closed=1", "before=1000", "after=1", "since={since}", "ids=1,2,3")
# writes that take a row away run last, so every other route still finds the rows it names
LAST_ACTS = ("/delete", "/remove", "/purge", "/sign-out", "/disconnect")
GET_TRIES = 3
# a row loaded, a write and a started kilobyte loaded are a point each, whatever the machine is doing
POINTS_BUDGET = 30
# the answers that spent more than the budget when the gate was made, each with what it spent then: none may spend more,
# each is brought down to the budget; a run that finds no file writes it, so deleting it takes the new points once one has come down
BASELINE = Path(__file__).with_name("route_points_baseline.json")
MISSING = not BASELINE.is_file()


@pytest.fixture
def full_project(tmp_path: Path):
    app = unpacked(tmp_path)
    yield app
    app.runtime().stop()


def key(route: Route) -> str:
    return f"{route.method} {route.pattern}"


def is_left_out(route: Route) -> bool:
    return route.outward or key(route) in LEFT_OUT or route.pattern.startswith(UNMEASURED_PATHS) or SlowRequests.is_outward(route.pattern.replace("{id}", "{n}"))


def is_list(route: Route) -> bool:
    return getattr(route.handler, "__name__", "") == "index" and isinstance(getattr(route.handler, "__self__", None), Controller)


def path(route: Route) -> str:
    filled = route.pattern.replace("/environments/{id}", f"/environments/{SPARE_ENVIRONMENT}")
    for name, value in PARAMETERS.items():
        filled = filled.replace(f"{{{name}}}", value)
    return filled


def cases(app: App) -> list[tuple[str, str, tuple[str, bytes]]]:
    """Every route not left out, as the method, a path that names a row of the full project and a harmless body: each read and each list with its list parameters first, then each write, the ones that take a row away last."""
    timed = [route for route in app.container.get(Router).routes if not is_left_out(route)]
    reads = [("GET", path(route), EMPTY) for route in timed if route.method == "GET"]
    lists = [("GET", f"{path(route)}?{parameter.format(since=time.time() - 3600)}", EMPTY) for route in timed if is_list(route) for parameter in LIST_PARAMETERS]
    writes = sorted((route for route in timed if route.method == "POST"), key=lambda route: route.pattern.endswith(LAST_ACTS))
    return [*reads, *lists, *(("POST", path(route), BODIES.get(route.pattern, EMPTY)) for route in writes)]


def hook_bodies() -> dict[HookKind, dict]:
    call = {"tool_name": "Read", "tool_input": {"file_path": "src/parser.py"}}
    return {HookKind.SESSION_START: {}, HookKind.USER_PROMPT: {"prompt": "the footer next"}, HookKind.PRE_TOOL_USE: call, HookKind.POST_TOOL_USE: {**call, "tool_response": ""},
            HookKind.POST_TOOL_USE_FAILURE: {**call, "error": "no such file"}, HookKind.PRE_COMPACT: {}, HookKind.STOP: {}, HookKind.STOP_FAILURE: {"error": "rate_limit", "last_assistant_message": "limit reached"},
            HookKind.SUBAGENT_START: {"agent_id": "a1", "agent_type": "Explore"}, HookKind.SUBAGENT_STOP: {"agent_id": "a1", "agent_type": "Explore", "last_assistant_message": "found it"},
            HookKind.MESSAGE_DISPLAY: {"message": "The parser is written."}, HookKind.SESSION_END: {"reason": "other"}}


def answer_loads(app: App, method: str, target: str, body: tuple[str, bytes]) -> RequestLoads:
    """The rows, bytes and writes the journal's own router spends answering, the answer written as the server writes it; the deferred listeners then run uncounted, so each request starts with the worker thread idle."""
    kind, raw = body
    request = RequestReading.read(RequestReading.head(method, target, {**MAIN, "Content-Type": kind}), raw if method == "POST" else b"", app.container.get(Identity))
    LoadTally.begin()
    answer = app.container.get(Router).route(request)
    if isinstance(answer, Response):
        JsonOut.encoded(answer.body)
    loads = LoadTally.ended()
    app.runtime().deferred.drain()
    return loads


def least_loads(app: App, method: str, target: str, body: tuple[str, bytes]) -> RequestLoads:
    """A read's least of its tries after the first, which loads a cold cache; a write once, since a second would change what it finds."""
    if method == "POST":
        return answer_loads(app, method, target, body)
    answer_loads(app, method, target, body)
    return min((answer_loads(app, method, target, body) for _ in range(GET_TRIES)), key=RequestLoads.points)


def allowed(name: str) -> int:
    return max(POINTS_BUDGET, json.loads(BASELINE.read_text()).get(name, 0)) if BASELINE.is_file() else POINTS_BUDGET


def spent(name: str, loads: RequestLoads) -> str:
    return f"{name} spent {loads.points()} points, over its {allowed(name)}: {loads.line()}"


def recorded(spending: dict[str, RequestLoads]) -> dict[str, RequestLoads]:
    if MISSING:
        kept = json.loads(BASELINE.read_text()) if BASELINE.is_file() else {}
        BASELINE.write_text(json.dumps(dict(sorted({**kept, **{name: loads.points() for name, loads in spending.items() if loads.points() > POINTS_BUDGET}}.items())), indent=1) + "\n")
    return spending


def over(spending: dict[str, RequestLoads]) -> list[str]:
    return [spent(name, loads) for name, loads in spending.items() if loads.points() > allowed(name)]


def measured_loads(app: App, measured: list[tuple[str, str, tuple[str, bytes]]]) -> dict[str, RequestLoads]:
    return {f"{method} {target}": least_loads(app, method, target, body) for method, target, body in measured}


def over_budget(app: App, measured: list[tuple[str, str, tuple[str, bytes]]]) -> list[str]:
    return over(measured_loads(app, measured))


def test_every_route_is_timed_or_left_out_by_name_and_every_hook_kind_has_a_body(full_project: App):
    routes = full_project.container.get(Router).routes
    assert sorted(set(LEFT_OUT) - {key(route) for route in routes}) == [], "a route left out by name is one the server registers"
    timed = {(method, target.split("?")[0]) for method, target, _ in cases(full_project)}
    assert [key(route) for route in routes if not is_left_out(route) and (route.method, path(route)) not in timed] == [], "every route not left out is timed"
    assert set(hook_bodies()) == set(HookKind), "every hook kind is timed"
    assert len(timed) > 200 and any("?closed=1" in target for _, target, _ in cases(full_project)), "the lists are timed with their list parameters"


def test_every_route_answers_within_its_budget_on_a_full_project(full_project: App):
    routes = over(recorded(measured_loads(full_project, cases(full_project))))
    assert not routes, "\n".join(routes)


def test_every_hook_kind_answers_within_its_budget_on_a_full_project(full_project: App):
    bodies = hook_bodies()
    posted = lambda kind, body, try_name: (JSON, json.dumps({"hook_event_name": kind.value, "session_id": "s1", "tool_use_id": f"{try_name}-{kind.value}", **body}).encode())
    for kind, body in bodies.items():
        answer_loads(full_project, "POST", HOOK_PATH, posted(kind, body, "warm"))
    loads = {kind: answer_loads(full_project, "POST", HOOK_PATH, posted(kind, body, "counted")) for kind, body in bodies.items()}
    hooks = over(recorded({f"hook {kind.value}": load for kind, load in loads.items()}))
    assert not hooks, "\n".join(hooks)


def test_a_route_made_heavy_on_purpose_is_reported_over_its_budget(full_project: App):
    router = full_project.container.get(Router)
    place, route = next((place, route) for place, route in enumerate(router.routes) if key(route) == "GET /journal/tasks")

    def heavy(request):
        for _ in range(POINTS_BUDGET * 2):
            LoadTally.counted("tasks", ("a row",))
        return route.handler(request)

    router.routes[place] = replace(route, handler=heavy)
    reported = over_budget(full_project, [("GET", "/journal/tasks", EMPTY)])
    assert len(reported) == 1 and reported[0].startswith("GET /journal/tasks spent") and "tasks" in reported[0], reported
