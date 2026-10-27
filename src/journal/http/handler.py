import traceback

from journal.http.support.json_out import JsonOut
from journal.http.support.file_response import FileResponse
from journal.engine.lifecycle import Lifecycle
from journal.http.support.identity import Identity
from journal.http.support.login_gate import LoginGate
from journal.http.support.pooled_handler import PooledHandler
from journal.http.support.request import Request
from journal.http.support.request_reading import RequestReading
from journal.support.response import Response
from journal.http.router import Router
from journal.http.static_files import StaticFiles
from journal.http.support.stream_response import StreamResponse


# the one question answered while the journal boots: which phase it is in
UNHELD_PATHS = ("/journal/health",)
# the sync service's doors answer busy while the journal boots, so the service waits and tries again, never held on a thread
UNHELD_PREFIXES = ("/journal/sync/",)


class Handler(PooledHandler):
    """Turns one HTTP exchange into a Request for the router and writes its Response back, holding it while the journal boots; nothing else lives here."""

    router: Router
    identity: Identity
    static: StaticFiles
    gate: LoginGate
    lifecycle: Lifecycle

    def do_GET(self) -> None:
        request = self._request()
        if refusal := self.gate.refusal(request):
            return self._reply(refusal)
        if not request.path.startswith(("/journal/", "/hooks/", "/cli")) and self.router.matched(request) is None and (rows := self.static.serve(request.path)):
            return self._file(rows)
        self._answer(self._dispatched(request))

    def do_POST(self) -> None:
        request = self._request()
        self._answer(self.gate.refusal(request) or self._dispatched(request))

    def _dispatched(self, request: Request):
        try:
            return self.router.route(request)
        except Exception as fault:
            traceback.print_exc()
            return Response(500, {"error": f"{type(fault).__name__}: {fault}"})

    def _answer(self, answer) -> None:
        if isinstance(answer, StreamResponse):
            return self._stream(answer)
        if isinstance(answer, FileResponse):
            return self._file(answer)
        self._reply(answer)

    def log_message(self, format, *args) -> None:
        return None

    def _request(self) -> Request:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        request = RequestReading.read(RequestReading.head(self.command, self.path, dict(self.headers.items())), raw, self.identity)
        if request.path in UNHELD_PATHS or request.path.startswith(UNHELD_PREFIXES):
            return request
        boot_wait = self.lifecycle.boot_wait_seconds()
        return request.boot_delayed(boot_wait) if boot_wait else request

    def _file(self, file: FileResponse) -> None:
        self.send_response(file.status)
        self.send_header("Content-Type", file.content_type)
        self.send_header("Content-Length", str(len(file.body)))
        self.send_header("Cache-Control", "no-cache")
        for name, value in file.headers().items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(file.body)

    def _stream(self, response: StreamResponse) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            for block in response.blocks:
                self.wfile.write(block)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as fault:
            traceback.print_exc()
            self.wfile.write(f"the journal failed while answering: {type(fault).__name__}: {fault}\n".encode())

    def _reply(self, response: Response) -> None:
        body = JsonOut.encoded(response.body)
        self.send_response(response.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in response.headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)
