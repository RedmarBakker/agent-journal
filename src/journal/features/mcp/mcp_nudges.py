from journal.engine.nudge import Nudge


class McpNudges:
    SERVER_LOGIN = Nudge("mcp", "sign_in_to_the_server", "sign in to {{title}}", "call mcp__{{name}}__authenticate, then complete_authentication once the browser has returned, and say in the chat that {{title}} is signed in", repeat_interval=0, chat_answerable=True)
