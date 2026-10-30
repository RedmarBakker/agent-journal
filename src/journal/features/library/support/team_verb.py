from argparse import ArgumentParser

TEAM_HELP = "the team it acts on; needed when this journal is connected to several"


class TeamVerb:
    """A verb that reaches a team's server takes the team it acts on with --team, which may be left out with one team connected."""

    @staticmethod
    def added(parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument("--team", default="", help=TEAM_HELP)
        return parser
