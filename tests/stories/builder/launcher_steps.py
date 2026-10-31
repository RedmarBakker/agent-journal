import json
from contextlib import nullcontext
from types import SimpleNamespace
from urllib.parse import urlsplit

from journal.http.support.json_out import JsonOut
from journal.launcher.support.page_wait import PageWait
from tests.in_process import routed


class LauncherSteps:
    """What the launcher tells the viewer when its page is already open."""

    def launcher_starts_viewer_in(self, environment: str):
        def answered(request, timeout=0.5):
            address = request if isinstance(request, str) else request.full_url
            method = "GET" if isinstance(request, str) else request.get_method()
            headers = {} if isinstance(request, str) else dict(request.header_items())
            response = routed(self.app, method, urlsplit(address).path + (f"?{urlsplit(address).query}" if urlsplit(address).query else ""), request.data if not isinstance(request, str) else b"", headers)
            body = JsonOut.encoded(response.body)
            return nullcontext(SimpleNamespace(status=response.status, read=lambda: body))

        self.monkeypatch.setattr("urllib.request.urlopen", answered)
        lines = []
        page = PageWait(self.app.config.root / ".journal" / "port", "", ("journal", environment), f"?env={environment}", lines.append)
        page.shown("http://journal/")
        self.viewer_status, self.viewer_answer = 200, {"log": "\n".join(lines)}
        return self.observed(f"the launcher starts the viewer in {environment}", None, None)
