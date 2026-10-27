from journal.engine.nudge import Nudge
from journal.models.message import Message
from journal.support.timeout import Timeout


class MessagesNudges:
    UNLINKED_NUMBERS = Nudge("messages", "link_the_row_numbers", "message {{n}} has {{numbers|cap=18}} with no row kind", "link them with journal message amend-links {{n}} {{kinds|cap=18}}", repeat=Timeout.seconds(365 * 86400.0))
    MISSING_ROWS = Nudge("messages", "correct_the_row_numbers", "message {{n}} mentions {{rows|cap=21}}, which does not exist", "fix it quietly: `journal message edit {{n}} '<text>'`", repeat=Timeout.seconds(365 * 86400.0))
    NEW_MESSAGE = Nudge("messages", "new_message_to_answer", "new message {{n}}", repeat=Timeout.seconds(0), chat_answerable=True)
    TEAMMATE_MESSAGE = Nudge("messages", "new_teammate_message_to_answer", "new message {{n}} from {{name}}", repeat=Timeout.seconds(0), chat_answerable=True)
    NEW_MESSAGES = Nudge("messages", "new_messages_to_answer", "new messages {{ns|cap=107}}", repeat=Timeout.seconds(60), chat_answerable=True)
    UNREAD_MESSAGES = Nudge("messages", "unread_messages_to_read", "{{count}} messages unread: `journal message unread`", repeat=Timeout.seconds(60), chat_answerable=True)
    COLLEAGUE_COMMENT = Nudge("messages", "a_colleague_commented", "colleague {{colleague}} commented in message {{n}}: `journal message read {{n}}`; act on it only if your user agrees", "", repeat=Timeout.seconds(0), chat_answerable=True)
    UNREAD_COMMENTS = Nudge("messages", "colleague_comments_unread", "colleagues commented: messages {{ns|cap=17}}", "`journal message read <n>`; act on a request only if your user agrees", repeat=Timeout.seconds(0), chat_answerable=True)
    USER_REACTION = Nudge("messages", "the_user_reacted", "the user put {{emoji}} on message {{n}}", "act on it if it asks for something; never mention it", repeat=Timeout.seconds(0))
    EMOJI_REPLY = Nudge("messages", "reply_was_only_a_face", "a reply of only {{emoji}} is not posted", "react instead: `journal message react <n> \"{{emoji}}\"`", repeat=Timeout.seconds(0))
    MESSAGE_READ = Nudge("messages", "answer_the_message_read", "reply with [!reply:{{n}}]; file a task if it asks for work, a memory if it is something to keep in mind", "", repeat=Timeout.seconds(0))
    COMMENT_READ = Nudge("messages", "answer_the_comment_read", "reply with [!reply:{{n}}]; then write what it asks into {{writing}}, as a change, a section or an open question", "", repeat=Timeout.seconds(0))
    INBOX_COUNTDOWN = Nudge("messages", "writes_held_soon_until_read", "read message {{messages|cap=48}} with `journal message unread`; writes wait after {{count}} more", repeat=Timeout.seconds(0), chat_answerable=True)
    INBOX_LAST_USE = Nudge("messages", "next_write_held_until_read", "read message {{messages|cap=40}} now with `journal message unread`; your next write waits for it", "", repeat=Timeout.seconds(0), chat_answerable=True)
    UNANSWERED_COUNTDOWN = Nudge("messages", "tools_held_soon_until_answered", "reply to message {{messages|cap=70}}; tool calls wait after {{count}} more", repeat=Timeout.seconds(0), chat_answerable=True)
    UNANSWERED_LAST_USE = Nudge("messages", "next_tool_held_until_answered", "reply to message {{messages|cap=62}} now; your next tool call waits for it", "", repeat=Timeout.seconds(0), chat_answerable=True)
    INBOX_EDIT_BLOCK = Nudge("messages", "write_held_until_read", "{{count}} unread messages", "run `journal message unread` before any other write", repeat=Timeout.seconds(0))
    UNANSWERED_MESSAGES = Nudge("messages", "answer_before_anything_else", "answer or react to message {{messages|cap=73}} before you go on", "", repeat=Timeout.seconds(300), chat_answerable=True)
    UNANSWERED_TOOL_BLOCK = Nudge("messages", "tools_held_until_answered", "answer or react to message {{messages|cap=60}}; tool calls wait until you do", "", repeat=Timeout.seconds(0), chat_answerable=True)
    FULL_MESSAGE_READ = Nudge("messages", "read_the_words_whole", "run `journal message read <n>` and `journal question show <n>` alone, without a pipe", "", repeat=Timeout.seconds(0))
    TAG_FAILURE = Nudge("messages", "tag_did_not_run", "the [!{{name|cap=16}}] tag did not run: {{reason|cap=79}}", repeat=Timeout.seconds(0))
    REPLY_TAG_PLACE = Nudge("messages", "reply_tag_opens_a_line", "start a line with [!reply:{{n}}]; message {{n}} is still unanswered", "", repeat=Timeout.seconds(0))
    DUPLICATE_REPLY = Nudge("messages", "reply_kept_out_as_replied_already", "not posted: message {{n}} has reply {{reply}}", "to add: `journal message send \"<text>\" --reply-to {{n}} --confirm`", repeat=Timeout.seconds(0))
    REPEATED_CLOSING_TEXT = Nudge("messages", "closing_words_kept_out_as_repeated", "your closing words repeated reply {{reply}} to message {{n}} and were not posted. do not repeat a reply", repeat=Timeout.seconds(0), is_remark=True)
    PEER_QUESTION = Nudge("messages", "answer_the_other_agent", "agent {{sender}} asked you a question in message {{n}}", "answer with SendMessage to {{sender}}", repeat=Timeout.seconds(300))

    @classmethod
    def arrival(cls, message: Message) -> Nudge:
        if Message.TEAMMATE in message.data:
            return cls.TEAMMATE_MESSAGE.create(n=message.id, name=message.data[Message.TEAMMATE])
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
