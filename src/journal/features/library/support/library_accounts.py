from journal.config import Config
from journal.features.library.support.library_account import LibraryAccount
from journal.support.rejection import Rejection


class LibraryAccounts:
    """Every team this journal is connected to, one account file each in the libraries folder: all of them, one by its key or its name, and the home team, the first joined."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def all(self) -> list[LibraryAccount]:
        return [self.keyed(path.stem) for path in LibraryAccount(self.config).files()]

    def keyed(self, key: str) -> LibraryAccount:
        return LibraryAccount.keyed(self.config, key)

    def names(self) -> list[str]:
        return [account.connection().team for account in self.all()]

    def team(self, name: str) -> LibraryAccount:
        accounts = [account for account in self.all() if account.connection().team == name]
        if not accounts:
            raise Rejection(f"no team called {name} is connected here; the teams are {', '.join(self.names()) or 'none'}")
        return accounts[0]

    def home(self) -> LibraryAccount:
        return self.keyed(LibraryAccount(self.config).path().stem)
