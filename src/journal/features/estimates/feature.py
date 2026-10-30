from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.feature import Feature
from journal.features.estimates.listeners.first_ready_task_sizes import FirstReadyTaskSizes
from journal.features.estimates.listeners.merged_delivery_evidence import MergedDeliveryEvidence


class Estimates(Feature[object]):
    name = "estimates"
    title = "Plan estimates"
    help = "Fixed sprint calendars and delivery estimates for existing plans."
    options = (EstimatesOptions.MODE, EstimatesOptions.SPRINT_LENGTH_DAYS, EstimatesOptions.SIZE_SCALE)
    listeners = (MergedDeliveryEvidence, FirstReadyTaskSizes)
