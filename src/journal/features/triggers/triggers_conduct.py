from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.message_arrived import MessageArrived
from journal.models.trigger import Trigger
from journal.models.trigger_action import TriggerAction
from journal.features.triggers.triggers_nudges import TriggersNudges
from journal.features.triggers.triggers_part import TriggersPart


class TriggersConduct(Conduct):
    """The triggers feature's conduct in every state: the triggers a prompt, a message or a tool call's input matches are reported as their action names, a nudge or an instruction, and a tool a trigger denies is blocked; a sequence a trigger starts is the listener's, with its first step."""

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.none(*trigger_lines(matching_triggers(event.data.part(TriggersPart).triggers, event.prompt)))

    def on_message_arrived(self, event: MessageArrived, settings: Settings) -> Transition:
        return self.none(*trigger_lines(matching_triggers(event.data.part(TriggersPart).triggers, event.text)))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        rows = matching_triggers(event.data.part(TriggersPart).triggers, event.call.input_text)
        denied = [t for t in rows if t.action == TriggerAction.DENY]
        if denied:
            return self.refuse(TriggersNudges.DENIED.create(title=denied[0].text))
        return self.none(*trigger_lines(rows))


def matching_triggers(triggers: tuple[Trigger, ...], text: str) -> list[Trigger]:
    return [trigger for trigger in triggers if trigger.matches(text)]


def trigger_lines(triggers: list[Trigger]) -> list[Nudge]:
    return [(TriggersNudges.INSTRUCT if trigger.action == TriggerAction.INSTRUCT else TriggersNudges.NUDGE).create(title=trigger.text) for trigger in triggers if trigger.action != TriggerAction.SEQUENCE]
