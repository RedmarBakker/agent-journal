from journal.support.option import USER, Option


class MessagesOptions:
    ANSWER_REQUEST_LIMIT = Option("messages.nudge_after", "Ask for an answer after", "Tool uses the agent may make after reading a message before it is told the message is still unanswered", 5, unit="tool uses", setter=USER)
    TOOL_BLOCK_LIMIT = Option("messages.hold_after", "Hold every tool after", "Tool uses the agent may make after reading a message before its tools wait for the answer; 0 holds the first", 10, unit="tool uses", setter=USER)
    TRANSCRIPT_SCAN_DELAY = Option("messages.sweep_after", "Look for missed words older than", "Seconds the hooks have to bring the agent's words to the chat before the transcript is looked through for any they missed", 10, unit="seconds", setter=USER)
    EDIT_BLOCK_LIMIT = Option("messages.hold_after_unread", "Hold the write after", "Tool uses the agent may make after a message arrives, each told how many are left, before its next write waits until it reads the message", 5, unit="tool uses", setter=USER)
