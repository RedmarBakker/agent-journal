from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.card_type_catalogue import WORK
from journal.support.card_type import CardType
from journal.features.feature import Feature
from journal.features.questions.commands.question_command import QuestionCommand
from journal.features.questions.listeners.question_card import QuestionCard
from journal.features.questions.listeners.answer_card import AnswerCard
from journal.features.questions.listeners.close_card import CloseCard
from journal.features.questions.support.question_process_card import QuestionProcessCard
from journal.features.questions.questions_conduct import QuestionsConduct
from journal.features.questions.support.questions_data_reader import QuestionsDataReader
from journal.features.questions.support.questions_data import QuestionsData
from journal.features.questions.states.waiting import Waiting
from journal.features.questions.questions_nudges import QuestionsNudges
from journal.features.questions.questions_part import QuestionsPart


class Questions(Feature[QuestionsData]):
    name = QuestionsPart.name
    card_families = (CardFamily("questions", "Questions", "questions", WORK),)
    card_types = (CardTypeEntry(CardType.QUESTIONS, "Questions asked and answered", "questions"),)
    title = "Questions"
    help = "The agent asks you a question and waits; your answer sends it back to work."
    states = (Waiting,)
    commands = (QuestionCommand,)
    listeners = (QuestionCard, AnswerCard, CloseCard)
    process_cards = (QuestionProcessCard,)
    conduct = (QuestionsConduct,)
    data = (QuestionsDataReader,)

    nudges = (QuestionsNudges.QUESTION_ANSWERED, QuestionsNudges.QUESTION_CLOSED, QuestionsNudges.JOURNAL_QUESTION_TOOL)
