from dataclasses import dataclass, field
from http.client import HTTPSConnection, HTTPException
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time
from typing import Callable, Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen

from supervisor_bridge.contracts import ContractError, METERED_PROVIDER_BASE_URL, RunReference
from supervisor_bridge.state import StateError, StateStore


METERED_PROVIDER_HEALTH_URL = "http://127.0.0.1:17840/healthz"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 17840
PROVIDER_HOST = "api.openai.com"
MODEL_ID = "gpt-6.1-sol"
MAX_PROVIDER_ATTEMPTS = 2
MAX_PROXY_REQUEST_BYTES = 1_048_576
MAX_PROVIDER_RESPONSE_BYTES = 8_388_608
INPUT_COUNT_FIELDS = frozenset({
    "model", "input", "instructions", "tools", "tool_choice", "parallel_tool_calls",
    "previous_response_id", "conversation", "reasoning", "text", "truncation", "prompt",
})
NON_INPUT_FIELDS = frozenset({
    "max_output_tokens", "stream", "store", "metadata", "prompt_cache_key", "prompt_cache_retention",
    "temperature", "top_p", "service_tier", "user", "safety_identifier", "background", "include",
})


def grant_token_limits(snapshot: object, run: RunReference) -> dict:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("grant"), dict):
        raise ContractError("admitted run observation has no canonical grant")
    grant = snapshot["grant"]
    if grant.get("grant_id") != run.grant_id or grant.get("grant_version") != run.grant_version:
        raise ContractError("observed grant differs from the admitted run")
    limits = grant.get("limits")
    fields = {"max_input_tokens_per_turn", "max_output_tokens_per_turn", "max_provider_requests_per_turn"}
    if not isinstance(limits, dict) or not fields.issubset(limits):
        raise ContractError("observed grant has no complete provider token limits")
    result = {key: limits[key] for key in fields}
    if any(type(value) is not int or value < 1 for value in result.values()):
        raise ContractError("observed grant provider token limits are invalid")
    return result


class MeteringError(RuntimeError):
    """A provider request cannot continue within the admitted run's grant."""

    def __init__(self, message: str, status_code: int = 429):
        super().__init__(message)
        self.status_code = status_code


class ProviderTransport(Protocol):
    """One fixed provider request made by the metering proxy."""

    def post(self, path: str, payload: dict, accept: str) -> "ProviderResponse": ...


@dataclass(frozen=True)
class ProviderResponse:
    status: int
    body: bytes
    content_type: str = "application/json"
    headers: dict[str, str] = field(default_factory=dict)


class OpenAIProviderTransport:
    """A fixed-origin, API-key-only connection to the pinned Responses API."""

    def __init__(self, api_key: str, timeout: int = 180):
        if not api_key or len(api_key) > 4096:
            raise MeteringError("the provider API key is unavailable", 503)
        self.api_key = api_key
        self.timeout = timeout

    def post(self, path: str, payload: dict, accept: str) -> ProviderResponse:
        if path not in {"/v1/responses/input_tokens", "/v1/responses"}:
            raise MeteringError("provider route is not enabled", 404)
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        if len(body) > MAX_PROXY_REQUEST_BYTES:
            raise MeteringError("provider request exceeded the fixed byte limit", 413)
        connection = HTTPSConnection(PROVIDER_HOST, 443, timeout=self.timeout)
        try:
            connection.request("POST", path, body, {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": accept,
                "Accept-Encoding": "identity",
            })
            response = connection.getresponse()
            result_body = response.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
            if len(result_body) > MAX_PROVIDER_RESPONSE_BYTES:
                raise MeteringError("provider response exceeded the fixed byte limit", 502)
            headers = {name.lower(): value for name, value in response.getheaders()}
            return ProviderResponse(response.status, result_body, headers.get("content-type", "application/json"), headers)
        finally:
            connection.close()


class MeteringProxy:
    """A single-run OpenAI Responses proxy with durable grant accounting."""

    def __init__(self, state: StateStore, provider: ProviderTransport, retry_wait: Callable[[float], None] = time.sleep):
        self.state = state
        self.provider = provider
        self.retry_wait = retry_wait

    def forward(self, value: object, accept: str = "application/json") -> ProviderResponse:
        request = self.request_object(value)
        request["model"] = MODEL_ID
        with self.state.provider_locked() as acquired:
            if not acquired:
                raise MeteringError("another provider request holds the run meter", 409)
            run = self.current_run()
            self.require_capacity(run, 2, "provider request cap")
            count = self.input_count(run, request)
            limits = self.state.metering_state(run)["limits"]
            usage = self.state.metering_state(run)
            remaining_output = limits["max_output_tokens_per_turn"] - usage["output_tokens"]
            if remaining_output < 1:
                self.state.mark_provider_cap(run)
                raise MeteringError("output token cap reached")
            requested_output = request.get("max_output_tokens", remaining_output)
            if type(requested_output) is not int or requested_output < 1:
                raise MeteringError("provider output limit is invalid", 400)
            request["max_output_tokens"] = min(requested_output, remaining_output)
            response = self.generation(run, request, accept)
            try:
                tokens = self.response_usage(response)
            except MeteringError:
                self.state.record_provider_unknown_cost(run, "provider_usage_missing")
                raise
            if tokens["input_tokens"] != count:
                self.state.record_provider_unknown_cost(run, "provider_usage_mismatch")
                raise MeteringError("provider usage does not match the input token preflight", 502)
            if not self.state.record_provider_usage(run, tokens["input_tokens"], tokens["output_tokens"], tokens["cached_tokens"]):
                raise MeteringError("provider usage exceeded the grant token cap", 502)
            return response

    @staticmethod
    def request_object(value: object) -> dict:
        if not isinstance(value, dict) or not isinstance(value.get("model"), str):
            raise MeteringError("provider request must name the pinned model", 400)
        if value["model"] not in {MODEL_ID, f"openai/{MODEL_ID}"}:
            raise MeteringError("provider request changed the pinned model", 403)
        unsupported = set(value) - INPUT_COUNT_FIELDS - NON_INPUT_FIELDS
        if unsupported:
            raise MeteringError("provider request has uncounted input fields", 400)
        if not ("input" in value or "prompt" in value or "previous_response_id" in value):
            raise MeteringError("provider request has no countable input", 400)
        return dict(value)

    def current_run(self) -> RunReference:
        run = self.state.active_run()
        if run is None:
            raise MeteringError("there is no active admitted run", 403)
        try:
            metering = self.state.metering_state(run)
        except StateError:
            raise MeteringError("the active run has no durable metering record", 403) from None
        if self.state.snapshot()["budget_gate"] != "verified" or metering["limits"] is None:
            raise MeteringError("the active run has no verified grant limits", 403)
        if metering["status"] == "capped":
            if (
                metering["input_tokens"] >= metering["limits"]["max_input_tokens_per_turn"]
                or metering["output_tokens"] >= metering["limits"]["max_output_tokens_per_turn"]
            ):
                raise MeteringError("token cap reached")
            raise MeteringError("provider request cap reached")
        if metering["status"] not in {"ready", "known"}:
            raise MeteringError("the active run's provider budget is closed")
        if metering["pending_request"] is not None:
            self.state.record_provider_unknown_cost(run, "provider_request_uncertain")
            raise MeteringError("a provider request did not settle before restart", 503)
        return run

    def input_count(self, run: RunReference, request: dict) -> int:
        count_request = {key: value for key, value in request.items() if key in INPUT_COUNT_FIELDS}
        count_request["model"] = MODEL_ID
        response = self.provider_request(run, "input_count", "/v1/responses/input_tokens", count_request, "application/json")
        if not 200 <= response.status < 300:
            self.state.record_provider_unknown_cost(run, "provider_request_uncertain")
            raise MeteringError("provider input token count failed closed", 502)
        try:
            value = json.loads(response.body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.state.record_provider_unknown_cost(run, "provider_usage_missing")
            raise MeteringError("provider input token count is missing", 502) from None
        count = value.get("input_tokens") if isinstance(value, dict) else None
        if type(count) is not int or count < 0:
            self.state.record_provider_unknown_cost(run, "provider_usage_missing")
            raise MeteringError("provider input token count is missing", 502)
        if not self.state.record_input_token_count(run, count):
            raise MeteringError("input token cap reached before provider generation")
        return count

    def generation(self, run: RunReference, request: dict, accept: str) -> ProviderResponse:
        response = self.provider_request(run, "generation", "/v1/responses", request, accept)
        if not 200 <= response.status < 300:
            self.state.record_provider_unknown_cost(run, "provider_request_uncertain")
            raise MeteringError("provider generation failed closed", 502)
        return response

    def provider_request(self, run: RunReference, kind: str, path: str, payload: dict, accept: str) -> ProviderResponse:
        for attempt in range(MAX_PROVIDER_ATTEMPTS):
            if not self.state.begin_provider_request(run, kind, retry=attempt > 0):
                self.state.mark_provider_cap(run)
                raise MeteringError("provider request cap reached")
            try:
                response = self.provider.post(path, payload, accept)
            except (HTTPException, OSError, TimeoutError, URLError) as error:
                self.state.record_provider_unknown_cost(run, "provider_request_uncertain")
                raise MeteringError("provider request outcome is uncertain", 502) from error
            if response.status in {401, 403}:
                self.state.record_provider_unknown_cost(run, "provider_unauthorized")
                raise MeteringError("provider credentials were rejected; no fallback is enabled", response.status)
            if response.status != 429:
                return response
            self.state.record_provider_retryable_failure(run)
            if attempt + 1 == MAX_PROVIDER_ATTEMPTS:
                if kind == "generation":
                    self.state.clear_provider_preflight(run)
                return response
            self.retry_wait(self.retry_after(response))
        raise MeteringError("provider retry limit reached")

    @staticmethod
    def retry_after(response: ProviderResponse) -> float:
        value = next((value for key, value in response.headers.items() if key.lower() == "retry-after"), "0")
        try:
            return min(max(float(value), 0), 1)
        except ValueError:
            return 0

    @staticmethod
    def response_usage(response: ProviderResponse) -> dict:
        if "text/event-stream" in response.content_type.lower():
            return MeteringProxy.stream_usage(response.body)
        try:
            payload = json.loads(response.body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise MeteringError("provider response usage is missing", 502) from None
        usage = payload.get("usage") if isinstance(payload, dict) else None
        return MeteringProxy.checked_usage(usage)

    @staticmethod
    def stream_usage(body: bytes) -> dict:
        terminal = None
        for line in body.splitlines():
            if not line.startswith(b"data:"):
                continue
            value = line[5:].strip()
            if not value or value == b"[DONE]":
                continue
            try:
                event = json.loads(value)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(event, dict) and event.get("type") in {"response.completed", "response.incomplete"}:
                terminal = event.get("response")
        if not isinstance(terminal, dict):
            raise MeteringError("provider stream ended without a usage-bearing response", 502)
        return MeteringProxy.checked_usage(terminal.get("usage"))

    @staticmethod
    def checked_usage(value: object) -> dict:
        if not isinstance(value, dict):
            raise MeteringError("provider response usage is missing", 502)
        input_tokens = value.get("input_tokens")
        output_tokens = value.get("output_tokens")
        details = value.get("input_tokens_details")
        cached_tokens = details.get("cached_tokens") if isinstance(details, dict) else None
        if any(type(token) is not int or token < 0 for token in (input_tokens, output_tokens, cached_tokens)):
            raise MeteringError("provider response token usage is incomplete", 502)
        if cached_tokens > input_tokens:
            raise MeteringError("provider cache token usage exceeds input usage", 502)
        return {"input_tokens": input_tokens, "output_tokens": output_tokens, "cached_tokens": cached_tokens}

    def require_capacity(self, run: RunReference, count: int, reason: str) -> None:
        metering = self.state.metering_state(run)
        if metering["status"] == "capped":
            raise MeteringError(f"{reason} reached")
        if not self.state.can_start_provider_requests(run, count):
            self.state.mark_provider_cap(run)
            raise MeteringError(f"{reason} reached")


class MeteredAggregateBudgetProof:
    """Proves the pinned provider route points at a live, bounded proxy."""

    def __init__(self, state: StateStore, config_path: Path | str, health_probe: Callable[[], bool] | None = None):
        self.state = state
        self.config_path = Path(config_path)
        self.health_probe = health_probe or self.proxy_is_healthy

    def is_verified(self, run: RunReference) -> bool:
        try:
            if self.state.active_run() != run:
                return False
            if self.state.metering_state(run)["limits"] is None:
                return False
            return self.config_routes_through_proxy() and self.health_probe()
        except (KeyError, OSError, TypeError, ValueError, StateError, ContractError):
            return False

    def config_routes_through_proxy(self) -> bool:
        config = json.loads(self.config_path.read_text())
        provider = config["models"]["providers"]
        entries = config["agents"]["entries"]
        defaults = config["agents"]["defaults"]
        return (
            set(provider) == {"openai"}
            and set(provider["openai"]) == {"baseUrl", "auth", "api", "agentRuntime", "maxTokens", "timeoutSeconds"}
            and provider["openai"]["baseUrl"] == METERED_PROVIDER_BASE_URL
            and provider["openai"]["api"] == "openai-responses"
            and provider["openai"]["auth"] == "api-key"
            and provider["openai"]["agentRuntime"] == {"id": "openclaw"}
            and provider["openai"]["maxTokens"] == 8000
            and provider["openai"]["timeoutSeconds"] == 180
            and set(entries) == {"supervisor"}
            and entries["supervisor"]["runtime"] == {"type": "embedded"}
            and entries["supervisor"]["model"] == {"primary": "openai/gpt-6.1-sol", "fallbacks": []}
            and entries["supervisor"]["modelPolicy"]["allow"] == ["openai/gpt-6.1-sol"]
            and entries["supervisor"]["models"] == {
                "openai/gpt-6.1-sol": {"agentRuntime": {"id": "openclaw"}, "codeMode": False}
            }
            and defaults["utilityModel"] == "openai/gpt-6.1-sol"
            and defaults["decisionModel"] == ""
            and defaults["maxConcurrent"] == 1
        )

    @staticmethod
    def proxy_is_healthy() -> bool:
        request = Request(METERED_PROVIDER_HEALTH_URL, headers={"Accept": "application/json"}, method="GET")
        try:
            with urlopen(request, timeout=1) as response:
                value = json.loads(response.read(2048))
        except (OSError, URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError):
            return False
        return response.status == 200 and value == {"protocol_version": 1, "status": "ready", "route": METERED_PROVIDER_BASE_URL}


class MeteringProxyServer:
    """A loopback HTTP route for the fixed OpenAI Responses provider."""

    def __init__(self, proxy: MeteringProxy, host: str = PROXY_HOST, port: int = PROXY_PORT):
        self.proxy = proxy
        self.server = self.build_server(host, port)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def build_server(self, host: str, port: int) -> ThreadingHTTPServer:
        proxy = self.proxy

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path != "/healthz":
                    self.send_error(404)
                    return
                self.send_value(200, {
                    "protocol_version": 1,
                    "status": "ready",
                    "route": METERED_PROVIDER_BASE_URL,
                })

            def do_POST(self):
                if self.path != "/v1/responses":
                    self.send_error(404)
                    return
                length = self.headers.get("Content-Length", "")
                if not length.isdecimal() or int(length) > MAX_PROXY_REQUEST_BYTES:
                    self.send_error(413)
                    return
                try:
                    request = json.loads(self.rfile.read(int(length)))
                    response = proxy.forward(request, self.headers.get("Accept", "application/json"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    self.send_error(400)
                    return
                except MeteringError as error:
                    self.send_error(error.status_code, str(error))
                    return
                self.send_response(response.status)
                self.send_header("Content-Type", response.content_type)
                self.send_header("Content-Length", str(len(response.body)))
                self.send_header("Cache-Control", "no-store")
                if response.status == 429 and "retry-after" in response.headers:
                    self.send_header("Retry-After", response.headers["retry-after"])
                self.end_headers()
                self.wfile.write(response.body)

            def send_value(self, status: int, value: dict) -> None:
                body = json.dumps(value, separators=(",", ":")).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, _format: str, *_args) -> None:
                return

        return ThreadingHTTPServer((host, port), Handler)
