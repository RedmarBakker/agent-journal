"""A small stdio and HTTP bridge for the journal supervisor."""

from supervisor_bridge.bridge import SupervisorBridge
from supervisor_bridge.contracts import RunReference

__all__ = ["RunReference", "SupervisorBridge"]
