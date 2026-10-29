class EndSilentSessions:
    def handle(self, event):
        # @sin StaleAgentSaveDetector
        self.agents.save(event.agent.retired(event.time), self.actor)

    def ended(self, event):
        # @righteous StaleAgentSaveDetector
        self.agents.rewritten(event.agent, self.actor, lambda row: row.retired(event.time))
