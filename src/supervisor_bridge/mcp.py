import json
import sys
from typing import TextIO

from supervisor_bridge.bridge import SupervisorBridge
from supervisor_bridge.contracts import ContractError, TOOL_NAMES, tool_input_schemas


PROTOCOL_VERSIONS = frozenset({"2024-11-05", "2025-03-26", "2025-06-18"})
MAX_FRAME_BYTES = 65536
TOOL_DESCRIPTIONS = {
    TOOL_NAMES[0]: "Read the admitted journal snapshot and its bounded observation page.",
    TOOL_NAMES[1]: "Submit only typed maintenance operations under the admitted journal fence.",
    TOOL_NAMES[2]: "Read the canonical journal receipt for the admitted action.",
}


class McpServer:
    """A line-oriented MCP server whose only tools are the fixed journal trio."""

    def __init__(self, bridge: SupervisorBridge):
        self.bridge = bridge
        self.cursors: dict[str, str | None] = {}
        self.schemas = tool_input_schemas()

    def handle(self, message: object) -> dict | None:
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
            return self.error(message.get("id") if isinstance(message, dict) else None, -32600, "Invalid Request")
        method = message["method"]
        request_id = message.get("id")
        if method == "notifications/initialized" or (method.startswith("notifications/") and "id" not in message):
            return None
        if "id" not in message:
            return None
        if method == "initialize":
            return self.initialize(request_id, message.get("params", {}))
        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}
        if method == "tools/list":
            return self.tool_list(request_id)
        if method == "tools/call":
            return self.tool_call(request_id, message.get("params"))
        return self.error(request_id, -32601, "Method not found")

    def initialize(self, request_id: object, params: object) -> dict:
        if not isinstance(params, dict):
            return self.error(request_id, -32602, "Invalid params")
        version = params.get("protocolVersion")
        if not isinstance(version, str) or version not in PROTOCOL_VERSIONS:
            return self.error(request_id, -32602, "Unsupported protocol version")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "journal-supervisor", "version": "1.0.0"},
            },
        }

    def tool_list(self, request_id: object) -> dict:
        tools = [
            {"name": name, "description": TOOL_DESCRIPTIONS[name], "inputSchema": self.schemas[name]}
            for name in TOOL_NAMES
        ]
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

    def tool_call(self, request_id: object, params: object) -> dict:
        if not isinstance(params, dict) or set(params) != {"name", "arguments"}:
            return self.error(request_id, -32602, "Invalid params")
        name = params["name"]
        if name not in TOOL_NAMES:
            return self.error(request_id, -32602, "Tool is not enabled")
        arguments = params["arguments"]
        try:
            if name == TOOL_NAMES[0]:
                if not isinstance(arguments, dict) or set(arguments) != {"run_ref", "cursor"}:
                    raise ContractError("observe requires only the current run_ref and page cursor")
                run = self.bridge.require_active(arguments.get("run_ref") if isinstance(arguments, dict) else None)
                expected_cursor = self.cursors.get(run.run_id, self.bridge.state.observation_cursor())
                if arguments.get("cursor") != expected_cursor:
                    raise ContractError("cursor is not the current journal page cursor")
                result = self.bridge.observe(arguments["run_ref"], expected_cursor)
                self.cursors[run.run_id] = result["page"]["next_cursor"]
            elif name == TOOL_NAMES[1]:
                result = self.bridge.apply(arguments)
                self.acknowledge_cursor(result)
            else:
                if not isinstance(arguments, dict) or set(arguments) != {"run_ref"}:
                    raise ContractError("receipt requires only the current run_ref")
                result = self.bridge.receipt(arguments["run_ref"])
                self.acknowledge_cursor(result)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, separators=(",", ":"))}], "isError": False},
            }
        except (ContractError, KeyError, TypeError, ValueError):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": "The journal supervisor request was rejected."}], "isError": True},
            }
        except Exception:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": "The journal supervisor service is unavailable."}], "isError": True},
            }

    def acknowledge_cursor(self, receipt: dict) -> None:
        if receipt.get("verification") not in {"verified", "superseded", "not_applied"}:
            return
        run = self.bridge.state.active_run()
        if run is None:
            return
        self.bridge.state.record_cursor(self.cursors.get(run.run_id, self.bridge.state.observation_cursor()))

    @staticmethod
    def error(request_id: object, code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    def serve(self, source: TextIO = sys.stdin, destination: TextIO = sys.stdout) -> None:
        while line := source.readline(MAX_FRAME_BYTES + 1):
            try:
                if len(line.encode("utf-8")) > MAX_FRAME_BYTES:
                    while line and not line.endswith("\n"):
                        line = source.readline(MAX_FRAME_BYTES + 1)
                    response = self.error(None, -32700, "Request exceeded the frame limit")
                else:
                    response = self.handle(json.loads(line))
            except (json.JSONDecodeError, UnicodeDecodeError):
                response = self.error(None, -32700, "Parse error")
            if response is not None:
                destination.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
                destination.flush()

