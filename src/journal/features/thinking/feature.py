from journal.features.feature import Feature
from journal.features.thinking.listeners.thought_record import ThoughtRecord
from journal.features.thinking.listeners.thinking_stop import ThinkingStop
from journal.features.thinking.listeners.thinking_watch import ThinkingWatch


class Thinking(Feature):
    name = "thinking"
    title = "Thinking"
    help = "Each of the agent's thoughts is kept as a message in the chat, marked a thought, which the chat's Shown menu can hide; the latest stands in the working bubble until the agent says something. A reply the agent wrote in its thinking, which the user would never see, is posted as the reply. The agent at work and quiet a few seconds after a tool came back is marked thinking, which the figure and the chat's status line show."
    listeners = (ThoughtRecord, ThinkingWatch, ThinkingStop)
