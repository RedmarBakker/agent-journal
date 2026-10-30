from journal.features.feature import Feature
from journal.features.faults.commands.developer_command import DeveloperCommand
from journal.features.faults.listeners.slow_job_notice import SlowJobNotice
from journal.features.faults.listeners.slow_requests_card import SlowRequestsCard
from journal.features.faults.listeners.transition_counts import TransitionCounts
from journal.features.faults.seeds.stale_test_run_files import StaleTestRunFiles
from journal.features.faults.support.slow_request_process_card import SlowRequestProcessCard
from journal.features.faults.faults_nudges import FaultsNudges
from journal.features.faults.faults_options import FaultsOptions


class Faults(Feature):
    name = "faults"
    title = "Developer features"
    default = False
    help = "Tools for developing the journal itself, off in every project; while off, nothing below is measured or shown."
    options = (FaultsOptions.PERFORMANCE, FaultsOptions.REPORT, FaultsOptions.REQUEST, FaultsOptions.EDIT_BUDGET, FaultsOptions.REPEAT, FaultsOptions.LOADS, FaultsOptions.STALL_STACKS, FaultsOptions.STAGE_TIMING, FaultsOptions.JOBS, FaultsOptions.INTERNAL, FaultsOptions.HOOK_LINE_COPY, FaultsOptions.HOOK_TIME_COPY, FaultsOptions.EARLY_VIEWER_WRITE_WARNING)
    nudges = (FaultsNudges.SLOW_REQUESTS, FaultsNudges.SLOW_JOB, FaultsNudges.EARLY_VIEWER_WRITE)
    listeners = (SlowJobNotice, SlowRequestsCard, TransitionCounts)
    seeds = (StaleTestRunFiles,)
    process_cards = (SlowRequestProcessCard,)
    commands = (DeveloperCommand,)