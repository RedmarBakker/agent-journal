from datetime import datetime, timezone

from journal.events.clock_ticked import ClockTicked
from journal.events.listener import Listener
from journal.features.sharing.support.tunnel import Tunnel
from journal.support.time_source import TimeSource


class TunnelSettlement(Listener[ClockTicked]):
    """As the clock ticks, the tunnel is reconciled again when what keeps it open has changed, so it closes once a pairing code or a phone's days run out."""

    def __init__(self, tunnel: Tunnel, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.tunnel = tunnel

    def handle(self, event: ClockTicked) -> None:
        self.tunnel.reconcile_changes(self.time_source.moment())
