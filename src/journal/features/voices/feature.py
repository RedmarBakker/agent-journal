from journal.features.feature import Feature
from journal.features.voices.commands.voice_command import VoiceCommand
from journal.features.voices.voices_conduct import VoicesConduct
from journal.features.voices.support.voices_data_reader import VoicesDataReader
from journal.features.voices.support.voices_data import VoicesData
from journal.features.voices.voices_part import VoicesPart
from journal.features.voices.voices_nudges import VoicesNudges
from journal.features.voices.voices_options import VoicesOptions


class Voices(Feature[VoicesData]):
    """The agent talks to you in the voice you choose, by your title and first name, as the voice says."""
    name = VoicesPart.name
    title = "Voice"
    help = "The agent talks to you in the voice you choose, by your title and first name."
    commands = (VoiceCommand,)
    options = (VoicesOptions.PROFILE, VoicesOptions.TITLE, VoicesOptions.NAME, VoicesOptions.AVATAR, VoicesOptions.AVATAR_SHOWN)
    data = (VoicesDataReader,)
    conduct = (VoicesConduct,)

    nudges = (VoicesNudges.VOICE_INSTRUCTION, VoicesNudges.VOICE_CHANGE, VoicesNudges.INTRODUCE_YOURSELF, VoicesNudges.RETURN_GREETING)
