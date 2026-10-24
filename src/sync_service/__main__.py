import sys
from pathlib import Path

from sync_service.carrier import Carrier
from sync_service.event_inbox import EventInbox
from sync_service.journal_doors import JournalDoors


def main(argv: list[str]) -> int:
    if len(argv) not in (1, 2) or (len(argv) == 2 and not argv[1].isdigit()):
        print("usage: python3 -m sync_service <the journal's project folder> [the loopback port it listens on]", file=sys.stderr)
        return 2
    carrier = Carrier(JournalDoors(Path(argv[0])))
    inbox = EventInbox(carrier, int(argv[1]) if argv[1:] else 0)
    inbox.start()
    carrier.run(inbox.address)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
