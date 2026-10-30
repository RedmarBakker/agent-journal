from journal.events.blocking import Blocking
from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.feature import Feature
from journal.features.estimates.estimates_conduct import EstimatesConduct
from journal.features.estimates.estimates_nudges import EstimatesNudges
from journal.features.estimates.estimates_part import EstimatesPart
from journal.features.estimates.listeners.enforcement_plan_boundary import EnforcementPlanBoundary
from journal.features.estimates.listeners.first_ready_task_sizes import FirstReadyTaskSizes
from journal.features.estimates.listeners.merged_delivery_evidence import MergedDeliveryEvidence
from journal.features.estimates.listeners.task_outcome_events import TaskOutcomeEvents
from journal.features.estimates.listeners.task_outcome_merges import TaskOutcomeMerges
from journal.features.estimates.listeners.task_outcome_waits import TaskOutcomeWaits
from journal.features.estimates.support.estimates_data_reader import EstimatesDataReader


class Estimates(Feature[object]):
    name = EstimatesPart.name
    title = "Plan estimates"
    help = "Fixed sprint calendars and delivery estimates for existing plans."
    options = (EstimatesOptions.MODE, EstimatesOptions.SPRINT_LENGTH_DAYS, EstimatesOptions.SIZE_SCALE,
               EstimatesOptions.FORECAST_TRIALS, EstimatesOptions.FORECAST_HORIZON_SPRINTS,
               EstimatesOptions.SCOPE_GROWTH_WARNING_POINTS, EstimatesOptions.AGING_P85_MULTIPLIER,
               EstimatesOptions.AGING_MINIMUM_OUTCOMES, EstimatesOptions.SPRINT_MISS_WARNING_PERCENT,
               EstimatesOptions.RISK_REPEAT_MINUTES)
    listeners = (TaskOutcomeEvents, TaskOutcomeWaits, TaskOutcomeMerges, MergedDeliveryEvidence, FirstReadyTaskSizes)
    answer_listeners = ((EnforcementPlanBoundary, Blocking.NEXT_DECISION),)
    conduct = (EstimatesConduct,)
    data = (EstimatesDataReader,)
    nudges = (EstimatesNudges.FORECAST_BASIS, EstimatesNudges.SCOPE_GROWTH, EstimatesNudges.AGING_TASK,
              EstimatesNudges.CRITICAL_PREREQUISITE, EstimatesNudges.SPRINT_MISS)
