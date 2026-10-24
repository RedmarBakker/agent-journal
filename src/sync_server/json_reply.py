import json
from http.server import BaseHTTPRequestHandler


class JsonReply:
    """A JSON body sent as the answer to a request, with its status and length."""

    @staticmethod
    def send(handler: BaseHTTPRequestHandler, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)
