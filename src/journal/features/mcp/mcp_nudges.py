from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class McpNudges:
    SERVER_LOGIN = Nudge("mcp", "sign_in_to_the_server", "sign in to {{server}}", "call mcp__{{name}}__authenticate, then complete_authentication once the browser has returned, and say in the chat that {{server}} is signed in", repeat=Timeout.seconds(0), chat_answerable=True)
