from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope


class EstimatesOptions:
    MODE = Option("estimates.mode", "Estimates mode", "Off leaves existing planning behavior alone; record saves delivery history; report shows estimates; enforce applies only explicitly enabled size and work-in-progress gates", "off", option_type="choice", choices=("off", "record", "report", "enforce"), scope=OptionScope.PERSON, setter=USER)
    SPRINT_LENGTH_DAYS = Option("estimates.sprint_length_days", "Calendar days in a sprint", "The fixed number of local calendar days in every new sprint; changing it applies to future periods only", 14, unit="days", scope=OptionScope.PERSON, setter=USER)
