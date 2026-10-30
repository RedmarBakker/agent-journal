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

A pin and a button are two different things.

- A pin is a note left on the user's desk: something ready that they must see when they come back hours later, after
  the chat has moved on. Your pull request is ready, your design is ready, the process has finished. Pin it above the
  chat: `journal notice create "<what is ready>" --link "<url>" --label "Open the design"`. It stays until the user
  closes it.
- A button is an action for now: open this page, start this, send this form. It goes under your message
  (`journal message send` with `--button` or `--form-button`, the messages skill) and moves on with the chat.
- Something ready that the user also acts on now gets both: the button in the message, and the pin for when they
  come back.
A document or a report docks itself at the bottom of the chat when it is created, by you or the user, and stays
until the user closes it. Any other row of the journal you want to keep in view, a plan or a task, is docked there with
`journal plan dock 12`, never pinned; only when the user asks for it pinned above the chat, pin it by its ref with
`--link plans:12 --user-asked`, its button opening the row in place. An outside address opens in a new tab.
A link in your chat text or in a command's output that no pin has, a pull request's address among them, is suggested
as a pin, and the same link again only after a number of your tool uses. The user closes a pin when done.

The same goes for what a subagent makes: when you dispatch one to produce something the user will open, tell it
to end its report with the link, and pin that the moment it reports, before you say anything else about its work.
""", keywords=('pin', 'pinned', 'link', 'design'), commands=('notice',))
