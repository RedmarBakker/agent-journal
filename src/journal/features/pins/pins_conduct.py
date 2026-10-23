import re

from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.turn_displayed import TurnDisplayed
from journal.features.pins.support.pins_data import PinsData
from journal.support.timeout import Timeout

LINK = re.compile(r"https?://[^\s<>()\[\]\"'`]+")
LOCAL_ADDRESS_PATTERN = re.compile(r"^https?://(?:localhost|127\.0\.0\.1)[:/]")
PIN_CLAIM = re.compile(r"\b(pinned|pin it|pinned it)\b", re.IGNORECASE)
CLAIM_WINDOW_SECONDS = 60


class PinsConduct(Conduct):
    """The pins feature's conduct in every state: a link in the agent's text or in a command's output that no pin has is suggested as a pin, once, and again only after so many tool uses; words to the user that a link is pinned, with no pin made in the last minute, are pointed out."""

    def on_turn_displayed(self, event: TurnDisplayed, settings: Settings) -> Transition:
        from journal.features.pins.feature import Pins
        pins = event.data.part(Pins)
        return self.none(*suggestions(event.content, pins), *unmade_pin_claims(event.content, pins, event.time)) if event.final else self.none()

    def on_tool_finished(self, event: ToolFinished, settings: Settings) -> Transition:
        from journal.features.pins.feature import Pins
        pins = event.data.part(Pins)
        return self.none() if event.subagent else self.none(*suggestions(event.output_text, pins), *unmade_pin_claims(event.call.journal_text("message"), pins, event.time))


def unmade_pin_claims(text: str, pins: PinsData, time: float) -> list[Nudge]:
    from journal.features.pins.feature import Pins
    if not PIN_CLAIM.search(text):
        return []
    recent_pin = pins.newest_pin_at is not None and not Timeout.seconds(CLAIM_WINDOW_SECONDS).started(pins.newest_pin_at).is_elapsed(time)
    return [] if recent_pin else [Pins.UNPINNED_CLAIM.create()]


def suggestions(text: str, pins: PinsData) -> list[Nudge]:
    from journal.features.pins.feature import Pins
    loose = [url.rstrip(".,;:") for url in LINK.findall(text) if not LOCAL_ADDRESS_PATTERN.match(url)]
    recent = [url for url in dict.fromkeys(loose) if url.rstrip("/") not in pins.pinned and url.rstrip("/") not in pins.recent_suggestions]
    return [Pins.LINK_PIN_REQUEST.create(url=url) for url in recent]
