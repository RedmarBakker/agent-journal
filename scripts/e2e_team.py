#!/usr/bin/env python3
"""End to end on a real team server: installs a fresh team server and hosted journal from this branch on the test server, starts two scratch journals here joined to it, and runs each check, printing one line per check.

    E2E_SERVER=<address> python3 scripts/e2e_team.py deploy    # build and start the team server on the test server (wipes the one it had)
    python3 scripts/e2e_team.py journals  # two scratch journals on ports 8531 and 8532, joined to it
    python3 scripts/e2e_team.py checks    # every check, one line each
    python3 scripts/e2e_team.py stop      # the scratch journals; the test server is left running
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

SERVER = os.environ.get("E2E_SERVER") or sys.exit("set E2E_SERVER to the test server's address, a machine you may wipe, reachable as root by ssh")
REMOTE = f"root@{SERVER}"
BRANCH = Path(__file__).resolve().parents[1]
WORK = Path("/tmp/e2e-team")
FOLDERS = {"a": "acme", "b": "acme-bob"}
PORTS = {"a": 8531, "b": 8532}
PASSWORD = "e2e-Password-4711!"
PEOPLE = {"a": ("ada@e2e.test", "Ada"), "b": ("bob@e2e.test", "Bob")}
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
    remote("cd /opt/agent-journal && docker build -q -f docker/team-server/Dockerfile -t agent-journal-team . ", timeout=1800)
    remote("docker run -d --name team --restart unless-stopped -p 80:80 -e TEAM_PLAIN_HTTP=1 -v team-data:/data agent-journal-team")
    print(f"team server started at http://{SERVER}")


def environment(name: str) -> dict:
    clean = {key: value for key, value in os.environ.items() if not key.startswith(("JOURNAL", "AGENT_JOURNAL", "CLAUDE", "CODEX")) and key != "AI_AGENT"}
    return {**clean, "JOURNAL_ROOT": str(WORK / FOLDERS[name]), "JOURNAL_PORT": str(PORTS[name]), "PYTHONPATH": str(WORK / FOLDERS[name] / ".journal/src")}


def journal(name: str, *words: str) -> str:
    done = run(["sh", str(WORK / FOLDERS[name] / ".journal/src/journal.sh"), *words], env=environment(name), cwd=WORK / FOLDERS[name], timeout=120)
    return (done.stdout + done.stderr).strip()


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


def journals() -> None:
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


def server_rows() -> list[dict]:
    program = "import json, sqlite3\nc = sqlite3.connect('/data/team/team.db')\nprint(json.dumps([[t, n, json.loads(f)] for t, n, f in c.execute('select row_table, row, fields from rows where is_deleted = 0')]))\n"
    done = subprocess.run(["ssh", "-o", "BatchMode=yes", REMOTE, "docker exec -i team python -"], input=program, capture_output=True, text=True, timeout=60)
    return [{"table": t, "id": n, **f} for t, n, f in json.loads(done.stdout)]


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
    journal("a", "task", "create", f"personal task {STAMP}", "--brief", "stays here")
    time.sleep(40)
    on_b = [environment for environment in ("ada-main", "main", "team", hubs("b")[0]["name"]) if f"personal task {STAMP}" in titles("b", environment)]
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
    return f"{'OK' if not personal else 'FAIL (waits on the migration task)'}: environments on the server: {[row.get('team_name') for row in environments]}; not the team's: {personal}"


def check_pre_hub_copy() -> str:
    return "WAITS: needs a copy of a pre-hub team journal and the migration of phase 2; not run yet"


CHECKS = (("team key and hub", check_team_key_and_hub), ("hub write reaches the other journal and the server", check_hub_write), ("a personal task never reaches the server", check_personal_task),
          ("a shared chat reaches the other journal, and unsharing takes it back", check_share_and_unshare), ("the server holds only team rows", check_server_holds_only_team_rows), ("a pre-hub team journal migrates", check_pre_hub_copy))


def checks() -> None:
    for title, check in CHECKS:
        try:
            print(f"{title}: {check()}", flush=True)
        except Exception as fault:
            print(f"{title}: FAIL: {type(fault).__name__}: {fault}", flush=True)


COMMANDS = {"deploy": deploy, "journals": journals, "checks": checks, "stop": stop}

if __name__ == "__main__":
    verb = sys.argv[1] if len(sys.argv) == 2 else ""
    if verb in COMMANDS:
        COMMANDS[verb]()
    else:
        raise SystemExit(__doc__)
