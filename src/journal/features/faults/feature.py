from journal.engine.nudge import Nudge
from journal.features.feature import Feature
from journal.support.option import Option
from journal.features.faults.commands.developer_command import DeveloperCommand
from journal.features.faults.jobs.developer_write import DeveloperWrite
from journal.features.faults.listeners.slow_job_notice import SlowJobNotice
from journal.features.faults.seeds.stale_test_run_files import StaleTestRunFiles
from journal.features.faults.support.slow_request_process_card import SlowRequestProcessCard


class Faults(Feature):
    REPORT = Option("faults.report", "Report slow requests to the agent", "A request over its budget is marked in the chat and the agent is told to fix it; off, the Developer tab still counts every request's time", False, kind="switch")
    HOOK_LINE_COPY = Option("faults.terminal_hook_lines", "Show the agent's hook lines in the terminal", "Every line the journal gives the agent in a hook is also shown to you in the agent's terminal; the agent gets its lines either way", False, kind="switch")
    REQUEST = Option("faults.budget.request", "Budget for a request that reads", "Milliseconds a request that reads may take before it is reported; 0 reports none", 50, unit="ms")
    EDIT_BUDGET = Option("faults.budget.write", "Budget for a request that writes", "Milliseconds a request that writes may take before it is reported; 0 reports none", 50, unit="ms")
    REPEAT = Option("faults.repeat_minutes", "Tell slow requests again after", "Minutes since the agent was last told of slow requests before it is told again how many have gathered since; 0 tells it once only", 15, unit="min")
    LOADS = Option("faults.count_loads", "Count the records each request reads", "Every record a request or a hook reads from the database is counted by its kind, shown with the newest requests and as totals since the last reset; off, nothing is counted", False, kind="switch")
    STALL_STACKS = Option("faults.stall_stacks", "Write every thread's stack when a request stalls", "A request still running after five seconds writes the stack of every thread of the journal to its log, so a stall names what holds it", False, kind="switch")
    STAGE_TIMING = Option("faults.stage_times", "Time every stage of a hook", "Each stage a hook passes through, its entry, its transcript, each feature's facts read and each listener, adds its time to the Developer numbers, listed by journal developer averages", False, kind="switch")
    JOBS = Option("faults.jobs", "Tell the agent about slow jobs", "A background job whose tick runs longer than a second is always logged; on, the agent is told to fix it too", False, kind="switch")
    name = "faults"
    title = "Slow requests"
    default = False
    help = "A request slower than its budget is a fault: everything runs on one machine against one file, so a slow answer is a bug. These are tools for developing the journal itself, so they start switched off in every project. They gather in one mark in the chat, each route with its worst time and how often, and the agent is told in one line how many gathered, once ten have or thirty seconds pass without another, and again only once the set minutes have passed. It stays quiet while the journal starts or updates and while the machine is busier than it has cores."
    SLOW_REQUESTS = Nudge(name, "slow_requests_to_fix", "{{count}} slow requests, the worst {{route}} at {{ms}} ms: journal developer slowest")
    SLOW_JOB = Nudge(name, "slow_job_to_fix", "the background job {{job}} took {{seconds}} seconds for one tick", "fix what made it slow at its source")
    options = (REPORT, REQUEST, EDIT_BUDGET, REPEAT, LOADS, JOBS, STALL_STACKS, STAGE_TIMING, HOOK_LINE_COPY)
    nudges = (SLOW_REQUESTS, SLOW_JOB)
    listeners = (SlowJobNotice,)
    seeds = (StaleTestRunFiles,)
    jobs = (DeveloperWrite,)
    process_cards = (SlowRequestProcessCard,)
    commands = (DeveloperCommand,)