class Conduct:
    pass


class Listener:
    pass


class ReplyConduct(Conduct):
    def on_tool_starting(self, event, settings):
        # @sin SessionPurityHookKindComparedDetector
        if event.hook_type == HookType.PRE_TOOL_USE:
            return self.none()
        return self.refuse(event)


class TurnRecord(Listener):
    def handle(self, entries):
        # @sin SessionPurityHookKindComparedDetector
        return [e for e in entries if e.entry_type == events.TOOL_STARTING]


class EntriesQuestion:
    def writes(self, entries):
        # @sin SessionPurityHookKindComparedDetector
        return [e for e in entries if e.entry_type == events.TOOL_STARTING]
