from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope


class OrganizationOptions:
    """The options of the agentic organization: how a new plan runs, the OpenRig it runs on and what it may spend."""

    PLAN_MODE = Option("workers.default_plan_mode", "Default plan mode", "How a new plan runs. Organization: its Plan agent hands the work to Roles that work as seats and writes no code itself. Solo: its Plan agent takes on one Role at a time and does the work itself. A plan already running keeps its mode", "organization", option_type="choice", choices=("organization", "solo"), scope=OptionScope.PERSON, setter=USER)
    OPENRIG_VERSION = Option("workers.openrig_version", "OpenRig version", "The OpenRig version the journal runs its seats on, such as 0.4.2; empty uses the newest installed", "", option_type="text", scope=OptionScope.MACHINE, setter=USER)
    COST_CAP = Option("workers.cost_cap_dollars", "Most a plan may cost", "The dollars one plan's agents may spend before the plan is paused and you are asked; 0 sets no cap", 0, unit="$", setter=USER)
    SEAT_CAP = Option("workers.seat_cap", "Most seats at once", "The most seats, Roles working at the same time, across all running plans; a seat past it waits until one is free; 0 sets no cap", 0, unit="seats", scope=OptionScope.MACHINE, setter=USER)
