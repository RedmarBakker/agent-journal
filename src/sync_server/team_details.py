import re

from sync_server.change_log import ChangeLog
from sync_server.db.team_detail_rows import TeamDetailRows
from sync_server.protocol import UNVERSIONED
from sync_server.refusal import Refusal
from sync_server.accounts import Accounts
from sync_server.team_summary import TeamSummary

REPOSITORY = "repository"
VERSION = "version"
MIGRATION = "migration"
LOWEST_SEQUENCE = "lowest_sequence"
VERSIONS = "versions"
KEY = "key"
NAME = "name"
NUMBER = "number"
HUB = "hub"
REPOSITORY_TIE = "repository_tie"
UNTIED = "untied"
ON_HUB = "on"
EXACT = "exact"
ANY = "any"
VERSION_SHAPE = re.compile(r"\d+\.\d+\.\d+")


class TeamDetails:
    """What the team server knows of the journal it hosts: the first commit of its repository, which a joining checkout must share, the journal version the team is pinned to, which the first copy's journal sets and an admin moves, and the migration the team's rows are at, which the first copy sets: a journal on an older migration may neither push nor pull until it is upgraded; the lowest sequence a pull may go on from, below which a device takes the full copy; and whether a journal must run exactly the pinned version to push or pull, the default, or any version will do, as the admin sets it; and the team's key and number T, both drawn when the server is made, T read as 0 for a team from before them, which stores none, and its name, which its first journal gives it; and whether the team is on the hub, as a team made since is and one from before is once it has been moved there, whose journals send the team only the rows that belong to it; and whether the team is tied to its repository, so a journal of another checkout is refused, as a team is unless it was made with --any-repository or its admin untied it."""

    def __init__(self, rows: TeamDetailRows, log: ChangeLog, accounts: Accounts) -> None:
        self.rows, self.log, self.accounts = rows, log, accounts

    def record_repository(self, repository: str) -> None:
        self.rows.write(REPOSITORY, repository)

    def record_version(self, version: str) -> None:
        if not VERSION_SHAPE.fullmatch(version):
            raise Refusal(f"{version} is not a journal version such as 4.20.0")
        self.rows.write(VERSION, version)
        self.log.wake()

    def record_name(self, name: str) -> None:
        self.rows.write(NAME, name)

    def record_migration(self, number: int) -> None:
        self.rows.write(MIGRATION, str(number))

    def require_migration(self, number: int) -> None:
        team = self.migration()
        if number < team:
            raise Refusal(f"this journal is on migration {number} and the team on {team}: upgrade it to version {self.version()} with journal update apply; its changes wait here until then")

    def record_lowest_sequence(self, sequence: int) -> None:
        self.rows.write(LOWEST_SEQUENCE, str(sequence))

    def lowest_sequence(self) -> int:
        return int(self.rows.value(LOWEST_SEQUENCE) or UNVERSIONED)

    def migration(self) -> int:
        return int(self.rows.value(MIGRATION) or UNVERSIONED)

    def record_versions(self, rule: str) -> None:
        if rule not in (EXACT, ANY):
            raise Refusal(f"versions is {EXACT} or {ANY}, not {rule}")
        self.rows.write(VERSIONS, rule)

    def versions(self) -> str:
        return self.rows.value(VERSIONS) or EXACT

    def require_version(self, version: str) -> None:
        pinned = self.version()
        if pinned and self.versions() == EXACT and version != pinned:
            raise Refusal(f"this journal runs {version or 'an unnamed version'} and the team {pinned}: install {pinned} with journal update apply; its changes wait here until then")

    def version(self) -> str:
        return self.rows.value(VERSION)

    def is_tied_to_repository(self) -> bool:
        return self.rows.value(REPOSITORY_TIE) != UNTIED

    def record_repository_tie(self, tied: bool) -> None:
        self.rows.write(REPOSITORY_TIE, "tied" if tied else UNTIED)

    def is_on_hub(self) -> bool:
        return self.rows.value(HUB) == ON_HUB

    def record_on_hub(self) -> None:
        self.rows.write(HUB, ON_HUB)

    def number(self) -> int:
        return int(self.rows.value(NUMBER) or UNVERSIONED)

    def answer(self) -> TeamSummary:
        return TeamSummary(self.rows.value(REPOSITORY), self.log.head() > 0, self.version(), self.migration(), self.versions(), not self.accounts.is_empty(), self.rows.value(KEY), self.rows.value(NAME), self.number(), self.is_on_hub(), self.is_tied_to_repository())
