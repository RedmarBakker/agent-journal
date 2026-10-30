import argparse
import sys
import time
from pathlib import Path

from sync_server.db.store import Store
from sync_server.team_server import BACKUPS, DATABASE, FILES, TeamServer
from sync_server.item_file_place import ITEMS_FOLDER
from sync_server.old_row_files import OldRowFiles
from sync_server.server_backups import ServerBackups



def serve(arguments: argparse.Namespace) -> None:
    for folder in OldRowFiles(arguments.data / FILES, arguments.data / BACKUPS).moved():
        print(f"moved the row sync's old files to {folder}", flush=True)
    team = TeamServer(arguments.data)
    if team.accounts.is_empty():
        print(f"this team server has no admin yet: claim it from your journal with journal team connect https://<this server's address>/setup?code={team.setup_code.current()}", flush=True)
    team.http(arguments.host, arguments.port).serve_forever()


def backups(data: Path) -> ServerBackups:
    return ServerBackups(Store(data / DATABASE), data / BACKUPS, data / FILES / ITEMS_FOLDER)


def backup(arguments: argparse.Namespace) -> None:
    print(backups(arguments.data).copied(arguments.to or arguments.data / BACKUPS / time.strftime("team-%Y%m%d-%H%M%S.db")))


def restore(arguments: argparse.Namespace) -> None:
    if not arguments.source.is_file():
        print(f"no backup at {arguments.source}", file=sys.stderr)
        sys.exit(1)
    backups(arguments.data).restored(arguments.source)
    print(f"restored {arguments.source} into {arguments.data / DATABASE}, with the library's files kept beside it")


def setup_code(arguments: argparse.Namespace) -> None:
    team = TeamServer(arguments.data)
    if not team.accounts.is_empty():
        print("this team server has its admin already, so it has no setup code: connect with your account, or with an invitation an admin shares")
        return
    print(team.setup_code.current())


VERBS = {"serve": serve, "backup": backup, "restore": restore, "setup-code": setup_code}


def main() -> None:
    parser = argparse.ArgumentParser(prog="sync_server", description="the team server of a library: its accounts and its items")
    verbs = parser.add_subparsers(dest="verb", required=True)
    serving = verbs.add_parser("serve", help="answer the team's journals; its own migrations run first, so a new image upgrades the database at its first start")
    serving.add_argument("--host", default="127.0.0.1")
    serving.add_argument("--port", type=int, default=8470)
    backing = verbs.add_parser("backup", help="copy the database while the server runs, with SQLite's online backup, into the data folder's backups or --to")
    backing.add_argument("--to", type=Path)
    restoring = verbs.add_parser("restore", help="put a backup in place of the database; run it while no server runs on the data folder")
    restoring.add_argument("--from", dest="source", type=Path, required=True)
    verbs.add_parser("setup-code", help="print the code that claims this server while it has no admin, for the person with a shell on its machine")
    for verb in verbs.choices.values():
        verb.add_argument("--data", type=Path, required=True, help="the folder its database lives in")
    arguments = parser.parse_args()
    arguments.data.mkdir(parents=True, exist_ok=True)
    VERBS[arguments.verb](arguments)


main()
