from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.feature import Feature


class Estimates(Feature[object]):
    name = "estimates"
    title = "Plan estimates"
    help = "Fixed sprint calendars and delivery estimates for existing plans."
    options = (EstimatesOptions.MODE, EstimatesOptions.SPRINT_LENGTH_DAYS)
