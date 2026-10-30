from pathlib import Path
from typing import Self

from journal.config import Config
from journal.sync.certificate_fingerprint import CertificateFingerprint
from journal.sync.team_url import TeamUrl


class HubAccount:
    """An account on a hub reached over TLS, made for one hub's key or, with none, the home hub's: the fingerprint of the hub's root certificate kept beside the account, and the invitation address that carries it."""

    def __init__(self, config: Config) -> None:
        self.config, self.key = config, ""

    @classmethod
    def keyed(cls, config: Config, key: str) -> Self:
        account = cls(config)
        account.key = key
        return account

    def root_path(self) -> Path:
        raise NotImplementedError

    def address(self) -> str:
        raise NotImplementedError

    def fingerprint(self) -> str:
        root = self.root_path()
        return CertificateFingerprint.digest(root.read_text()) if root.is_file() else ""

    def invitation_url(self, code: str) -> str:
        return TeamUrl(self.address()).invitation(code, self.fingerprint())
