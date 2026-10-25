import json
import os
import select
import signal
import socket
import subprocess
import tempfile
import time
from collections.abc import Callable

from journal.config import Config
from journal.features.plugins.support.plugin_fault import PluginFault
from journal.features.plugins.support.window_missed import WindowMissed
from journal.features.plugins.support.plugin_folders import PluginFolders
from journal.features.plugins.support.plugin_settings import PluginSettings
from journal.support.login_path import LoginPath
from journal.support.plugin_tokens import PluginTokens
from journal.features.plugins.support.protocol import Protocol
from journal.models.plugin import Plugin
from journal.features.plugins.support.plugin_answer import PluginAnswer

PASSED_VARIABLES = ("HOME", "LANG", "LC_ALL", "TMPDIR", "USER")
# a service socket that is gone or dropped the connection, as a service exiting or restarting leaves it: the plugin's program answers instead
READ_BYTES = 65536
SOCKET_FAILURES = (ConnectionRefusedError, FileNotFoundError, BrokenPipeError, ConnectionResetError)


class PluginRunner:
    """Runs a plugin's program for one event: the line on its input, in its own folder and process group, with a clean environment that names the journal and the plugin and has the user's login shell's PATH, and at most the time it is given, each line it prints that holds a status told on as it comes; a plugin with a service is asked on its socket first, and its program answers when the socket is gone or drops the connection, the supervisor starting the service again by its restart rule."""

    def __init__(self, config: Config, folders: PluginFolders, tokens: PluginTokens, protocol: Protocol, settings: PluginSettings, login_path: LoginPath) -> None:
        self.config, self.folders, self.tokens, self.protocol, self.settings, self.login_path = config, folders, tokens, protocol, settings, login_path

    def ask(self, plugin: Plugin, environment: str, line: str, window: float, on_status: Callable[[str], None] | None = None) -> PluginAnswer:
        subscribed = self.folders.socket(plugin, environment)
        if any(s.answers for s in plugin.manifest.services) and subscribed.is_socket():
            try:
                return self.service_run(subscribed, line, window)
            except SOCKET_FAILURES:
                return self.program_run(plugin, environment, line, window, on_status)
        return self.program_run(plugin, environment, line, window, on_status)

    def service_run(self, subscribed, line: str, window: float) -> PluginAnswer:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as link:
            link.settimeout(window)
            try:
                link.connect(str(subscribed))
                link.sendall((line + "\n").encode())
                answer = link.makefile("rb").readline().decode()
            except TimeoutError as late:
                raise WindowMissed(f"its service gave no answer within {window * 1000:.0f} ms, its hold window") from late
            except SOCKET_FAILURES:
                raise
            except OSError as failed:
                raise PluginFault(f"its service did not answer on its socket: {failed}") from failed
            if not answer:
                raise ConnectionResetError("the service closed its socket without an answer")
            return self.protocol.parsed_answer(answer)

    def program_run(self, plugin: Plugin, environment: str, line: str, window: float, on_status: Callable[[str], None] | None = None) -> PluginAnswer:
        folder = self.folders.folder(plugin)
        with tempfile.TemporaryFile("w+") as given, tempfile.TemporaryFile("w+") as errors:
            given.write(line + "\n")
            given.seek(0)
            process = subprocess.Popen([str(folder / plugin.manifest.program)], cwd=folder, env=self.environment(plugin, environment), stdin=given, stdout=subprocess.PIPE, stderr=errors, bufsize=0, start_new_session=True)
            try:
                output = self.printed(process, window, on_status)
            except WindowMissed:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise
            finally:
                process.stdout.close()
            errors.seek(0)
            if process.returncode != 0:
                raise PluginFault(f"it exited with {process.returncode}: {errors.read().strip()[-300:]}")
        return self.protocol.parsed_answer(output)

    def printed(self, process: subprocess.Popen, window: float, on_status: Callable[[str], None] | None) -> str:
        ends, printed, partial = time.monotonic() + window, [], b""
        while True:
            remaining = ends - time.monotonic()
            if remaining <= 0 or not select.select([process.stdout], [], [], remaining)[0]:
                raise WindowMissed(f"it gave no answer within {window * 1000:.0f} ms, its hold window")
            chunk = os.read(process.stdout.fileno(), READ_BYTES)
            if not chunk:
                break
            *whole, partial = (partial + chunk).split(b"\n")
            for text in whole:
                printed.append(text.decode(errors="replace"))
                self.told(printed[-1], on_status)
        printed.append(partial.decode(errors="replace"))
        try:
            process.wait(timeout=max(ends - time.monotonic(), 0.001))
        except subprocess.TimeoutExpired as late:
            raise WindowMissed(f"it gave no answer within {window * 1000:.0f} ms, its hold window") from late
        return "\n".join(printed)

    def told(self, text: str, on_status: Callable[[str], None] | None) -> None:
        if on_status and (status := self.protocol.status_of(text)):
            on_status(status)

    def shell(self, plugin: Plugin, environment: str, line: str, seconds: float) -> subprocess.CompletedProcess:
        return subprocess.run(["sh", "-c", line], cwd=self.folders.folder(plugin), env=self.environment(plugin, environment), capture_output=True, text=True, timeout=seconds)

    def environment(self, plugin: Plugin, environment: str) -> dict[str, str]:
        settings = self.folders.settings(plugin)
        settings.write_text(json.dumps(plugin.settings))
        port = self.config.port_file.read_text().strip() if self.config.port_file.is_file() else str(self.config.port)
        return {key: os.environ[key] for key in PASSED_VARIABLES if key in os.environ} | {
            "PATH": os.pathsep.join([str(self.config.home / "bin"), self.login_path.value()]),
            "JOURNAL_ROOT": str(self.config.root),
            "JOURNAL_URL": f"http://127.0.0.1:{port}",
            "JOURNAL_ENV": environment,
            "JOURNAL_PLUGIN": plugin.name,
            "JOURNAL_PLUGIN_TOKEN": self.tokens.build(plugin.name),
            "JOURNAL_PLUGIN_DIR": str(self.folders.folder(plugin)),
            "JOURNAL_PLUGIN_DATA": str(self.folders.data(plugin)),
            "JOURNAL_SETTINGS": str(settings),
        } | self.settings.supplied(plugin)
