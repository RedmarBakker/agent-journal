from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.feature import Feature
from journal.features.estimates.listeners.first_ready_task_sizes import FirstReadyTaskSizes
from journal.features.estimates.listeners.merged_delivery_evidence import MergedDeliveryEvidence
from journal.features.estimates.listeners.task_outcome_events import TaskOutcomeEvents
from journal.features.estimates.listeners.task_outcome_merges import TaskOutcomeMerges
from journal.features.estimates.listeners.task_outcome_waits import TaskOutcomeWaits


class Estimates(Feature[object]):
    name = "estimates"
    title = "Plan estimates"
    help = "Fixed sprint calendars and delivery estimates for existing plans."
    options = (EstimatesOptions.MODE, EstimatesOptions.SPRINT_LENGTH_DAYS, EstimatesOptions.SIZE_SCALE,
               EstimatesOptions.FORECAST_TRIALS, EstimatesOptions.FORECAST_HORIZON_SPRINTS)
    listeners = (TaskOutcomeEvents, TaskOutcomeWaits, TaskOutcomeMerges, MergedDeliveryEvidence, FirstReadyTaskSizes)
