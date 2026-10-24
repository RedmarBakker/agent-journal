from journal.features.feature import Feature
from journal.features.pins.commands.notice_command import NoticeCommand
from journal.features.pins.listeners.dock_new_writing import DockNewWriting
from journal.features.pins.listeners.docked_row_card import DockedRowCard
from journal.features.pins.pins_conduct import PinsConduct
from journal.features.pins.support.pins_data_reader import PinsDataReader
from journal.features.pins.support.pins_data import PinsData
from journal.support.skill import Skill
from journal.features.pins.pins_part import PinsPart
from journal.features.pins.pins_nudges import PinsNudges
from journal.features.pins.pins_options import PinsOptions


class Pins(Feature[PinsData]):
    name = PinsPart.name
    title = "Pinned links"
    help = "A link the agent gives the user is pinned above the chat, so it is not lost as the chat scrolls; the user closes it when done."
    commands = (NoticeCommand,)
    listeners = (DockNewWriting, DockedRowCard)
    options = (PinsOptions.PIN_SUGGESTION_INTERVAL,)
    data = (PinsDataReader,)
    conduct = (PinsConduct,)

    nudges = (PinsNudges.LINK_PIN_REQUEST, PinsNudges.UNPINNED_CLAIM)

    skill = Skill("pinned-links", 'Load it when you point the user at a design, a page or anything else outside the journal. A link the agent gives the user in the chat is pinned to the chat, so it is not lost as the chat scrolls.', """
# Pinned links

Whenever you point the user at something outside the journal, a design, a hosted page, a document, any link they
will open again, pin it above the chat: `journal notice create "<what it is>" --link "<url>" --label "Open the design"`.
A row of the journal, a document or a plan you want to keep in view, is pinned by its ref, `--link docs:55`, and its
button opens the row in place, as a click on its card does; an outside address opens in a new tab.
A link in your chat text or in a command's output that no pin has, a pull request's address among them, is suggested
as a pin, and the same link again only after a number of your tool uses. The user closes a pin when done.

The same goes for what a subagent makes: when you dispatch one to produce something the user will open, tell it
to end its report with the link, and pin that the moment it reports, before you say anything else about its work.
""", keywords=('pin', 'pinned', 'link', 'design'))
