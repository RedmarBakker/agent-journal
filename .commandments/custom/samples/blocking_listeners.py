class SkillReadRecord:
    def __init__(self, cards, agents) -> None:
        self.cards, self.agents = cards, agents

    def handle(self, event) -> None:
        self.agents.skill_read(event.session)
        # @sin MarkWrittenOutsideListenerDetector
        self.cards.show(event.environment_id, event.session, "Skill loaded")


class CommitDetection:
    def __init__(self, processes) -> None:
        self.processes = processes

    def handle(self, event) -> None:
        # @sin MarkWrittenOutsideListenerDetector
        self.processes.show_recent(event.contents)


class SkillLoadedCard:
    def __init__(self, cards) -> None:
        self.cards = cards

    def handle(self, event) -> None:
        # @sin MarkWrittenOutsideListenerDetector
        self.cards.show(event.environment_id, event.session, "Skill loaded")
