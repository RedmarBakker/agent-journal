import json
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, urlsplit

from journal.http.support.project_check import PROJECT_HEADER
from journal.support.timeout import Timeout
from journal.support.supervisor_socket import SupervisorSocket

WAIT_LIMIT_SECONDS = 600.0
TAB_WAIT_SECONDS = 8.0
BAND_WAIT_SECONDS = 8.0
BAND_POLL_SECONDS = 0.1


class PageWait:
    """The launch's watch for the journal's page: the first time the port in the port file answers as this project's journal, the band shows its address and the viewer opens in the browser; a port file a dead journal left answers nothing, and another project's journal on that port is refused."""

    def __init__(self, port_file: Path, socket: str, band: tuple[str, str], viewer: str, log: Callable[[str], None]) -> None:
        self.port_file, self.socket, self.band, self.viewer, self.log = port_file, socket, band, viewer, log

    def start(self) -> None:
        threading.Thread(target=self.wait, daemon=True).start()

    def wait(self) -> None:
        began = time.time()
        while not Timeout.seconds(WAIT_LIMIT_SECONDS).started(began).is_elapsed(time.time()):
            url = self.is_responsive()
            if url:
                self.shown(url)
                return
            time.sleep(0.5)
        self.log(f"viewer: the journal's page did not answer within {int(WAIT_LIMIT_SECONDS)} seconds, so no tab was opened")

    def is_responsive(self) -> str:
        url = f"http://127.0.0.1:{self.port_file.read_text().strip()}/" if self.port_file.is_file() else ""
        if not url:
            return ""
        health_request = urllib.request.Request(url + "journal/health", headers={PROJECT_HEADER: str(self.port_file.parent.parent)})
        try:
            with urllib.request.urlopen(health_request, timeout=0.5) as reply:
                return url if reply.status == 200 else ""
        except OSError:
            return ""

    def shown(self, url: str) -> None:
        self.update_band(url)
        if not self.viewer:
            return
        if self.tab_open(url):
            self.follow_open_viewer(url)
            self.log(f"viewer: a tab of {url} is open already, so none was opened")
            return
        opened = webbrowser.open(url + self.viewer, new=2)
        self.log(f"viewer: opened {url + self.viewer}" if opened else f"viewer: the browser would not open {url + self.viewer}")

    def update_band(self, url: str) -> None:
        if not self.socket:
            return
        request = {"verb": "band", "left": self.band[0], "middle": self.band[1], "right": url}
        began = time.monotonic()
        while time.monotonic() - began < BAND_WAIT_SECONDS:
            try:
                if SupervisorSocket.ask(self.socket, request).success:
                    return
            except OSError:
                pass
            time.sleep(BAND_POLL_SECONDS)
        self.log(f"viewer: the supervisor did not update the launch band within {int(BAND_WAIT_SECONDS)} seconds")

    def follow_open_viewer(self, url: str) -> None:
        environments = parse_qs(urlsplit(self.viewer).query).get("env", [])
        if not environments:
            return
        environment = environments[-1]
        request = urllib.request.Request(url + "journal/viewer/launch", data=json.dumps({"environment": environment}).encode(), headers={PROJECT_HEADER: str(self.port_file.parent.parent), "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=0.5) as reply:
                if reply.status < 300:
                    self.log(f"viewer: asked the open tab to use {environment}")
                    return
        except OSError:
            pass
        self.log(f"viewer: could not ask the open tab to use {environment}")

    def tab_open(self, url: str) -> bool:
        began = time.time()
        while not Timeout.seconds(TAB_WAIT_SECONDS).started(began).is_elapsed(time.time()):
            try:
                with urllib.request.urlopen(url + "journal/viewer", timeout=0.5) as reply:
                    if json.loads(reply.read()).get("open"):
                        return True
            except (OSError, ValueError):
                return False
            time.sleep(0.5)
        return False
