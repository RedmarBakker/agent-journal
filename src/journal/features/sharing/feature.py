from journal.features.feature import Feature
from journal.features.sharing.commands.share_command import ShareCommand
from journal.features.sharing.seeds.tunnel_seed import TunnelSeed
from journal.features.sharing.sharing_options import SharingOptions


class Sharing(Feature):
    name = "sharing"
    title = "Share links"
    help = "Share one document, report or plan with someone outside the journal. The link opens that item and nothing else, and reaches this journal through a tunler tunnel."
    options = (SharingOptions.HOST,)
    seeds = (TunnelSeed,)
    commands = (ShareCommand,)
