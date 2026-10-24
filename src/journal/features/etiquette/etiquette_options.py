from journal.support.option import Option


class EtiquetteOptions:
    PLAIN_CODE_INTERVAL = Option("etiquette.plain_code_every", "Remind to write code in plain words every", "Edits of code files between reminders that names and text in code are plain words, never the voice", 50, unit="edits")
    REMINDER_INTERVAL = Option("etiquette.remind_every", "Remind what a journal line is every", "Lines the journal says to the agent between reminders that a journal line is an instruction, not a message", 50, unit="lines")
