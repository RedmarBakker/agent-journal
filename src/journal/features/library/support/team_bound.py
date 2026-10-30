from copy import copy
from typing import Self

from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_link import LibraryLink


class TeamBound:
    """A part that reaches a team's server through one account and its link, the home team's as built; bound gives the same part for another team."""

    account: LibraryAccount
    link: LibraryLink

    def bound(self, account: LibraryAccount) -> Self:
        part = copy(self)
        part.account, part.link = account, self.link.bound(account)
        return part
