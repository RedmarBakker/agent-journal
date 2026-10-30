class HookReading:
    """A sample for raw-event-name: a hook named by its raw name, and one named by its type."""

    def is_start(self, hook_name: str) -> bool:
        # @sin RawEventNameDetector
        return hook_name == "SessionStart"

    def is_start_type(self, hook_type, start_type) -> bool:
        return hook_type == start_type
