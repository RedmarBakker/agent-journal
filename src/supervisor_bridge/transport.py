import json
import re
import ssl
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from supervisor_bridge.contracts import (
    ROUTES,
    RunReference,
    bounded_cursor,
    bounded_text,
    nonnegative_integer,
    positive_integer,
    strict_object,
)


REQUEST_TIMEOUT_SECONDS = 20
RESPONSE_MAX_BYTES = 1_048_576
HOOK_PATH = "/hooks/agent"
RECEIPT_ENVELOPE_FIELDS = frozenset({"status", "reason", "receipt_id", "data", "report", "duplicate"})


class TransportError(RuntimeError):
    """A fixed supervisor route or hook request failed."""


class AuthorizationError(TransportError):
    """A dedicated service credential was rejected."""


class RetryableTransportError(TransportError):
    """A bounded retry may be made with the same request identity."""

    def __init__(self, message: str, cause: str = "TransportError"):
        known_cause = isinstance(cause, str) and cause in {
            "URLError", "SSLError", "TimeoutError", "OSError", "TransportError", "HTTP error"
        }
        known_status = isinstance(cause, str) and re.fullmatch(r"HTTP (?:429|5[0-9]{2})", cause)
        if not isinstance(cause, str) or not (known_cause or known_status):
            raise ValueError("retryable transport cause is unsupported")
        super().__init__(message)
        self.cause = cause


def retryable_cause(error: BaseException) -> str:
    if isinstance(error, HTTPError):
        if type(error.code) is int and (error.code == 429 or 500 <= error.code <= 599):
            return f"HTTP {error.code}"
        return "HTTP error"
    if isinstance(error, URLError):
        reason = error.reason
        if isinstance(reason, ssl.SSLError):
            return "SSLError"
        if isinstance(reason, TimeoutError):
            return "TimeoutError"
        if isinstance(reason, OSError):
            return "OSError"
        return "URLError"
    if isinstance(error, ssl.SSLError):
        return "SSLError"
    if isinstance(error, TimeoutError):
        return "TimeoutError"
    if isinstance(error, OSError):
        return "OSError"
    return "TransportError"


class ReceiptNotFound(TransportError):
    """The journal has not recorded a canonical receipt yet."""


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


class JsonHttpConnection:
    """A bounded JSON connection with redirects disabled and no fallback identity."""

    def __init__(self, base_url: str, token: str, timeout: int = REQUEST_TIMEOUT_SECONDS, ca_file: str = ""):
        self.base_url = self.checked_base_url(base_url)
        self.token = bounded_text(token, "service token", 1, 4096)
        self.timeout = timeout
        handlers = [NoRedirectHandler()]
        if ca_file:
            handlers.append(HTTPSHandler(context=ssl.create_default_context(cafile=ca_file)))
        self.opener = build_opener(*handlers)

    def post(self, path: str, payload: dict, idempotency_key: str = "") -> dict:
        if path not in ROUTES.values():
            raise TransportError("journal adapter route is not enabled")
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        if len(body) > 65536:
            raise TransportError("journal request exceeded the byte limit")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = bounded_text(idempotency_key, "idempotency key", 1, 256)
        request = Request(f"{self.base_url}{path}", data=body, headers=headers, method="POST")
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                return self.response_object(response.read(RESPONSE_MAX_BYTES + 1))
        except HTTPError as error:
            if error.code in {401, 403}:
                raise AuthorizationError("dedicated service credential was rejected") from None
            if error.code == 404 and path == ROUTES["receipt"]:
                raise ReceiptNotFound("canonical receipt is not available yet") from None
            if error.code == 429 or error.code >= 500:
                raise RetryableTransportError(f"service returned HTTP {error.code}", retryable_cause(error)) from None
            raise TransportError(f"service rejected the fixed request with HTTP {error.code}") from None
        except (TimeoutError, URLError, OSError) as error:
            raise RetryableTransportError("service request did not complete", retryable_cause(error)) from error

    @staticmethod
    def checked_base_url(value: str) -> str:
        bounded_text(value, "service URL", 1, 2048)
        parsed = urlsplit(value)
        local = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        if parsed.scheme != "https" and not (parsed.scheme == "http" and local):
            raise TransportError("service URL must use HTTPS or loopback HTTP")
        if not parsed.netloc or parsed.username or parsed.password or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            raise TransportError("service URL must be one fixed origin")
        return value.rstrip("/")

    @staticmethod
    def response_object(body: bytes) -> dict:
        if len(body) > RESPONSE_MAX_BYTES:
            raise TransportError("service response exceeded the byte limit")
        try:
            value = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise TransportError("service response was not valid JSON") from error
        if not isinstance(value, dict):
            raise TransportError("service response must be an object")
        return value


class SupervisorHttpClient:
    """Only the five fixed contract routes are available through the journal client."""

    def __init__(self, connection: JsonHttpConnection):
        self.connection = connection

    def admit(self, source: str, observation_cursor: str | None) -> dict:
        if source not in {"timer", "hint"}:
            raise TransportError("admission source is not enabled")
        bounded_cursor(observation_cursor)
        return self.connection.post(ROUTES["admit"], {
            "protocol_version": 1,
            "source": source,
            "observation_cursor": observation_cursor,
        })

    def observe(self, request: dict) -> dict:
        fields = frozenset({"protocol_version", "run_id", "installation_epoch", "fence", "cursor"})
        strict_object(request, fields, fields, "observe request")
        if type(request["protocol_version"]) is not int or request["protocol_version"] != 1:
            raise TransportError("observe protocol version is unsupported")
        bounded_text(request["run_id"], "run_id", 1, 256)
        positive_integer(request["installation_epoch"], "installation_epoch")
        positive_integer(request["fence"], "fence")
        bounded_cursor(request["cursor"])
        return self.connection.post(ROUTES["observe"], request)

    def apply(self, request: dict) -> dict:
        fields = frozenset({
            "protocol_version", "run_id", "installation_epoch", "fence", "grant_version", "episode_id", "action_id",
            "observation_ids", "expected_revisions", "operations", "rationale",
        })
        strict_object(request, fields, fields, "apply request")
        envelope = self.connection.post(ROUTES["apply"], request)
        return self.canonical_receipt(envelope)

    def settle_usage(self, run: RunReference, usage: dict) -> dict:
        fields = frozenset({
            "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
            "total_input_tokens", "provider_requests", "provider_retries",
        })
        strict_object(usage, fields, fields, "metered usage")
        for key in fields:
            nonnegative_integer(usage[key], key)
        if (usage["provider_requests"] < 1 or usage["provider_retries"] > usage["provider_requests"]
                or usage["total_input_tokens"] != usage["input_tokens"]
                + usage["cache_creation_input_tokens"] + usage["cache_read_input_tokens"]):
            raise TransportError("metered usage totals are inconsistent")
        request = {"protocol_version": 1, "run_ref": run.to_dict(), "usage": dict(usage)}
        result = self.connection.post(ROUTES["usage"], request, idempotency_key=run.run_id)
        if (set(result) != {"status", "usage_id", "run_id", "fence", "usage_status", "duplicate"}
                or result["status"] != "settled" or type(result["usage_id"]) is not int or result["usage_id"] < 1
                or result["run_id"] != run.run_id or type(result["fence"]) is not int or result["fence"] != run.fence
                or result["usage_status"] != "known" or type(result["duplicate"]) is not bool):
            raise TransportError("journal did not settle known usage for the admitted run")
        return result

    def receipt(self, action_id: str) -> dict:
        bounded_text(action_id, "action_id", 1, 256)
        envelope = self.connection.post(ROUTES["receipt"], {"protocol_version": 1, "action_id": action_id})
        return self.canonical_receipt(envelope)

    @staticmethod
    def canonical_receipt(envelope: dict) -> dict:
        data = envelope.get("data")
        if (set(envelope) != RECEIPT_ENVELOPE_FIELDS or not isinstance(data, dict)
                or type(envelope["receipt_id"]) is not int or envelope["receipt_id"] < 1
                or not isinstance(envelope["report"], dict) or type(envelope["duplicate"]) is not bool
                or envelope["status"] != data.get("status") or envelope["reason"] != data.get("reason")):
            raise TransportError("journal receipt envelope is unsupported")
        return data


@dataclass(frozen=True)
class HookAcknowledgement:
    gateway_run_id: str


def hook_request(run: RunReference) -> tuple[dict, dict[str, str]]:
    reference = json.dumps(run.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "message": f"Resolve only the journal-issued run reference {reference} using journal_supervisor.observe; evidence and authority come from journal.",
        "name": "Journal supervision admission",
        "agentId": "supervisor",
        "sessionMode": "isolated",
        "deliver": False,
        "thinking": "high",
        "model": "anthropic/claude-sonnet-5",
        "timeoutSeconds": 180,
    }, {
        "Content-Type": "application/json",
        "Idempotency-Key": run.run_id,
    }


class OpenClawHookClient:
    """A private one-agent hook client that only sends a server-issued run reference."""

    def __init__(self, base_url: str, token: str, timeout: int = REQUEST_TIMEOUT_SECONDS):
        self.base_url = JsonHttpConnection.checked_base_url(base_url)
        self.token = bounded_text(token, "hook token", 1, 4096)
        self.timeout = timeout
        self.opener = build_opener(NoRedirectHandler())

    def send(self, run: RunReference) -> HookAcknowledgement:
        payload, headers = hook_request(run)
        headers["Authorization"] = f"Bearer {self.token}"
        request = Request(
            f"{self.base_url}{HOOK_PATH}",
            data=json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(),
            headers=headers,
            method="POST",
        )
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                body = response.read(RESPONSE_MAX_BYTES + 1)
        except HTTPError as error:
            if error.code in {401, 403}:
                raise AuthorizationError("private hook credential was rejected") from None
            if error.code == 429 or error.code >= 500:
                raise RetryableTransportError(f"private hook returned HTTP {error.code}", retryable_cause(error)) from None
            raise TransportError(f"private hook rejected the fixed request with HTTP {error.code}") from None
        except (TimeoutError, URLError, OSError) as error:
            raise RetryableTransportError("private hook request did not complete", retryable_cause(error)) from error
        if len(body) > RESPONSE_MAX_BYTES:
            raise TransportError("private hook response exceeded the byte limit")
        try:
            acknowledgement = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            acknowledgement = {}
        if not isinstance(acknowledgement, dict):
            acknowledgement = {}
        run_id = acknowledgement.get("runId", acknowledgement.get("run_id", ""))
        if not isinstance(run_id, str):
            run_id = ""
        return HookAcknowledgement(run_id[:256])
