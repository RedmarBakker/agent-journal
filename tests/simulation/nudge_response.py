import re
import shlex

SPOKEN_ACTIONS = {
    "builder_write_next": "write",
    "builder_clear_oldest": "merge",
    "orchestrator_clear_oldest": "merge",
    "builder_take_in_first": "merge",
    "orchestrator_check_worker": "merge",
    "orchestrator_hand_out": "dispatch",
    "orchestrator_fill_place": "dispatch",
    "orchestrator_queue_more": "dispatch",
    "solo_answer": "answer",
    "load_rising": "merge",
    "load_critical": "merge",
    "builder_load_over_ceiling": "merge",
}
REPLY_FEATURE = "messages"
NAMED_ROWS = {"merge": re.compile(r"worker (\d+)"), "dispatch": re.compile(r"task (\d+)"), "answer": re.compile(r"message (\d+)")}
REMEDY = re.compile(r"`journal ([^`<>]+)`")


class NudgeResponse:
    """The action the simulated main agent takes for a line it is told, by the line's key: each measure's line names one action (the measures design, section 5), any line of the messages feature asks for a reply, the row a line names (its worker, task or message) is the one acted on, a refusal's remedy is the journal command it names, and every other line asks for nothing."""

    @staticmethod
    def action(key: str) -> str:
        feature, _, name = key.partition(".")
        return "answer" if feature == REPLY_FEATURE else SPOKEN_ACTIONS.get(name, "")

    @staticmethod
    def named_row(action: str, line: str) -> int:
        found = NAMED_ROWS[action].search(line) if action in NAMED_ROWS else None
        return int(found.group(1)) if found else 0

    @staticmethod
    def remedy(line: str) -> list[str]:
        found = REMEDY.search(line)
        return shlex.split(found.group(1)) if found else []
