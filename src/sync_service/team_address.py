from dataclasses import dataclass


@dataclass(frozen=True)
class TeamAddress:
    """How the journal server says to reach its team server: whether it is in a team, the address, the headers each request carries, the certificate authority to trust, and the header and least number of the protocol an answer must be in."""

    joined: bool
    address: str
    headers: dict[str, str]
    authority: str
    protocol_header: str
    least_protocol: int

    @classmethod
    def parsed(cls, joined: bool, address: str, headers: dict, authority: str, protocol: dict) -> "TeamAddress":
        return cls(joined, address, headers, authority, protocol["header"], protocol["least"])
