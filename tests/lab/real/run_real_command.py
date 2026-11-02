import json
import math
import os
from pathlib import Path
import stat
import time
from typing import Callable

from journal.support.actor import Actor
from tests.lab.real.approval_receipt import ApprovalReceipt
from tests.lab.real.batch_approval import BatchApproval
from tests.lab.real.manifest import Manifest
from tests.lab.real.run_real_batch import RunRealBatch


def execute(manifest_path: Path, receipt_path: Path, key_path: Path, runner_specification: str,
            resolve_runner: Callable[[str], Callable]) -> tuple[int, tuple[Path, ...]]:
    manifest = read_manifest(manifest_path)
    receipt = read_receipt(receipt_path)
    key = read_key(key_path)
    approvals = BatchApproval(receipt.owner_id, key)
    data = manifest.data()
    for run_id in approvals.run_ids(data):
        approvals.verify(manifest, receipt, run_id, Actor.user(receipt.owner_id), time.time())
    runner_factory = resolve_runner(runner_specification)
    service = runner_factory(manifest, approvals, manifest_path.parent)
    if not isinstance(service, RunRealBatch):
        raise ValueError("the real-run adapter must return a RunRealBatch")
    service.approvals = approvals
    records = service.run(manifest, receipt, Actor.user(receipt.owner_id))
    paths = tuple(service.record_path(manifest.batch_id, record.run_id)
                  for record in records)
    return (1 if any(record.terminal_reason != "completed" for record in records) else 0), paths


def read_manifest(path: Path) -> Manifest:
    document = read_private_document(path, "manifest")
    batch_id = document.pop("batch_id", None)
    if not isinstance(batch_id, str):
        raise ValueError("approved manifest must name its batch id")
    return Manifest.build(batch_id, document)


def read_receipt(path: Path) -> ApprovalReceipt:
    document = read_private_document(path, "owner receipt")
    fields = {"batch_id", "manifest_digest", "run_ids", "resources_digest", "providers_digest",
              "expires_at", "owner_id", "signature"}
    if set(document) != fields:
        raise ValueError("owner receipt does not match the approval schema")
    run_ids = document["run_ids"]
    if not isinstance(run_ids, list) or any(not isinstance(run_id, str) for run_id in run_ids):
        raise ValueError("owner receipt run ids must be a list of strings")
    text_fields = ("batch_id", "manifest_digest", "resources_digest", "providers_digest", "signature")
    if any(not isinstance(document[key], str) or not document[key] for key in text_fields):
        raise ValueError("owner receipt text fields must be non-empty strings")
    if type(document["owner_id"]) is not int or document["owner_id"] <= 0:
        raise ValueError("owner receipt must name its authenticated owner")
    if type(document["expires_at"]) not in (int, float) or not math.isfinite(document["expires_at"]):
        raise ValueError("owner receipt expiry must be a timestamp")
    return ApprovalReceipt(**{**document, "run_ids": tuple(run_ids)})


def read_key(path: Path) -> bytes:
    if not path.is_absolute() or any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("owner signing key must be a private absolute regular file")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError("owner signing key must be a private absolute regular file")
        key = os.read(descriptor, 4097)
    finally:
        os.close(descriptor)
    if len(key) < 32:
        raise ValueError("owner signing key must contain at least 32 bytes")
    if len(key) > 4096:
        raise ValueError("owner signing key is larger than the accepted key size")
    return key


def read_private_document(path: Path, name: str) -> dict:
    if not path.is_absolute() or any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError(f"{name} must be a private absolute regular file")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError(f"{name} must be a private absolute regular file")
        with os.fdopen(descriptor, "r", encoding="utf-8") as source:
            descriptor = -1
            document = json.load(source)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if not isinstance(document, dict):
        raise ValueError(f"{name} must be a JSON object")
    return document
