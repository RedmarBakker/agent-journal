from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class VoicesNudges:
    VOICE_INSTRUCTION = Nudge("voices", "how_to_talk_to_the_user", "how to talk to the user", "{{voice}}", repeat=Timeout.seconds(0))
    INTRODUCE_YOURSELF = Nudge("voices", "introduce_yourself", "introduce yourself in the chat", "one or two lines in your voice, then ask what to do unless the user already asked for something", repeat=Timeout.seconds(0), chat_answerable=True)
    VOICE_CHANGE = Nudge("voices", "the_voice_changed", "the user changed how you talk to them", "from now on: {{voice}} Open your next chat line in the new voice, and say nothing else about it", repeat=Timeout.seconds(0), chat_answerable=True)
    RETURN_GREETING = Nudge("voices", "say_you_are_back", "you are back in an earlier conversation", "say so in a line in your voice, then carry on", repeat=Timeout.seconds(0))
