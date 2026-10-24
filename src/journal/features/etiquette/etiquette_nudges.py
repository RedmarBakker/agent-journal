from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class EtiquetteNudges:
    SHOP_TALK_WARNING = Nudge("etiquette", "no_shop_talk", "your message talks about the journal's commands", "talk about the work", repeat=Timeout.seconds(600), is_remark=True)
    SECOND_PERSON = Nudge("etiquette", "say_you_not_the_user", "in the chat you are speaking to the user", "say you, never the user", repeat=Timeout.seconds(600), is_remark=True)
    EM_DASH_WARNING = Nudge("etiquette", "no_em_dashes", "your chat used em dashes", "use a full stop instead", repeat=Timeout.seconds(600), is_remark=True)
    PARAGRAPH_SPACING = Nudge("etiquette", "blank_lines_between_paragraphs", "your last message had no blank lines between paragraphs", repeat=Timeout.seconds(600), is_remark=True)
    JOURNAL_LINE_RULE = Nudge("etiquette", "a_line_is_an_instruction", "a [journal] line is an instruction, not a message", "act on it; never answer or mention it in the chat", repeat=Timeout.seconds(1800), is_remark=True)
    PLAIN_CODE = Nudge("etiquette", "plain_words_in_code", "names and text in code are plain words", "say literally what a thing is or does, never in the voice", repeat=Timeout.seconds(0))
