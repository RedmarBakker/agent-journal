from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.stop import Stop
from journal.events.agent.prompt_submitted import PromptSubmitted
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.tool_starting import ToolStarting
from journal.features.skills.support.skill_card import SkillCard
from journal.support.option import Option
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from journal.features.skills.feature import Skills


class SkillsConduct(Conduct):
    """The skills feature's conduct in every state: a session starts needing the skills its setting names, those of skills.session_start at a new start and of skills.after_compaction after a compaction, and the state's own; a prompt of the user's that names a skill's keyword must do for that skill, never a journal line, a plugin's or a subagent's notice; while a skill is pending, every tool but a read of it and a journal command is blocked, and so is a stop; a journal command of a noun a skill names is blocked until that skill is read."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return self.none(*read_first(event.data.part(skills_feature()).start_debts(settings.texts(start_option(event)), self.name)))

    def on_prompt_submitted(self, event: PromptSubmitted, settings: Settings) -> Transition:
        return self.none(*read_first(event.data.part(skills_feature()).mentioned(event.users_words())))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        data = event.data.part(skills_feature())
        if event.subagent:
            return self.none()
        if event.call.is_journal:
            unread = data.command_debts(journal_nouns(event))
            return self.refuse(read_first(unread)[0]) if unread else self.none()
        obligations = data.debt_cards()
        if not obligations or is_skill_read(event, obligations):
            return self.none()
        return self.refuse(read_first(obligations)[0])

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        obligations = event.data.part(skills_feature()).skills_due
        return self.refuse(skills_feature().UNREAD_SKILL_STOP.create(skills=" and ".join(obligations))) if obligations else self.none()


def skills_feature() -> "type[Skills]":
    from journal.features.skills.feature import Skills
    return Skills


def start_option(event: SessionStarted) -> Option:
    return skills_feature().COMPACTION_SKILLS if event.is_compaction_start() else skills_feature().START_SKILLS


def journal_nouns(event: ToolStarting) -> set[str]:
    return {part.journal_noun for part in event.call.parts} - {""}


def is_skill_read(event: ToolStarting, cards: list[SkillCard]) -> bool:
    return any(card.name == event.call.skill_loaded or card.path in event.call.command or any(path.endswith(card.path) for path in event.call.read_paths) for card in cards)


def read_first(cards: list[SkillCard]) -> list[Nudge]:
    return [skills_feature().SKILL_READ_REQUEST.create(skill=card.name, path=card.path) for card in cards]
