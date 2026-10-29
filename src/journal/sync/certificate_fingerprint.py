import hashlib
import ssl


class CertificateFingerprint:
    """The SHA-256 fingerprint of a PEM certificate, as an invitation address carries it."""

    @staticmethod
    def digest(certificate: str) -> str:
        return hashlib.sha256(ssl.PEM_cert_to_DER_cert(certificate)).hexdigest()

    @classmethod
    def matches(cls, certificate: str, fingerprint: str) -> bool:
        return cls.digest(certificate) == fingerprint.lower()
