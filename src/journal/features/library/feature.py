from journal.features.feature import Feature
from journal.features.library.commands.library_command import LibraryCommand
from journal.features.library.commands.team_command import TeamCommand


class LibraryFeature(Feature):
    name = "library"
    title = "Library"
    help = "The team's library: the sequences, templates, profiles and more that the team shares, published once and imported by anyone on the team."
    commands = (TeamCommand, LibraryCommand)
