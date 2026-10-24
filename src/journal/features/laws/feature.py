from journal.features.feature import Feature
from journal.features.laws.laws_conduct import LawsConduct
from journal.features.laws.laws_nudges import LawsNudges


class Laws(Feature):
    """The journal's law: what binds every agent and cannot be switched off."""

    name = "laws"
    title = "Journal laws"
    help = "A dispatch without a model or a job is refused; a large result is named."
    conduct = (LawsConduct,)

    nudges = (LawsNudges.MISSING_MODEL, LawsNudges.MISSING_PROFILE, LawsNudges.UNBOUND_DISPATCH, LawsNudges.LONG_OUTPUT)
