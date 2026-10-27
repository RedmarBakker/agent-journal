from journal.features.feature import Feature
from journal.features.library.commands.library_command import LibraryCommand


class LibraryFeature(Feature):
    name = "library"
    title = "Library"
    help = "The team's library: sequences, templates, profiles and more, published once and imported by anyone on the team."
    commands = (LibraryCommand,)
