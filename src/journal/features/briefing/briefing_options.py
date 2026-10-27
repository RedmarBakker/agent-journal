from journal.support.option import Option


class BriefingOptions:
    OVERVIEW_COMMANDS = Option("briefing.look_commands", "Commands the overview runs",
                               "The commands journal environment overview runs after its summary, in this order, each under its heading: a journal line by the journal itself, any other "
                               "line in the project's shell; journal plan show current shows the started plan and journal task show current the task in hand, each saying so when there is none; journal reader list names the readers kept for reading outputs",
                               ["journal plan show current", "journal task list", "journal message unread", "journal worker open", "journal question list", "journal reader list", "journal task show current"], option_type="lines")
