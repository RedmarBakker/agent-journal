class Receiver:
    def receive(self, hook):
        # @sin AssignmentInConditionDetector
        if hook_entries := self.entries.keyed(hook.key()):
            return self.replayed(hook_entries[0])
        return None

    def answered(self, hook):
        # @righteous AssignmentInConditionDetector
        if self.is_resent(hook):
            return self.resent_answer(hook)
        return None
