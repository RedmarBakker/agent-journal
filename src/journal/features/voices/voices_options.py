from journal.features.voices.support.builtin_catalogue import BuiltinCatalogue
from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope


class VoicesOptions:
    PROFILE = Option("voices.profile", "Voice", "How the agent talks to you", "butler", kind="choice", choices=tuple(v.name for v in BuiltinCatalogue.ALL), scope=OptionScope.PERSON, setter=USER)
    TITLE = Option("voices.title", "Your title", "Sir, Madam, Captain: what the voice calls you before your name", "Sir", kind="text", scope=OptionScope.PERSON)
    NAME = Option("voices.name", "Your first name", "Empty takes the name git knows you by", "", kind="text", scope=OptionScope.PERSON)
    AVATAR = Option("voices.avatar", "Show a figure in the chat", "A small figure beside the chat shows what the agent is doing, in the voice it speaks", True, kind="switch", scope=OptionScope.PERSON)
    AVATAR_SHOWN = Option("voices.avatar_shown", "Show the figure", "Always, only while the agent works, or never", "always", kind="choice", choices=("always", "working", "never"), scope=OptionScope.PERSON)
    VOICE_OPTIONS = (PROFILE, TITLE, NAME)
