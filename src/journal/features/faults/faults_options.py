from journal.support.option import Option


class FaultsOptions:
    DEVELOPER = Option("faults.developer", "Developer features", "Times every request and hook and lists the newest of them, and lets each developer switch below work; off, nothing is timed, listed or counted, whatever the switches below are set to", False, kind="switch")
    REPORT = Option("faults.report", "Report slow requests to the agent", "A request over its budget is marked in the chat and the agent is sent a line to fix it; off, the Developer tab still counts every request's time while the developer features are on", False, kind="switch", main_switch=DEVELOPER)
    HOOK_LINE_COPY = Option("faults.terminal_hook_lines", "Show the agent's hook lines in the terminal", "Every line the journal gives the agent in a hook is also shown to you in the agent's terminal; the agent gets its lines either way", False, kind="switch", main_switch=DEVELOPER)
    REQUEST = Option("faults.budget.request", "Budget for a request that reads", "Milliseconds a request that reads may take before it is reported; 0 reports none", 50, unit="ms")
    EDIT_BUDGET = Option("faults.budget.write", "Budget for a request that writes", "Milliseconds a request that writes may take before it is reported; 0 reports none", 50, unit="ms")
    REPEAT = Option("faults.repeat_minutes", "New slow requests report after", "Minutes since the last slow requests report before a new one is made of what gathered since, its mark written in the chat and the agent sent a line to read it; 0 makes one only", 5, unit="min")
    LOADS = Option("faults.count_loads", "Count the records each request reads", "Every record a request or a hook reads from the database is counted by its kind, shown with the newest requests and as totals since the last reset; off, nothing is counted", False, kind="switch", main_switch=DEVELOPER)
    STALL_STACKS = Option("faults.stall_stacks", "Write every thread's stack when a request stalls", "A request still running after five seconds writes the stack of every thread of the journal to its log, which shows what a stall waits on", False, kind="switch", main_switch=DEVELOPER)
    STAGE_TIMING = Option("faults.stage_times", "Time every stage of a hook", "Each stage a hook passes through, its entry, its transcript, each feature's facts read and each listener, adds its time to the Developer numbers, listed by journal developer averages", False, kind="switch", main_switch=DEVELOPER)
    JOBS = Option("faults.jobs", "Tell the agent about slow jobs", "A background job whose tick runs longer than a second is logged while the developer features are on; on, the agent is also sent a line to fix it", False, kind="switch", main_switch=DEVELOPER)
