from journal.features.feature import Feature
from journal.engine.nudge import Nudge
from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope
from journal.features.voices.support.builtin_catalogue import BuiltinCatalogue
from journal.features.voices.commands.voice_command import VoiceCommand
from journal.features.voices.voices_conduct import VoicesConduct
from journal.features.voices.support.voices_data_reader import VoicesDataReader
from journal.features.voices.support.voices_data import VoicesData


class Voices(Feature[VoicesData]):
    """The agent talks to you in the voice you choose, by your title and first name, as the voice says."""
    PROFILE = Option("voices.profile", "Voice", "How the agent talks to you", "butler", kind="choice", choices=tuple(v.name for v in BuiltinCatalogue.ALL), scope=OptionScope.PERSON, setter=USER)
    TITLE = Option("voices.title", "Your title", "Sir, Madam, Captain: what the voice calls you before your name", "Sir", kind="text", scope=OptionScope.PERSON)
    NAME = Option("voices.name", "Your first name", "Empty takes the name git knows you by", "", kind="text", scope=OptionScope.PERSON)
    VOICE_OPTIONS = (PROFILE, TITLE, NAME)
    AVATAR = Option("voices.avatar", "Show a figure in the chat", "A small figure beside the chat shows what the agent is doing, in the voice it speaks", True, kind="switch", scope=OptionScope.PERSON)
    AVATAR_SHOWN = Option("voices.avatar_shown", "Show the figure", "Always, only while the agent works, or never", "always", kind="choice", choices=("always", "working", "never"), scope=OptionScope.PERSON)

    name = "voices"
    title = "Voice"
    help = "The agent talks to you in the voice you choose, by your title and first name."
    commands = (VoiceCommand,)
    options = (PROFILE, TITLE, NAME, AVATAR, AVATAR_SHOWN)
    data = (VoicesDataReader,)
    conduct = (VoicesConduct,)

    VOICE_INSTRUCTION = Nudge(name, "how_to_talk_to_the_user", "how to talk to the user", "{{voice}}", repeat_interval=0)
    INTRODUCE_YOURSELF = Nudge(name, "introduce_yourself", "introduce yourself in the chat", "one or two lines in your voice, then ask what to do unless the user already asked for something", repeat_interval=0, chat_answerable=True)
    VOICE_CHANGE = Nudge(name, "the_voice_changed", "the user changed how you talk to them", "from now on: {{voice}} Open your next chat line in the new voice, and say nothing else about it", repeat_interval=0, chat_answerable=True)
    RETURN_GREETING = Nudge(name, "say_you_are_back", "you are back in an earlier conversation", "say so in a line in your voice, then carry on", repeat_interval=0)
    nudges = (VOICE_INSTRUCTION, VOICE_CHANGE, INTRODUCE_YOURSELF, RETURN_GREETING)
