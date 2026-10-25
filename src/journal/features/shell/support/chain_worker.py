import os
import threading
import time
from pathlib import Path
from typing import Callable

from journal.features.shell.support.changed_file import ChangedFile
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.shell_process import ShellProcess
from journal.features.shell.support.shell_record import ShellRecord
from journal.features.shell.support.shell_request import OUTPUT_FOLDER_VARIABLE, ShellRequest
from journal.support.caller import Caller
from journal.support.merger import Merger
from journal.support.part import Part

SHELL_SETUP = """
ulimit -n 65536 2>/dev/null || ulimit -n 10240 2>/dev/null || ulimit -n "$(ulimit -Hn)" 2>/dev/null
__journal_tree() {
    git diff --numstat HEAD 2>/dev/null | grep -v "	\\.journal/"
    git ls-files --others --exclude-standard 2>/dev/null | grep -v "^\\.journal/" | sed 's/^/?\\t0\\t/'
}
__journal_status() {
    case "$-" in *e*) return 0 ;; *) return "$__journal_code" ;; esac
}
__journal_code=0
(while kill -0 __JOURNAL_OWNER 2>/dev/null && kill -0 $$ 2>/dev/null; do sleep 3; done; kill -0 $$ 2>/dev/null && kill -KILL -- -$$) >/dev/null 2>&1 &
"""
POLL_SECONDS = 0.02
# Claude Code's snapshot of a bash setup can carry set -o onecmd, which ends a shell after the command it reads next; turned off on
# the same line as each part, it never ends the shell the chain's next parts are written to
ONECMD_RESET = "set +t 2>/dev/null"


class ChainWorker:
    """Runs a chain's parts one by one in one shell process, as the shell would: a part after && is skipped while the part before it failed, a part after ; runs whatever arrived before, a part before && may fail without ending a shell under set -e, and an exec part ends the chain. A part of the agent's own set-up, outside its command, that ends the shell, as a shell snapshot that execs or exits does, leaves the rest of the chain to a new shell. Each of the agent's own parts is recorded as it starts and ends with its status, its time, its output tail and the files it changed; a moved chain's end is recorded too. Output goes to the part's files, or straight through for a read or write of the project's code. The shell is a process group of its own, which a watcher in it ends, with every command it runs, once the server that started it is gone."""

    def __init__(self, record: ShellRecord, merger: Merger) -> None:
        self.record, self.merger = record, merger

    def run(self, folder: OutputFiles, request: ShellRequest, caller: Caller, direct: bool, output_text: Callable[[bytes], None]) -> int:
        request = request.folder_request(folder.folder)
        shell, pump = self.started(request, output_text)
        code = 0
        for i, kind in enumerate(folder.kinds()):
            code = self.part(shell, folder, i, kind, code, direct, caller)
            if folder.part_text(i).startswith("exec "):
                break
            if shell.process.poll() is None:
                continue
            if kind[0] == "R":
                break
            pump.join(timeout=2)
            shell, pump = self.started(request, output_text)
        self.write_part(shell, "exit $__journal_code\n")
        code = self.ended(shell, code)
        pump.join(timeout=2)
        if folder.is_moved():
            self.record.ended(folder.folder.name, code, folder.folder, "\n".join(folder.last(5)), caller)
        elif folder.number():
            self.record.foreground_end(folder.folder.name, code, caller)
        folder.finish(code)
        return code

    def started(self, request: ShellRequest, output_text: Callable[[bytes], None]) -> tuple[ShellProcess, threading.Thread]:
        shell = ShellProcess.started(request)
        OutputFiles(Path(request.environment[OUTPUT_FOLDER_VARIABLE])).shell_started(shell.process.pid)
        pump = threading.Thread(target=lambda: self.pump(shell, output_text), name="shell-output", daemon=True)
        pump.start()
        self.write_part(shell, SHELL_SETUP.replace("__JOURNAL_OWNER", str(os.getpid())))
        return shell, pump

    def part(self, shell: ShellProcess, folder: OutputFiles, i: int, kind: str, code: int, direct: bool, caller: Caller) -> int:
        recorded, tail_edges, edges, writes = kind[0] == "R", kind[1] == "&", kind[2] == "&", kind.endswith("w")
        text = folder.part_text(i)
        if tail_edges and code != 0:
            folder.ended_with(i, code)
            return code
        if recorded:
            self.record.started(folder.folder.name, text, caller)
        previous = self.tree(shell, folder, i, "before") if writes else ""
        began = time.monotonic()
        status = self.branch_write(shell, folder, i, text, edges, direct) if Part(text).is_branch_write() else self.run_part(shell, folder, i, text, edges, direct)
        following = self.tree(shell, folder, i, "after") if writes else ""
        if recorded:
            self.record.finish_part(folder.folder.name, text, status, round(time.monotonic() - began, 1), folder.output_text(i), self.changed(previous, following), caller)
        return status

    def branch_write(self, shell: ShellProcess, folder: OutputFiles, i: int, text: str, edges: bool, direct: bool) -> int:
        with self.merger.turn():
            return self.run_part(shell, folder, i, text, edges, direct)

    def run_part(self, shell: ShellProcess, folder: OutputFiles, i: int, text: str, edges: bool, direct: bool) -> int:
        self.write_part(shell, self.script(folder, i, text, edges, direct))
        return self.status_once_ended(shell, folder, i)

    @staticmethod
    def script(folder: OutputFiles, i: int, text: str, edges: bool, direct: bool) -> str:
        part = f'"$(cat {str(folder.folder / f"{i}.part")!r})"'
        redirect = "" if direct else f" > {str(folder.folder / f'{i}.out')!r} 2> {str(folder.folder / f'{i}.err')!r}"
        if text.startswith("exec "):
            run = f"(eval {part} < /dev/null{redirect}); __journal_code=$?; {ONECMD_RESET}"
        elif edges:
            run = f"if __journal_status; eval {part} < /dev/null{redirect}; then __journal_code=0; else __journal_code=$?; fi; {ONECMD_RESET}"
        else:
            run = f"__journal_status; eval {part} < /dev/null{redirect}; __journal_code=$?; {ONECMD_RESET}"
        status = str(folder.folder / f"{i}.status")
        return f"{run}\necho \"$__journal_code\" > {status + '.part'!r} && mv {status + '.part'!r} {status!r}\n"

    def tree(self, shell: ShellProcess, folder: OutputFiles, i: int, moment: str) -> str:
        path = folder.folder / f"{i}.{moment}"
        self.write_part(shell, f"__journal_tree > {str(path)!r} 2>/dev/null; : > {str(path)!r}.ready\n")
        ready = Path(f"{path}.ready")
        while not ready.is_file() and shell.process.poll() is None:
            time.sleep(POLL_SECONDS)
        return path.read_text(errors="replace") if path.is_file() else ""

    @staticmethod
    def status_once_ended(shell: ShellProcess, folder: OutputFiles, i: int) -> int:
        while not folder.has_ended(i):
            if shell.process.poll() is not None:
                return shell.process.returncode
            time.sleep(POLL_SECONDS)
        return folder.status(i)

    @staticmethod
    def ended(shell: ShellProcess, code: int) -> int:
        try:
            shell.stdin.close()
        except OSError:
            pass
        returned = shell.process.wait()
        return returned if returned != 0 and code == 0 else code

    @staticmethod
    def write_part(shell: ShellProcess, script: str) -> None:
        try:
            shell.stdin.write(script.encode())
            shell.stdin.flush()
        except (BrokenPipeError, OSError):
            return

    @staticmethod
    def pump(shell: ShellProcess, output_text: Callable[[bytes], None]) -> None:
        for block in iter(lambda: shell.stdout.read1(65536), b""):
            output_text(block)

    @classmethod
    def changed(cls, previous: str, following: str) -> list[ChangedFile]:
        older = set(previous.splitlines())
        return [cls.changed_file(line) for line in following.splitlines() if line not in older and line.count("\t") == 2]

    @staticmethod
    def changed_file(line: str) -> ChangedFile:
        added, removed, path = line.split("\t", 2)
        if added == "?":
            added = str(sum(1 for _ in open(path, errors="replace"))) if Path(path).is_file() else "0"
        return ChangedFile(int(added) if added.isdigit() else 0, int(removed) if removed.isdigit() else 0, path)
