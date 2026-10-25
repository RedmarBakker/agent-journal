#!/usr/bin/env python3
"""End to end on a real team server: installs a fresh team server and hosted journal from this branch on the test server, starts two scratch journals here joined to it, and runs each check, printing one line per check.

    E2E_SERVER=<address> python3 scripts/e2e_team.py deploy    # build and start the team server on the test server (wipes the one it had)
    python3 scripts/e2e_team.py journals  # two scratch journals on ports 8531 and 8532, joined to it
    python3 scripts/e2e_team.py checks    # every check, one line each
    python3 scripts/e2e_team.py stop      # the scratch journals; the test server is left running
    python3 scripts/e2e_team.py wipe      # the scratch journals and every team server, its data and the package on the test server
"""
import http.client
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERVER = os.environ.get("E2E_SERVER") or sys.exit("set E2E_SERVER to the test server's address, a machine you may wipe, reachable as root by ssh")
REMOTE = f"root@{SERVER}"
BRANCH = Path(__file__).resolve().parents[1]
WORK = Path("/tmp/e2e-team")
FOLDERS = {"a": "acme", "b": "acme-bob", "c": "pre", "d": "pre-dan"}
PORTS = {"a": 8531, "b": 8532, "c": 8533, "d": 8534}
PASSWORD = "e2e-Password-4711!"
PEOPLE = {"a": ("ada@e2e.test", "Ada"), "b": ("bob@e2e.test", "Bob"), "c": ("cara@e2e.test", "Cara"), "d": ("dan@e2e.test", "Dan")}
PACKAGE = ("src/sync_server", "src/journal", "src/supervisor", "src/sync_service", "src/journal.py", "src/journal.sh", "src/web/dist", "install.sh", "docker/team-server")
PYTHON = shutil.which("python3.14") or sys.executable


def run(command: list[str], **options) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True, timeout=options.pop("timeout", 120), **options)


def remote(command: str, timeout: int = 600) -> str:
    done = run(["ssh", "-o", "BatchMode=yes", REMOTE, command], timeout=timeout)
    if done.returncode:
        raise SystemExit(f"on the test server: {command}\n{done.stdout}{done.stderr}")
    return done.stdout.strip()


def deploy() -> None:
    remote("docker rm -f team >/dev/null 2>&1; docker volume rm team-data >/dev/null 2>&1; rm -rf /opt/agent-journal && mkdir -p /opt/agent-journal")
    packed = subprocess.Popen(["tar", "-C", str(BRANCH), "--exclude=__pycache__", "-cf", "-", *PACKAGE], stdout=subprocess.PIPE)
    shipped = subprocess.run(["ssh", "-o", "BatchMode=yes", REMOTE, "tar -C /opt/agent-journal -xf -"], stdin=packed.stdout, capture_output=True, timeout=600)
    if shipped.returncode:
        raise SystemExit(shipped.stderr.decode())
    commit = run(["git", "-C", str(BRANCH), "rev-parse", "HEAD"]).stdout.strip()
    remote(f"cd /opt/agent-journal && docker build -q -f docker/team-server/Dockerfile --build-arg COMMIT={commit} -t agent-journal-team . ", timeout=1800)
    started()
    print(f"team server started at http://{SERVER}")


# a fresh team server from the image built last, its data wiped
def started() -> None:
    remote("docker rm -f team >/dev/null 2>&1; docker volume rm team-data >/dev/null 2>&1; docker run -d --name team --restart unless-stopped -p 80:80 -e TEAM_PLAIN_HTTP=1 -v team-data:/data agent-journal-team")


def environment(name: str) -> dict:
    clean = {key: value for key, value in os.environ.items() if not key.startswith(("JOURNAL", "AGENT_JOURNAL", "CLAUDE", "CODEX")) and key != "AI_AGENT"}
    return {**clean, "JOURNAL_ROOT": str(WORK / FOLDERS[name]), "JOURNAL_PORT": str(PORTS[name]), "PYTHONPATH": str(WORK / FOLDERS[name] / ".journal/src")}


def journal(name: str, *words: str) -> str:
    done = run(["sh", str(WORK / FOLDERS[name] / ".journal/src/journal.sh"), *words], env=environment(name), cwd=WORK / FOLDERS[name], timeout=120)
    return (done.stdout + done.stderr).strip()


def posted(name: str, path: str, body: dict, environment_name: str) -> dict:
    return sent(name, f"/journal{path}", body, environment_name)


def sent(name: str, path: str, body: dict, environment_name: str) -> dict:
    request = urllib.request.Request(f"http://127.0.0.1:{PORTS[name]}{path}", data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": environment_name})
    with urllib.request.urlopen(request, timeout=20) as reply:
        return json.loads(reply.read())


def api(name: str, path: str, environment_name: str = "main") -> dict:
    request = urllib.request.Request(f"http://127.0.0.1:{PORTS[name]}/journal{path}", headers={"X-Journal-Env": environment_name})
    with urllib.request.urlopen(request, timeout=20) as reply:
        return json.loads(reply.read())


def start_scratch(name: str, clone_of: str = "") -> None:
    root = WORK / FOLDERS[name]
    shutil.rmtree(root, ignore_errors=True)
    if clone_of:
        run(["git", "clone", "-q", str(WORK / FOLDERS[clone_of]), str(root)])
        (root / ".journal").mkdir(exist_ok=True)
    else:
        (root / ".journal").mkdir(parents=True)
        run(["git", "init", "-q", str(root)])
        (root / "README.md").write_text(f"scratch journal {name}\n")
        run(["git", "-C", str(root), "add", "-A"])
        run(["git", "-C", str(root), "-c", "user.name=e2e", "-c", "user.email=e2e@e2e.test", "commit", "-qm", "start"])
    for part in PACKAGE[:6]:
        target = root / ".journal" / part
        target.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if (BRANCH / part).is_dir() else shutil.copy)(BRANCH / part, target, **({"ignore": shutil.ignore_patterns("__pycache__")} if (BRANCH / part).is_dir() else {}))
    (root / ".journal" / "python").write_text(PYTHON)
    run([PYTHON, str(root / ".journal/src/journal.py"), "environment", "create", "main"], env=environment(name), cwd=root)
    for process, command in (("journal", [PYTHON, str(root / ".journal/src/journal.py"), "serve"]), ("sync", [PYTHON, "-m", "sync_service", str(root)])):
        log = open(root / f"{process}.log", "w")
        subprocess.Popen(command, cwd=root, env=environment(name), stdout=log, stderr=log, start_new_session=True)
        if process == "journal":
            wait(lambda: (root / ".journal/port").is_file() and api(name, "/environments"), f"journal {name} to listen")


def wait(ready, what: str, seconds: int = 60):
    end = time.time() + seconds
    while time.time() < end:
        try:
            if value := ready():
                return value
        except Exception:
            pass
        time.sleep(1)
    raise SystemExit(f"timed out waiting for {what}")


def team_answers() -> bool:
    request = urllib.request.Request(f"http://{SERVER}/team", headers={"X-Journal-Protocol": "99"})
    with urllib.request.urlopen(request, timeout=10) as reply:
        return reply.status == 200


def journals() -> None:
    stop()
    wait(team_answers, "the team server to answer", 180)
    start_scratch("a")
    email, person = PEOPLE["a"]
    print(journal("a", "team", "join", f"http://{SERVER}", "--email", email, "--name", person, f"--password={PASSWORD}"))
    invitation = journal("a", "team", "invite", PEOPLE["b"][0])
    url = next(word for word in invitation.split() if word.startswith("http"))
    start_scratch("b", clone_of="a")
    email, person = PEOPLE["b"]
    print(journal("b", "team", "join", url, "--email", email, "--name", person, f"--password={PASSWORD}"))


def stop() -> None:
    for name, port in PORTS.items():
        run(["sh", "-c", f"kill $(lsof -t -nP -iTCP:{port} -sTCP:LISTEN) 2>/dev/null; pkill -f 'sync_service {WORK / FOLDERS[name]}' 2>/dev/null; true"])


def server_python(program: str, container: str = "team") -> str:
    return subprocess.run(["ssh", "-o", "BatchMode=yes", REMOTE, f"docker exec -i {container} python -"], input=program, capture_output=True, text=True, timeout=60).stdout


def server_rows(container: str = "team") -> list[dict]:
    program = "import json, sqlite3\nc = sqlite3.connect('/data/team/team.db')\nprint(json.dumps([[t, n, json.loads(f)] for t, n, f in c.execute('select row_table, row, fields from rows where is_deleted = 0')]))\n"
    return [{"table": t, "id": n, **f} for t, n, f in json.loads(server_python(program, container))]


def waiting_for(found, seconds: int = 90):
    end = time.time() + seconds
    while time.time() < end:
        if value := found():
            return value
        time.sleep(3)
    return None


STAMP = str(int(time.time()))


def is_shared(row: dict) -> bool:
    return row.get("kind") == "local" and bool(row.get("team_key"))


def hubs(name: str) -> list[dict]:
    return [row for row in api(name, "/environments")["rows"] if row["kind"] == "hub"]


def titles(name: str, environment_name: str) -> list[str]:
    return [row["title"] for row in api(name, "/tasks?limit=49", environment_name)["rows"]]


def check_team_key_and_hub() -> str:
    one, other = hubs("a"), hubs("b")
    if len(one) != 1 or len(other) != 1:
        return f"FAIL: hubs a={len(one)} b={len(other)}"
    same = one[0]["team_key"] and one[0]["team_key"] == other[0]["team_key"]
    return f"{'OK' if same else 'FAIL'}: both journals hold the hub '{one[0]['name']}' of team key {one[0]['team_key'][:8]}, kind {one[0]['kind']}"


def check_hub_write() -> str:
    hub = hubs("a")[0]
    journal("a", "task", "create", f"hub task {STAMP}", "--brief", "filed in the hub", "--team", hub["team_name"])
    on_a = f"hub task {STAMP}" in titles("a", hub["name"])
    reached = waiting_for(lambda: f"hub task {STAMP}" in titles("b", hub["name"]))
    on_server = any(row["table"] == "tasks" and row.get("title") == f"hub task {STAMP}" for row in server_rows())
    return f"{'OK' if on_a and reached and on_server else 'FAIL'}: filed with --team in the hub: on a's hub {on_a}, reached b's hub {bool(reached)}, held by the server {on_server}"


def check_personal_task() -> str:
    journal("a", "environment", "unshare", "main")
    journal("a", "task", "create", f"personal task {STAMP}", "--brief", "stays here")
    time.sleep(40)
    present = {row["name"] for row in api("b", "/environments")["rows"]}
    on_b = [environment for environment in ("ada-main", "main", "team", hubs("b")[0]["name"]) if environment in present and f"personal task {STAMP}" in titles("b", environment)]
    on_server = any(row.get("title") == f"personal task {STAMP}" for row in server_rows())
    return f"{'OK' if not on_b and not on_server else 'FAIL'}: a task in a's own environment: seen on b in {on_b or 'no environment'}, held by the server {on_server}"


def check_share_and_unshare() -> str:
    journal("a", "environment", "share", "main")
    journal("a", "message", "send", f"shared chat {STAMP}")
    shared = waiting_for(lambda: next((row for row in api("b", "/environments")["rows"] if row["name"] == "ada-main" and is_shared(row)), None))
    seen = bool(shared) and waiting_for(lambda: any(f"shared chat {STAMP}" in str(row.get("text")) for row in api("b", "/messages", "ada-main")["rows"]))
    journal("a", "environment", "unshare", "main")
    gone = waiting_for(lambda: not is_shared(next((row for row in api("b", "/environments")["rows"] if row["name"] == "ada-main"), {})))
    return f"{'OK' if shared and seen and gone else 'FAIL'}: a shared main: b lists it shared {bool(shared)}, reads its chat {bool(seen)}; after unshare b lists it shared {not gone}"


def check_server_holds_only_team_rows() -> str:
    environments = [row for row in server_rows() if row["table"] == "environments"]
    personal = [row.get("team_name") for row in environments if row.get("kind") not in ("hub", "session") and not is_shared(row)]
    return f"{'OK' if not personal else 'FAIL'}: environments on the server: {[row.get('team_name') for row in environments]}; not the team's: {personal}"


def hosted(method: str, path: str, body: dict | None = None, cookie: str = "") -> http.client.HTTPResponse:
    connection = http.client.HTTPConnection(SERVER, 80, timeout=30)
    headers = {"Content-Type": "application/json", "X-Journal-Env": hubs("a")[0]["name"], **({"Cookie": cookie} if cookie else {})}
    connection.request(method, path, json.dumps(body).encode() if body is not None else None, headers)
    return connection.getresponse()


# a opens the team's journal as the viewer's Open does: its own journal asks the team server for a one-time link, and the link opens a session
def signed_in() -> str:
    request = urllib.request.Request(f"http://127.0.0.1:{PORTS['a']}/journal/team/open", data=b"{}", method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main"})
    with urllib.request.urlopen(request, timeout=20) as reply:
        link = urllib.parse.urlsplit(json.loads(reply.read())["url"])
    opened = hosted("GET", f"{link.path}?{link.query}")
    cookie = (opened.getheader("Set-Cookie") or "").split(";")[0]
    return cookie if opened.status == 303 and cookie else ""


def check_hosted_journal() -> str:
    cookie = waiting_for(signed_in, 180)
    if not cookie:
        return "FAIL: the hosted journal opened no session from a's one-time link within three minutes"
    reply = hosted("GET", "/journal/environments", cookie=cookie)
    rows = json.loads(reply.read()).get("rows", []) if reply.status == 200 else []
    hub = next((row for row in rows if row.get("kind") == "hub"), None)
    found = bool(hub) and hub.get("team_key") == hubs("a")[0]["team_key"]
    home = hosted("GET", "/journal/tasks?limit=49", cookie=cookie)
    tasks = [row.get("title") for row in json.loads(home.read()).get("rows", [])] if home.status == 200 else []
    opened = f"hub task {STAMP}" in tasks
    return f"{'OK' if found and opened else 'FAIL'}: a opened the hosted journal at http://{SERVER} from its own journal: it shows the hub {hub.get('name') if hub else 'none'} of the team (environments {reply.status}: {[row.get('name') for row in rows]}) and its home holds the hub task filed here {opened} (tasks {home.status})"


def stored(name: str, sql: str, params: tuple = ()) -> list[dict]:
    connection = sqlite3.connect(f"file:{WORK / FOLDERS[name] / '.journal/journal.db'}?mode=ro", uri=True, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in connection.execute(sql, params)]
    finally:
        connection.close()


def page(name: str, title: str, words: str) -> str:
    written = WORK / f"{name}-{title.replace(' ', '-')}-{abs(hash(words))}.md"
    written.write_text(f"# {title}\n\n{words}\n")
    return str(written)


def body(name: str, number: int) -> str:
    rows = stored(name, "SELECT body FROM docs WHERE id = ?", (number,))
    return rows[0]["body"] if rows else ""


def check_hosted_hub_home() -> str:
    cookie = waiting_for(signed_in, 180)
    if not cookie:
        return "FAIL: the hosted journal opened no session from a's one-time link"
    reply = hosted("GET", "/journal/environments", cookie=cookie)
    rows = json.loads(reply.read()).get("rows", []) if reply.status == 200 else []
    unshared = [row.get("name") for row in rows if row.get("kind") == "local" and not row.get("team_key")]
    hub = next((row.get("name") for row in rows if row.get("kind") == "hub"), "")
    return f"{'OK' if hub and not unshared else 'FAIL'}: the hosted journal lists the hub {hub or 'none'} and these environments that are not shared: {unshared or 'none'} (all: {[row.get('name') for row in rows]})"


def check_hub_documents() -> str:
    seen = []
    for mode in ("free", "read_only"):
        title = f"{mode} page {STAMP}"
        journal("a", "doc", "create", title, "--file", page("a", title, "the first words"))
        number = stored("a", "SELECT id FROM docs WHERE title = ? ORDER BY id DESC", (title,))[0]["id"]
        journal("a", "doc", "share", str(number), "--mode", mode)
        reached = bool(waiting_for(lambda: "the first words" in body("b", number)))
        by_b = journal("b", "doc", "update", str(number), "--file", page("b", title, "Bob's words"))
        refused = "read-only on the hub" in by_b
        bob_on_a = bool(waiting_for(lambda: "Bob's words" in body("a", number), 45)) if not refused else "Bob's words" in body("a", number)
        journal("a", "doc", "update", str(number), "--file", page("a", title, "Ada's later words"))
        ada_on_b = bool(waiting_for(lambda: "Ada's later words" in body("b", number)))
        expected = (reached, bob_on_a, ada_on_b, refused) == ((True, True, True, False) if mode == "free" else (True, False, True, True))
        seen.append((expected, f"{mode} doc {number}: reached b {reached}, b's edit {'refused' if refused else 'taken'} and on a {bob_on_a}, a's edit on b {ada_on_b}"))
    return f"{'OK' if all(ok for ok, _ in seen) else 'FAIL'}: " + "; ".join(text for _, text in seen)


def check_drive_to_done() -> str:
    hub = hubs("a")[0]
    title = f"driven task {STAMP}"
    journal("a", "task", "create", title, "--brief", "driven from a to done", "--team", hub["team_name"])
    number = stored("a", "SELECT id FROM tasks WHERE title = ? ORDER BY id DESC", (title,))[0]["id"]
    on_b = lambda: next(iter(stored("b", "SELECT state, driver FROM tasks WHERE id = ?", (number,))), {})
    reached = bool(waiting_for(on_b))
    drive = journal("a", "task", "drive", str(number))
    driven_on_b = bool(waiting_for(lambda: on_b().get("driver") == PEOPLE["a"][1]))
    started = journal("a", "task", "start", str(number))
    completed = journal("a", "task", "complete", str(number), "--how", "finished end to end")
    done_on_b = bool(waiting_for(lambda: on_b().get("state") == "done"))
    cookie = waiting_for(signed_in, 60)
    reply = hosted("GET", "/journal/tasks?limit=49", cookie=cookie) if cookie else None
    hosted_rows = json.loads(reply.read()).get("rows", []) if reply and reply.status == 200 else []
    on_hosted = next((row for row in hosted_rows if row.get("title") == title), {})
    hosted_seen = on_hosted.get("state") == "done" and on_hosted.get("driver") == PEOPLE["a"][1]
    ok = reached and driven_on_b and done_on_b and hosted_seen
    return f"{'OK' if ok else 'FAIL'}: hub task {number} driven from a's main by journal commands, as its agent runs them (drive: {drive.splitlines()[0] if drive else 'nothing'}; start: {started.splitlines()[0] if started else 'nothing'}; complete: {completed.splitlines()[0] if completed else 'nothing'}): reached b {reached}, b shows it driven by {PEOPLE['a'][1]} {driven_on_b}, b shows it done {done_on_b}, the hosted journal shows it {on_hosted.get('state', 'absent')} driven by {on_hosted.get('driver') or 'nobody'}"


SECOND_PORT = 8090


def task_row(name: str, title: str) -> dict:
    return next(iter(stored(name, "SELECT * FROM tasks WHERE title = ? ORDER BY id DESC", (title,))), {})


def check_requests() -> str:
    for_bob, for_team = f"a request for Bob {STAMP}", f"a request for the team {STAMP}"
    journal("a", "task", "create", for_bob, "--brief", "Bob may turn it down", "--to", PEOPLE["b"][1])
    journal("a", "task", "create", for_team, "--brief", "anyone may take it", "--to-team")
    reached = waiting_for(lambda: task_row("b", for_bob) and task_row("b", for_team))
    declined = journal("b", "task", "decline", str(task_row("b", for_bob).get("id", 0)), "--why", f"not mine {STAMP}")
    claimed = journal("b", "task", "drive", str(task_row("b", for_team).get("id", 0)))
    turned_down = waiting_for(lambda: task_row("a", for_bob).get("state") == "cancelled" and STAMP in str(task_row("a", for_bob)))
    taken = waiting_for(lambda: task_row("a", for_team).get("driver") == PEOPLE["b"][1])
    ok = bool(reached and turned_down and taken)
    return f"{'OK' if ok else 'FAIL'}: a filed a request for Bob and one for the team, which reached b {bool(reached)}; b declined the first ({declined.splitlines()[0] if declined else 'nothing'}) and a sees it cancelled with b's reason {bool(turned_down)}; b claimed the second by driving it ({claimed.splitlines()[0] if claimed else 'nothing'}) and a sees it driven by Bob {bool(taken)}"


def lease_holders() -> dict:
    program = "import json, sqlite3\nc = sqlite3.connect('/data/team/team.db')\nprint(json.dumps({n: p for n, p in c.execute('select leases.name, accounts.name from leases join accounts on accounts.id = leases.account_id')}))\n"
    return json.loads(server_python(program) or "{}")


def check_sessions() -> str:
    review, notes, planner = f"review-{STAMP}", f"notes-{STAMP}", f"planner-{STAMP}"
    journal("a", "session", "start", review)
    journal("b", "session", "start", notes)
    both = waiting_for(lambda: all(stored(name, "SELECT id FROM environments WHERE kind = 'session' AND name IN (?, ?)", (review, notes)) and len(stored(name, "SELECT id FROM environments WHERE kind = 'session' AND name IN (?, ?)", (review, notes))) == 2 for name in ("a", "b")))
    holders = lease_holders()
    held_apart = holders.get(f"session:{review}") == PEOPLE["a"][1] and holders.get(f"session:{notes}") == PEOPLE["b"][1]
    sent("a", "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": f"e2e-{STAMP}"}, review)
    posted("b", "/messages", {"text": f"for the review {STAMP}", "idempotency": f"e2e-{STAMP}"}, review)
    heard = waiting_for(lambda: any("from Bob" in str(row["data"]) for row in stored("a", "SELECT data FROM entries WHERE kind = 'nudge' AND data LIKE ?", (f"%e2e-{STAMP}%",))), 120)
    made = bool(stored("a", "SELECT id FROM messages WHERE text = ?", (f"for the review {STAMP}",)))
    plan_title = f"session plan {STAMP}"
    journal("a", "plan", "create", plan_title, "--brief", "driven by a session", "--team", hubs("a")[0]["team_name"])
    plan = next(iter(stored("a", "SELECT id FROM plans WHERE title = ?", (plan_title,))), {})
    reached = waiting_for(lambda: stored("b", "SELECT id FROM plans WHERE id = ?", (plan.get("id", 0),)))
    driving = journal("b", "session", "start", planner, "--plan", str(plan.get("id", 0)))
    driven = waiting_for(lambda: next(iter(stored("a", "SELECT driver FROM plans WHERE id = ?", (plan.get("id", 0),))), {}).get("driver") == PEOPLE["b"][1])
    ok = bool(both) and held_apart and made and bool(heard) and bool(reached) and bool(driven)
    return f"{'OK' if ok else 'FAIL'}: sessions {review} and {notes} on both journals {bool(both)}, held by Ada and by Bob on the server {held_apart} ({holders}); Bob's message in {review} made on a, its holder, {made}, and its agent told {bool(heard)}; b's session {planner} drives hub plan {plan.get('id')} ({driving.splitlines()[0] if driving else 'nothing'}), a sees it driven by Bob {bool(driven)}"


def check_two_teams() -> str:
    remote(f"docker rm -f team2 >/dev/null 2>&1; docker volume rm team2-data >/dev/null 2>&1; docker run -d --name team2 --restart unless-stopped -p {SECOND_PORT}:80 -e TEAM_PLAIN_HTTP=1 -v team2-data:/data agent-journal-team")
    second = f"http://{SERVER}:{SECOND_PORT}"
    wait(lambda: urllib.request.urlopen(urllib.request.Request(f"{second}/team", headers={"X-Journal-Protocol": "99"}), timeout=10).status == 200, "the second team server to answer", 180)
    email, person = PEOPLE["a"]
    server_python(f"from pathlib import Path\nfrom sync_server.accounts import Accounts\nfrom sync_server.account import ADMIN\nfrom sync_server.db.account_rows import AccountRows\nfrom sync_server.db.store import Store\naccounts = Accounts(AccountRows(Store(Path('/data/team/team.db'))))\naccounts.create('lead@e2e.test', 'Lead', {PASSWORD!r}, ADMIN, 1.0)\naccounts.create({email!r}, {person!r}, {PASSWORD!r}, ADMIN, 1.0)\n", "team2")
    joined = journal("a", "team", "join", second, "--email", email, "--name", person, f"--password={PASSWORD}")
    names = {row["team_key"]: row["team_name"] for row in hubs("a")}
    summaries = [json.loads(urllib.request.urlopen(urllib.request.Request(f"{address}/team", headers={"X-Journal-Protocol": "99"}), timeout=10).read()) for address in (f"http://{SERVER}", second)]
    first_hub, second_hub = names.get(summaries[0]["key"], ""), names.get(summaries[1]["key"], "")
    titles = (f"first team's task {STAMP}", f"second team's task {STAMP}")
    for title, hub in zip(titles, (first_hub, second_hub)):
        journal("a", "task", "create", title, "--brief", "filed in its team's hub", "--team", hub)
    rows = lambda container: {row.get("title"): row for row in server_rows(container) if row["table"] == "tasks"}
    arrived = waiting_for(lambda: titles[0] in rows("team") and titles[1] in rows("team2"), 120)
    first_rows, second_rows = rows("team"), rows("team2")
    apart = titles[1] not in first_rows and titles[0] not in second_rows
    stamps = (first_rows.get(titles[0], {}).get("creator"), second_rows.get(titles[1], {}).get("creator"))
    numbers = [task_row("a", title).get("id", 0) >> 32 for title in titles]
    spaces = numbers == [summaries[0]["number"], summaries[1]["number"]] and numbers[0] != numbers[1]
    ok = bool(arrived) and apart and stamps == ("user:1", "user:2") and spaces
    return f"{'OK' if ok else 'FAIL'}: a joined a second team server at {second} ({joined.splitlines()[0] if joined else 'nothing'}); hubs {first_hub} and {second_hub}; each task reached its own server {bool(arrived)} and no other {apart}; stamped {stamps}, a's account in each team; numbered in each team's space T = {numbers} against the servers' {[summary['number'] for summary in summaries]} {spaces}"


def wipe() -> None:
    stop()
    remote("docker rm -f team team2 >/dev/null 2>&1; docker volume rm team-data team2-data >/dev/null 2>&1; rm -rf /opt/agent-journal; true")
    print(f"the test server {SERVER} holds no team server, no team data and no package of this run")


def joined_pair(first: str, second: str) -> None:
    for name in (first, second):
        run(["sh", "-c", f"kill $(lsof -t -nP -iTCP:{PORTS[name]} -sTCP:LISTEN) 2>/dev/null; pkill -f 'sync_service {WORK / FOLDERS[name]}' 2>/dev/null; true"])
    start_scratch(first)
    email, person = PEOPLE[first]
    journal(first, "team", "join", f"http://{SERVER}", "--email", email, "--name", person, f"--password={PASSWORD}")
    url = next(word for word in journal(first, "team", "invite", PEOPLE[second][0]).split() if word.startswith("http"))
    start_scratch(second, clone_of=first)
    email, person = PEOPLE[second]
    journal(second, "team", "join", url, "--email", email, "--name", person, f"--password={PASSWORD}")


def server_environments() -> list[dict]:
    return [row for row in server_rows() if row["table"] == "environments"]


# a team made the old way on a fresh team server, every row synced, then moved to the hub by journal team migrate; it leaves the team server holding this team, so it runs last
def check_pre_hub_migration() -> str:
    started()
    wait(team_answers, "the fresh team server to answer", 180)
    server_python("import sqlite3\nc = sqlite3.connect('/data/team/team.db')\nc.execute(\"DELETE FROM team_details WHERE name = 'hub'\")\nc.commit()\n")
    joined_pair("c", "d")
    journal("c", "task", "create", f"Cara's own task {STAMP}", "--brief", "stays hers")
    journal("d", "task", "create", f"Dan's own task {STAMP}", "--brief", "stays his")
    journal("c", "environment", "create", "lab")
    journal("c", "environment", "share", "lab")
    posted("c", "/messages", {"text": f"lab chat {STAMP}"}, "lab")
    synced_old_way = waiting_for(lambda: any(row.get("team_name") == "cara-main" for row in server_environments()) and stored("d", "SELECT id FROM tasks WHERE title = ?", (f"Cara's own task {STAMP}",)))
    migrated = journal("c", "team", "migrate")
    hub_on = lambda name: bool(stored(name, "SELECT id FROM environments WHERE kind = 'hub'"))
    task_on = lambda name, title: bool(stored(name, "SELECT id FROM tasks WHERE title = ?", (title,)))
    chat_on = lambda name: bool(stored(name, "SELECT id FROM messages WHERE text = ?", (f"lab chat {STAMP}",)))
    settled = waiting_for(lambda: hub_on("c") and hub_on("d") and not [row for row in server_environments() if row.get("kind") not in ("hub", "session") and not (row.get("kind") == "local" and row.get("team_key"))], 150)
    kept = {"c's own task": task_on("c", f"Cara's own task {STAMP}"), "d's own task": task_on("d", f"Dan's own task {STAMP}"), "c's lab chat": chat_on("c"), "the shared lab chat on d": chat_on("d"), "the hub on c": hub_on("c"), "the hub on d": hub_on("d")}
    held = [row.get("team_name") for row in server_environments()]
    gone = not task_on("d", f"Cara's own task {STAMP}")
    ok = bool(synced_old_way) and bool(settled) and all(kept.values()) and gone
    return f"{'OK' if ok else 'FAIL'}: a team made the old way synced c's own environment and task to the server and to d {bool(synced_old_way)}; journal team migrate on c said: {migrated.splitlines()[0] if migrated else 'nothing'}; kept: {kept}; c's own task gone from d {gone}; environments on the server: {held}"


CHECKS = (("team key and hub", check_team_key_and_hub), ("hub write reaches the other journal and the server", check_hub_write), ("a personal task never reaches the server", check_personal_task),
          ("a shared chat reaches the other journal, and unsharing takes it back", check_share_and_unshare), ("the server holds only team rows", check_server_holds_only_team_rows), ("the hosted journal starts and a sign-in finds the hub", check_hosted_journal), ("the hosted journal's hub home lists no environment that is not shared", check_hosted_hub_home), ("a hub document in each edit mode is edited from both journals, a read-only one refused to the other", check_hub_documents), ("a hub task driven from a to done shows driven and done on b and the hosted journal", check_drive_to_done), ("a request is filed, declined and claimed", check_requests), ("sessions are held one machine each, a message reaches its holder's agent, and a session drives a hub plan", check_sessions), ("a journal joined to two teams writes with each team's account, its numbers apart", check_two_teams), ("a pre-hub team journal migrates", check_pre_hub_migration))


def checks() -> None:
    for title, check in CHECKS:
        try:
            print(f"{title}: {check()}", flush=True)
        except Exception as fault:
            print(f"{title}: FAIL: {type(fault).__name__}: {fault}", flush=True)


COMMANDS = {"deploy": deploy, "journals": journals, "checks": checks, "stop": stop, "wipe": wipe}

if __name__ == "__main__":
    verb = sys.argv[1] if len(sys.argv) == 2 else ""
    if verb in COMMANDS:
        COMMANDS[verb]()
    else:
        raise SystemExit(__doc__)
