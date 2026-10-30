from dataclasses import dataclass


@dataclass(frozen=True)
class ApprovalReceipt:
    """The owner signature binding a batch approval to its manifest and expiry."""

    batch_id: str
    manifest_digest: str
    run_ids: tuple[str, ...]
    resources_digest: str
    providers_digest: str
    expires_at: float
    owner_id: int
    signature: str
