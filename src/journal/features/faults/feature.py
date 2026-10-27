from journal.features.feature import Feature
from journal.features.faults.commands.developer_command import DeveloperCommand
from journal.features.faults.listeners.slow_job_notice import SlowJobNotice
from journal.features.faults.listeners.slow_requests_card import SlowRequestsCard
from journal.features.faults.seeds.stale_test_run_files import StaleTestRunFiles
from journal.features.faults.support.slow_request_process_card import SlowRequestProcessCard
from journal.features.faults.faults_nudges import FaultsNudges
from journal.features.faults.faults_options import FaultsOptions
from journal.features.faults.jobs.sentry_sender import SentrySender


class Faults(Feature):
    name = "faults"
    title = "Slow requests"
    default = False
    help = "A request slower than its budget is a fault: everything runs on one machine against one file, so a slow answer is a bug. These are tools for developing the journal itself, so they start switched off in every project. They gather in one mark in the chat, each route with its worst time and how often, and the agent is told in one line how many gathered, once ten have or thirty seconds pass without another, and again only once the set minutes have passed. It stays quiet while the journal starts or updates and while the machine is busier than it has cores."
    jobs = (SentrySender,)
    options = (FaultsOptions.SENTRY_DSN, FaultsOptions.DEVELOPER, FaultsOptions.REPORT, FaultsOptions.REQUEST, FaultsOptions.EDIT_BUDGET, FaultsOptions.REPEAT, FaultsOptions.LOADS, FaultsOptions.JOBS, FaultsOptions.STALL_STACKS, FaultsOptions.STAGE_TIMING, FaultsOptions.HOOK_LINE_COPY)
    nudges = (FaultsNudges.SLOW_REQUESTS, FaultsNudges.SLOW_JOB)
    listeners = (SlowJobNotice, SlowRequestsCard)
    seeds = (StaleTestRunFiles,)
    process_cards = (SlowRequestProcessCard,)
    commands = (DeveloperCommand,)