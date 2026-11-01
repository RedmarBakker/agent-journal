from http.server import BaseHTTPRequestHandler


class HostedJournalOrigin(BaseHTTPRequestHandler):
    """A journal response used to prove the hosted login forwards an authenticated visit."""

    def do_GET(self) -> None:
        body = f"Hosted journal content; cookie={self.headers.get('Cookie', '')}".encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
