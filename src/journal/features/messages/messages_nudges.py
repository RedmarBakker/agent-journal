from journal.engine.nudge import Nudge
from journal.engine.nudge_kind import NudgeKind
from journal.models.message import Message
from journal.support.timeout import Timeout

REPLY_COMMAND_SPAN_USES = 50
MESSAGE_REPLY = "`journal message send '<text>' --reply-to <n>`"


class MessagesNudges:
    UNLINKED_NUMBERS = Nudge("messages", "link_the_row_numbers", "message {{n}} has {{numbers|cap=18}} with no row kind", "link them with journal message amend-links {{n}} {{kinds|cap=18}}", repeat=Timeout.seconds(365 * 86400.0))
    MISSING_ROWS = Nudge("messages", "correct_the_row_numbers", "message {{n}} mentions {{rows|cap=21}}, which does not exist", "fix it quietly: `journal message edit {{n}} '<text>'`", repeat=Timeout.seconds(365 * 86400.0), kind=NudgeKind.REMARK)
    NEW_MESSAGE = Nudge("messages", "new_message_to_answer", "new message {{n}}", repeat=Timeout.seconds(0), chat_answerable=True)
    AGENT_MESSAGE = Nudge("messages", "new_agent_message_to_answer", "new message {{n}} from {{name}}", repeat=Timeout.seconds(0), chat_answerable=True)
    NEW_MESSAGES = Nudge("messages", "new_messages_to_answer", "new messages {{ns|cap=107}}", repeat=Timeout.seconds(60), chat_answerable=True)
    UNREAD_MESSAGES = Nudge("messages", "unread_messages_to_read", "{{count}} messages unread: `journal message unread`", repeat=Timeout.seconds(60), chat_answerable=True)
    USER_REACTION = Nudge("messages", "the_user_reacted", "the user put {{emoji}} on message {{n}}", "act on it if it asks for something; never mention it", repeat=Timeout.seconds(0))
    EMOJI_REPLY = Nudge("messages", "reply_was_only_a_face", "a reply of only {{emoji}} is not posted", "react instead: `journal message react <n> \"{{emoji}}\"`", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    MESSAGE_READ = Nudge("messages", "answer_the_message_read", "answer message {{n}}: reply, file a task if it asks for work, follow it if it steers, or keep it as a memory", "", repeat=Timeout.seconds(0))
    REPLY_COMMAND = Nudge("messages", "reply_by_command", "reply with `journal message send '<text>' --reply-to <n>`, then go on in the same turn", "", repeat=Timeout.tool_uses(REPLY_COMMAND_SPAN_USES))
    COMMENT_READ = Nudge("messages", "answer_the_comment_read", "reply with `journal message send '<text>' --reply-to {{n}}`, then write what it asks into {{writing}}", "", repeat=Timeout.seconds(0))
    INBOX_COUNTDOWN = Nudge("messages", "writes_held_soon_until_read", "read message {{messages|cap=48}} with `journal message unread`; writes wait after {{count}} more", repeat=Timeout.seconds(0), chat_answerable=True)
    INBOX_LAST_USE = Nudge("messages", "next_write_held_until_read", "read message {{messages|cap=40}} now with `journal message unread`; your next write waits for it", "", repeat=Timeout.seconds(0), chat_answerable=True)
    UNANSWERED_COUNTDOWN = Nudge("messages", "tools_held_soon_until_answered", "run " + MESSAGE_REPLY + " to reply to message {{messages|cap=18}}; tools wait after {{count}} more", repeat=Timeout.seconds(0), chat_answerable=True)
    UNANSWERED_LAST_USE = Nudge("messages", "next_tool_held_until_answered", "run " + MESSAGE_REPLY + " to reply to message {{messages|cap=18}}; next tool waits", "", repeat=Timeout.seconds(0), chat_answerable=True)
    INBOX_EDIT_BLOCK = Nudge("messages", "write_held_until_read", "{{count}} unread messages", "run `journal message unread` before any other write", repeat=Timeout.seconds(0))
    UNANSWERED_MESSAGES = Nudge("messages", "answer_before_anything_else", "run " + MESSAGE_REPLY + " to reply to message {{messages|cap=18}} before going on", "", repeat=Timeout.seconds(300), chat_answerable=True)
    UNANSWERED_TOOL_BLOCK = Nudge("messages", "tools_held_until_answered", "run " + MESSAGE_REPLY + " to reply to message {{messages|cap=18}}", "tool calls wait until you do", repeat=Timeout.seconds(0), chat_answerable=True)
    FULL_MESSAGE_READ = Nudge("messages", "read_the_words_whole", "run `journal message read <n>` and `journal question show <n>` alone, without a pipe", "", repeat=Timeout.seconds(0))
    RETIRED_TAGS = Nudge("messages", "tags_run_nothing", "tags run nothing any more", "reply with `journal message send '<text>' --reply-to <n>`, act by command", repeat=Timeout.minutes(60), kind=NudgeKind.REMARK)
    REPLY_REPEAT_WARNING = Nudge("messages", "reply_in_the_chat", "message {{n}} answered: reply {{reply}}", "go on; closing text is not sent", repeat=Timeout.seconds(0), kind=NudgeKind.REMARK)
    REPLY_CLOSING_WORDS = Nudge("messages", "closing_words_after_a_reply", "words after reply {{reply}} were not sent", "end a turn that replied by command with the reply", repeat=Timeout.seconds(86400), kind=NudgeKind.REMARK)
    PEER_QUESTION = Nudge("messages", "answer_the_other_agent", "agent {{sender}} asked you a question in message {{n}}", "answer with SendMessage to {{sender}}", repeat=Timeout.seconds(300))

    @classmethod
    def arrival(cls, message: Message) -> Nudge:
        if message.is_agent_word:
            return cls.AGENT_MESSAGE.create(n=message.id, name=message.sender)
        return cls.NEW_MESSAGE.create(n=message.id)

    @classmethod
    def inbox(cls, unread: tuple[int, ...], count: int) -> Nudge:
        if count == 1:
            return cls.NEW_MESSAGE.create(n=unread[0])
        if count <= 3:
            return cls.NEW_MESSAGES.create(ns=", ".join(str(n) for n in unread))
        return cls.UNREAD_MESSAGES.create(count=count)

    @classmethod
    def inbox_lines(cls) -> tuple[Nudge, ...]:
        return (cls.NEW_MESSAGE, cls.NEW_MESSAGES, cls.UNREAD_MESSAGES)

    @classmethod
    def inbox_countdown(cls, unread: tuple[int, ...], remaining_uses: int) -> Nudge:
        numbers = ", ".join(str(n) for n in unread)
        return cls.INBOX_COUNTDOWN.create(count=remaining_uses, messages=numbers) if remaining_uses else cls.INBOX_LAST_USE.create(messages=numbers)

    @classmethod
    def unanswered_countdown(cls, unanswered: tuple[int, ...], remaining_uses: int) -> Nudge:
        numbers = ", ".join(str(n) for n in unanswered)
        return cls.UNANSWERED_COUNTDOWN.create(count=remaining_uses, messages=numbers) if remaining_uses else cls.UNANSWERED_LAST_USE.create(messages=numbers)
