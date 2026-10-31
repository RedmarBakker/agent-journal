from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope
from journal.support.rejection import Rejection


ENFORCEMENT_PLAN_BOUNDARY = "estimates.enforcement_plan_boundary"


class EstimatesOptions:
    EXECUTION_WIP_LIMIT = Option("estimates.execution_wip", "Project execution WIP limit", "Owner-set number of started tasks that may be in execution at once; zero leaves this limit off", 0, unit="tasks", scope=OptionScope.PERSON, setter=USER)
    PLAN_DELIVERY_WIP_LIMIT = Option("estimates.delivery_wip_per_plan", "Plan delivery WIP limit", "Owner-set number of started tasks awaiting accepted delivery that one plan may hold; zero leaves this limit off", 0, unit="tasks", scope=OptionScope.PERSON, setter=USER)
    DOMAIN_DELIVERY_WIP_LIMIT = Option("estimates.delivery_wip_per_domain", "Domain delivery WIP limit", "Owner-set number of started tasks awaiting accepted delivery that one domain may hold across plans; zero leaves this limit off", 0, unit="tasks", scope=OptionScope.PERSON, setter=USER)
    WORKER_QUEUE_WIP_LIMIT = Option("estimates.worker_queue", "Worker assignment WIP limit", "Owner-set number of queued, current and finished-unmerged task assignments one worker may hold; zero leaves this limit off", 0, unit="tasks", scope=OptionScope.PERSON, setter=USER)
    MODE = Option("estimates.mode", "Estimates mode", "Off leaves existing planning behavior alone; record saves delivery history; report shows estimates; enforce applies only explicitly enabled size and work-in-progress gates", "off", option_type="choice", choices=("off", "record", "report", "enforce"), scope=OptionScope.PERSON, setter=USER)
    SPRINT_LENGTH_DAYS = Option("estimates.sprint_length_days", "Calendar days in a sprint", "The fixed number of local calendar days in every new sprint; changing it applies to future periods only", 14, unit="days", scope=OptionScope.PERSON, setter=USER)
    SIZE_SCALE = Option("estimates.size_scale", "Story point scale", "The relative task sizes a plan builder can choose; a size above its largest value must be split", [1, 2, 3, 5, 8, 13], option_type="lines", scope=OptionScope.PERSON, setter=USER)
    FORECAST_TRIALS = Option("estimates.forecast_trials", "Forecast trials", "How many empirical delivery scenarios the baseline forecast samples", 10000, unit="trials", scope=OptionScope.PERSON, setter=USER)
    FORECAST_HORIZON_SPRINTS = Option("estimates.forecast_horizon_sprints", "Forecast horizon", "How many sprint lengths the baseline forecast simulates before reporting work beyond its horizon", 6, unit="sprints", scope=OptionScope.PERSON, setter=USER)
    SCOPE_GROWTH_WARNING_POINTS = Option("estimates.scope_growth_warning_points", "Warn after scope grows by", "Story points added or accepted beyond the first ready scope before the agent is advised to review the change with the owner", 1, unit="points", scope=OptionScope.PERSON, setter=USER)
    AGING_P85_MULTIPLIER = Option("estimates.aging_p85_multiplier", "Warn past historical P85 by", "The multiple of comparable completed active time a task must exceed before it is called older than its historical P85", 1.0, unit="times", scope=OptionScope.PERSON, setter=USER)
    AGING_MINIMUM_OUTCOMES = Option("estimates.aging_minimum_outcomes", "Comparable completed tasks before an aging warning", "The minimum number of completed tasks in the same recorded outcome cohort before its P85 can be used as a comparison", 5, unit="tasks", scope=OptionScope.PERSON, setter=USER)
    SPRINT_MISS_WARNING_PERCENT = Option("estimates.sprint_miss_warning_percent", "Warn below this sprint delivery chance", "The minimum empirical chance of finishing by the current sprint end before the agent is advised to review scope and dependencies with the owner", 70, unit="percent", scope=OptionScope.PERSON, setter=USER)
    RISK_REPEAT_MINUTES = Option("estimates.risk_repeat_minutes", "Repeat bounded plan advice after", "Minutes before the same forecast or risk advice may be sent again; zero permits it at every stop or tick", 30, unit="minutes", scope=OptionScope.PERSON, setter=USER)


def wip_limit(value: object, key: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Rejection(f"{key} must be a nonnegative integer")
    return value
