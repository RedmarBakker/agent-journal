from journal.engine.nudge import Nudge
from journal.engine.nudge_kind import NudgeKind


def test_a_nudge_is_an_instruction_by_default_and_a_remark_keeps_its_kind_once_made():
    instruction = Nudge("tasks", "carry_on", "{{name}} is in hand")
    remark = Nudge("etiquette", "no_em_dashes", "no em dashes in {{place}}", kind=NudgeKind.REMARK)
    assert instruction.kind is NudgeKind.INSTRUCTION and not instruction.kind.is_remark()
    assert remark.create(place="the chat").kind.is_remark(), "a nudge made with its values keeps its kind"
    assert remark.create(place="the chat").rendered() == "no em dashes in the chat", "the kind never changes the words"
