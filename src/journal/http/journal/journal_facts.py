from dataclasses import dataclass


@dataclass(frozen=True)
class JournalFacts:
    """What the viewer boots from: the project, the environment it opens on, the version and build, every feature with its options in the groups the settings page shows, and every kind of chat mark in its group, which Show in chat is built from."""

    project: str
    environment: str
    version: str
    build: str
    features: list
    groups: list
    marks: dict
