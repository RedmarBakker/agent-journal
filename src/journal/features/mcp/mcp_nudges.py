from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class McpNudges:
    SERVER_LOGIN = Nudge("mcp", "sign_in_to_the_server", "sign in to {{server}}: `mcp__{{name|cap=23}}__authenticate`, then `complete_authentication`; tell the user", "", repeat=Timeout.seconds(0), chat_answerable=True)
