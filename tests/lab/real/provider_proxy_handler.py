import socket
import socketserver


class ProviderProxyHandler(socketserver.BaseRequestHandler):
    """Permit only HTTPS tunnels to the approved subscription provider hosts."""

    def handle(self) -> None:
        request = self.request.recv(8192).decode("latin-1")
        first = request.splitlines()[0].split() if request else []
        if len(first) != 3 or first[0] != "CONNECT":
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            return
        host, separator, port = first[1].rpartition(":")
        if not separator or not port.isdecimal() or int(port) != 443 or not self.server.owner.allowed(host):
            self.request.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            return
        try:
            upstream = socket.create_connection((host, int(port)), timeout=10)
        except OSError:
            self.request.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            return
        with upstream:
            self.request.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            self.server.owner.relay(self.request, upstream)
