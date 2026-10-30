from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope


class EstimatesOptions:
    MODE = Option("estimates.mode", "Estimates mode", "Off leaves existing planning behavior alone; record saves delivery history; report shows estimates; enforce applies only explicitly enabled size and work-in-progress gates", "off", option_type="choice", choices=("off", "record", "report", "enforce"), scope=OptionScope.PERSON, setter=USER)
    SPRINT_LENGTH_DAYS = Option("estimates.sprint_length_days", "Calendar days in a sprint", "The fixed number of local calendar days in every new sprint; changing it applies to future periods only", 14, unit="days", scope=OptionScope.PERSON, setter=USER)
    SIZE_SCALE = Option("estimates.size_scale", "Story point scale", "The relative task sizes a plan builder can choose; a size above its largest value must be split", [1, 2, 3, 5, 8, 13], option_type="lines", scope=OptionScope.PERSON, setter=USER)
    FORECAST_TRIALS = Option("estimates.forecast_trials", "Forecast trials", "How many empirical delivery scenarios the baseline forecast samples", 10000, unit="trials", scope=OptionScope.PERSON, setter=USER)
    FORECAST_HORIZON_SPRINTS = Option("estimates.forecast_horizon_sprints", "Forecast horizon", "How many sprint lengths the baseline forecast simulates before reporting work beyond its horizon", 6, unit="sprints", scope=OptionScope.PERSON, setter=USER)
