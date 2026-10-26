from enum import StrEnum


class ActorType(StrEnum):
    SYSTEM = "system"
    AGENT = "agent"
    USER = "user"
    PLUGIN = "plugin"
    PHONE = "phone"
    EXTERNAL = "external"
    WORKER = "worker"
    VERIFIER = "verifier"
    REVIEWER = "reviewer"
