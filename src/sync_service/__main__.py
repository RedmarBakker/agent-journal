import sys
from pathlib import Path

from sync_service.carrier import Carrier
from sync_service.event_inbox import EventInbox
from sync_service.journal_doors import JournalDoors
from sync_service.team_carriers import TeamCarriers


def main(argv: list[str]) -> int:
    if len(argv) > 2 or (len(argv) == 2 and not argv[1].isdigit()):
        print("usage: python3 -m sync_service [the journal's project folder, else the working folder] [the loopback port it listens on]", file=sys.stderr)
        return 2
    doors = JournalDoors(Path(argv[0]) if argv else Path.cwd())
    carrier = Carrier(doors)
    inbox = EventInbox(carrier, int(argv[1]) if argv[1:] else 0)
    inbox.start()
    TeamCarriers(doors).started()
    carrier.run(inbox.address)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
