from journal.events.blocking import Blocking


class SkillReadRecord:
    blocking = Blocking.NEXT_DECISION

    def __init__(self, cards, agents) -> None:
        self.cards, self.agents = cards, agents

    def handle(self, event) -> None:
        self.agents.skill_read(event.session)
        # @sin MarkWrittenOutsideListenerDetector
        # @sin ViewerWriteInBlockingListenerDetector
        self.cards.show(event.environment_id, event.session, "Skill loaded")


class CommitDetection:
    blocking = Blocking.ANSWER

    def __init__(self, processes) -> None:
        self.processes = processes

    def handle(self, event) -> None:
        # @sin MarkWrittenOutsideListenerDetector
        # @sin ViewerWriteInBlockingListenerDetector
        self.processes.show_recent(event.contents)


class SkillLoadedCard:
    def __init__(self, cards) -> None:
        self.cards = cards

    def handle(self, event) -> None:
        # @sin MarkWrittenOutsideListenerDetector
        # @righteous ViewerWriteInBlockingListenerDetector
        self.cards.show(event.environment_id, event.session, "Skill loaded")
