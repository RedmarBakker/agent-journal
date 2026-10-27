from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class VoicesNudges:
    VOICE_INSTRUCTION = Nudge("voices", "how_to_talk_to_the_user", "talk to the user like this: {{voice|cap=1500}}", "", repeat=Timeout.seconds(0), longest_characters=1530, longest_reason="it contains the voice the user wrote")
    INTRODUCE_YOURSELF = Nudge("voices", "introduce_yourself", "introduce yourself in the chat in one or two lines in your voice, then ask what to do unless the user already asked", "", repeat=Timeout.seconds(0), chat_answerable=True)
    VOICE_CHANGE = Nudge("voices", "the_voice_changed", "from now on talk to the user like this: {{voice|cap=1500}} use it from your next chat line; say nothing of the change", "", repeat=Timeout.seconds(0), chat_answerable=True, longest_characters=1600, longest_reason="it contains the voice the user wrote")
    RETURN_GREETING = Nudge("voices", "say_you_are_back", "you are back in an earlier conversation", "say so in a line in your voice, then carry on", repeat=Timeout.seconds(0))
