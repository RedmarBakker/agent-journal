#!/usr/local/bin/python3
import array
import ctypes
import json
import os
import re
import socket
import struct
import subprocess
import sys
from pathlib import Path


DRIVER_UID = 10003
DRIVER_GID = 10003
JOURNAL_UID = 10001
JOURNAL_GID = 10001
CODEX_HOME = "/var/lib/journal-codex"
PROGRAM = "/opt/agent-journal/src/journal.py"
SERVER_PID_FILE = "/run/journal-plan-driver-server.pid"
MAX_REQUEST = 65536
PR_SET_NO_NEW_PRIVS = 38
PR_CAPBSET_DROP = 24
PR_CAP_AMBIENT = 47
PR_CAP_AMBIENT_CLEAR_ALL = 4

libc = ctypes.CDLL(None, use_errno=True)
libc.prctl.restype = ctypes.c_int
libc.capset.restype = ctypes.c_int


def refused(connection: socket.socket, message: str) -> None:
    connection.sendall(json.dumps({"error": message}).encode())


def request_received(connection: socket.socket) -> tuple[dict, int]:
    data, ancillary, flags, _ = connection.recvmsg(MAX_REQUEST, socket.CMSG_SPACE(array.array("i").itemsize))
    if flags & socket.MSG_CTRUNC:
        raise ValueError("driver request descriptor was truncated")
    descriptors = [array.array("i", payload[:len(payload) - len(payload) % array.array("i").itemsize]) for level, kind, payload in ancillary if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS]
    file_descriptors = [descriptor for group in descriptors for descriptor in group]
    while len(data) <= MAX_REQUEST:
        part = connection.recv(min(4096, MAX_REQUEST + 1 - len(data)))
        if not part:
            break
        data += part
    if len(data) > MAX_REQUEST or len(file_descriptors) != 1:
        for descriptor in file_descriptors:
            os.close(descriptor)
        raise ValueError("driver request must carry one log descriptor and stay within its size limit")
    try:
        request = json.loads(data)
    except json.JSONDecodeError:
        os.close(file_descriptors[0])
        raise
    return request, file_descriptors[0]


def plan_worktree(root: Path, request: dict) -> tuple[str, Path, str]:
    environment = request.get("environment")
    if not isinstance(environment, str) or not re.fullmatch(r"plan-[1-9][0-9]*", environment):
        raise ValueError("only a numbered Plan environment can use the Codex driver")
    configured_root = Path(os.environ["JOURNAL_ROOT"]).resolve()
    requested_root = Path(request.get("root", "")).resolve()
    if requested_root != root or root != configured_root:
        raise ValueError("the Plan driver must use the designated journal root")
    worktree = root / ".claude" / "worktrees" / environment
    requested_worktree = Path(request.get("worktree", ""))
    if requested_worktree != worktree or worktree.is_symlink() or not worktree.is_dir():
        raise ValueError("the Plan driver's worktree does not match its environment")
    if worktree.resolve() != worktree:
        raise ValueError("the Plan driver's worktree cannot resolve through a link")
    port = request.get("port")
    if not isinstance(port, str) or not port.isdigit() or not 1 <= int(port) <= 65535:
        raise ValueError("the Plan driver needs the designated journal port")
    resume = request.get("resume", [])
    if not isinstance(resume, list) or len(resume) > 8 or any(not isinstance(value, str) or "\x00" in value or len(value) > 4096 for value in resume):
        raise ValueError("the Plan driver's resume arguments are invalid")
    return environment, worktree, port


def restricted_identity() -> None:
    if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1:
        raise OSError(ctypes.get_errno(), "could not set no-new-privileges for the Plan driver")
    for capability in range(64):
        if libc.prctl(PR_CAPBSET_DROP, capability, 0, 0, 0) == -1:
            error = ctypes.get_errno()
            if error == 22:
                break
            raise OSError(error, "could not drop the Plan driver's capability bounding set")
    if libc.prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL, 0, 0, 0) == -1:
        raise OSError(ctypes.get_errno(), "could not clear the Plan driver's ambient capabilities")
    os.setgroups([])
    os.setgid(DRIVER_GID)
    os.setuid(DRIVER_UID)
    header = ctypes.create_string_buffer(struct.pack("II", 0x20080522, 0))
    data = ctypes.create_string_buffer(struct.pack("III", 0, 0, 0) * 2)
    if libc.capset(ctypes.byref(header), ctypes.byref(data)) == -1:
        raise OSError(ctypes.get_errno(), "could not clear the Plan driver's capability sets")


def launched(connection: socket.socket, request: dict, log_fd: int, root: Path) -> None:
    environment, worktree, port = plan_worktree(root, request)
    resume = request.get("resume", [])
    command = [sys.executable, PROGRAM, "codex", "--env", environment, "--worktree", environment, "--yes", "--no-open", "--no-journal", "--skip", "--", *resume]
    child_environment = {
        "CODEX_HOME": CODEX_HOME,
        "HOME": CODEX_HOME,
        "JOURNAL_ROOT": str(root),
        "JOURNAL_PORT": port,
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONSAFEPATH": "1",
    }
    os.set_inheritable(log_fd, True)
    process = subprocess.Popen(command, cwd=worktree, env=child_environment, stdin=subprocess.DEVNULL, stdout=log_fd, stderr=subprocess.STDOUT, start_new_session=True, preexec_fn=restricted_identity)
    connection.sendall(json.dumps({"pid": process.pid}).encode())
    os.close(log_fd)


def main() -> None:
    socket_path = os.environ["JOURNAL_PLAN_DRIVER_SOCKET"]
    root = Path(os.environ["JOURNAL_ROOT"]).resolve()
    server_pid = int(Path(SERVER_PID_FILE).read_text().strip())
    os.setgroups([JOURNAL_GID])
    os.setgid(JOURNAL_GID)
    os.umask(0o007)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_path)
    os.chmod(socket_path, 0o660)
    server.listen(8)
    while True:
        connection, _ = server.accept()
        with connection:
            descriptor = -1
            try:
                peer_pid, peer_uid, _ = struct.unpack("3i", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
                if peer_uid != JOURNAL_UID or peer_pid != server_pid:
                    raise PermissionError("only the designated journal server process can launch a Plan driver")
                request, descriptor = request_received(connection)
                launched(connection, request, descriptor, root)
                descriptor = -1
            except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
                if descriptor >= 0:
                    os.close(descriptor)
                refused(connection, str(error))


if __name__ == "__main__":
    main()
