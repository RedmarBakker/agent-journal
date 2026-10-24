import sys
from pathlib import Path

from sync_service.carrier import Carrier
from sync_service.event_inbox import EventInbox
from sync_service.journal_doors import JournalDoors


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python3 -m sync_service <the journal's project folder>", file=sys.stderr)
        return 2
    carrier = Carrier(JournalDoors(Path(argv[0])))
    inbox = EventInbox(carrier)
    inbox.start()
    carrier.run(inbox.address)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
