import hashlib
import hmac
import json
import math
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Mapping

from journal.support.actor import Actor
from journal.support.actor_type import ActorType
from tests.lab.real.approval_receipt import ApprovalReceipt
from tests.lab.real.manifest import Manifest
from tests.lab.real.run_caps import BATCH_LIMITS, RUN_LIMITS, RunCaps


class BatchApproval:
    """Sign and verify owner-approved batches without relying on agent environment markers."""

    def __init__(self, owner_id: int, signing_key: bytes) -> None:
        if type(owner_id) is not int or owner_id <= 0 or not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise ValueError("batch approval needs an owner id and a 256-bit signing key")
        self.owner_id, self.signing_key = owner_id, signing_key

    def approve(self, manifest: Manifest, actor: Actor, expires_at: float, now: float) -> ApprovalReceipt:
        if actor.actor_type is not ActorType.USER or actor.id != str(self.owner_id):
            raise ValueError("only the authenticated owner may approve a real batch")
        if type(expires_at) not in (int, float) or type(now) not in (int, float) or not math.isfinite(expires_at) or not math.isfinite(now) or expires_at <= now:
            raise ValueError("batch approval must have a future expiry")
        data = manifest.data()
        run_ids = self.run_ids(data)
        self.validate_caps(data)
        resources = data["batch_caps"]
        approved_until = resources.get("approval_valid_until")
        if type(approved_until) not in (int, float) or not math.isfinite(float(approved_until)) or expires_at > approved_until:
            raise ValueError("approval expiry must fit the owner-selected approval window")
        providers = data["providers"]
        resources_digest = self.digest(resources)
        providers_digest = self.digest(providers)
        payload = self.payload(manifest.batch_id, manifest.digest, run_ids, resources_digest, providers_digest, expires_at, self.owner_id)
        signature = hmac.new(self.signing_key, payload, hashlib.sha256).hexdigest()
        return ApprovalReceipt(manifest.batch_id, manifest.digest, run_ids, resources_digest, providers_digest, expires_at, self.owner_id, signature)

    @staticmethod
    def save(receipt: ApprovalReceipt, path: Path) -> None:
        if not path.is_absolute() or any(part.is_symlink() for part in (path, *path.parents)):
            raise ValueError("approval receipt must be written to a private absolute path")
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if path.parent.stat().st_mode & 0o077:
            raise ValueError("approval receipt directory must be private to its owner")
        descriptor, name = tempfile.mkstemp(prefix=".approval-", dir=path.parent)
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as target:
                json.dump(asdict(receipt), target, sort_keys=True, separators=(",", ":"), allow_nan=False)
                target.flush()
                os.fsync(target.fileno())
            os.replace(name, path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def verify(self, manifest: Manifest, receipt: ApprovalReceipt, run_id: str, actor: Actor, now: float) -> None:
        if actor.actor_type is not ActorType.USER or actor.id != str(self.owner_id):
            raise ValueError("only the authenticated owner may start an approved real batch")
        data = manifest.data()
        run_ids = self.run_ids(data)
        if receipt.batch_id != manifest.batch_id or receipt.manifest_digest != manifest.digest or receipt.run_ids != run_ids:
            raise ValueError("batch approval does not match the immutable manifest")
        if run_id not in run_ids:
            raise ValueError("run id is outside the approved batch")
        if receipt.owner_id != self.owner_id or receipt.expires_at <= now:
            raise ValueError("batch approval is expired or belongs to another owner")
        if receipt.resources_digest != self.digest(data["batch_caps"]) or receipt.providers_digest != self.digest(data["providers"]):
            raise ValueError("approved resources or providers changed")
        payload = self.payload(receipt.batch_id, receipt.manifest_digest, receipt.run_ids, receipt.resources_digest,
                               receipt.providers_digest, receipt.expires_at, receipt.owner_id)
        expected = hmac.new(self.signing_key, payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(receipt.signature, expected):
            raise ValueError("batch approval signature is invalid")

    @staticmethod
    def run_ids(data: Mapping[str, object]) -> tuple[str, ...]:
        run_ids = data.get("run_ids")
        if not isinstance(run_ids, list) or not run_ids or any(not isinstance(item, str) or not item for item in run_ids):
            raise ValueError("batch manifest needs explicit run ids")
        if len(set(run_ids)) != len(run_ids):
            raise ValueError("batch manifest run ids must be unique")
        runs = data.get("runs")
        if not isinstance(runs, list) or any(not isinstance(item, Mapping) for item in runs):
            raise ValueError("each approved run needs a manifest object")
        if tuple(item.get("id") for item in runs) != tuple(run_ids):
            raise ValueError("run ids must match the ordered run manifests")
        return tuple(run_ids)

    @staticmethod
    def validate_caps(data: Mapping[str, object]) -> None:
        run_caps, batch_caps = data.get("run_caps"), data.get("batch_caps")
        if not isinstance(run_caps, Mapping) or not isinstance(batch_caps, Mapping):
            raise ValueError("batch manifest needs explicit run and batch caps")
        if set(run_caps) != set(BatchApproval.run_ids(data)):
            raise ValueError("each approved run needs exactly one cap set")
        for caps in run_caps.values():
            if not isinstance(caps, Mapping):
                raise ValueError("each run needs its own selected caps")
            RunCaps.validate(caps, RUN_LIMITS)
            RunCaps.validate_cost_cap(caps)
        RunCaps.validate(batch_caps, BATCH_LIMITS)
        RunCaps.validate_cost_cap(batch_caps, "batch_max_usd")

    @staticmethod
    def digest(value: object) -> str:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @staticmethod
    def payload(batch_id: str, manifest_digest: str, run_ids: tuple[str, ...], resources_digest: str,
                providers_digest: str, expires_at: float, owner_id: int) -> bytes:
        document = {"batch_id": batch_id, "manifest_digest": manifest_digest, "run_ids": run_ids,
                    "resources_digest": resources_digest, "providers_digest": providers_digest,
                    "expires_at": expires_at, "owner_id": owner_id}
        return json.dumps(document, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
