from journal.features.feature import Feature
from journal.features.usage.jobs.context_limit_compaction import ContextLimitCompaction
from journal.features.usage.states.usage_limited import UsageLimited
from journal.features.usage.usage_conduct import UsageConduct
from journal.features.usage.usage_nudges import UsageNudges
from journal.features.usage.usage_options import UsageOptions


class Usage(Feature):
    NAME = "usage"

    name = NAME
    title = "Usage limits"
    fixed = True
    help = "When the agent's provider refuses its turns on a usage limit, the journal types nothing to it, types your messages at once, and tries a turn every so often until the limit is over. When the agent stops at the context limit, the journal types the compact command for it."
    states = (UsageLimited,)
    conduct = (UsageConduct,)
    nudges = (UsageNudges.LIMIT_CHECK,)
    options = (UsageOptions.CHECK_MINUTES,)
    jobs = (ContextLimitCompaction,)
