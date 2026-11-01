from journal.features.feature import Feature
from journal.features.organization.commands.organization_command import OrganizationCommand
from journal.features.organization.commands.role_command import RoleCommand
from journal.features.organization.hub_conduct import HubConduct
from journal.features.organization.listeners.board_standing_record import BoardStandingRecord
from journal.features.organization.listeners.domain_count_record import DomainCountRecord
from journal.features.organization.listeners.plan_task_completion_wake import PlanTaskCompletionWake
from journal.features.organization.listeners.role_clock_out_wake import RoleClockOutWake
from journal.features.organization.listeners.split_completion import SplitCompletion
from journal.features.organization.listeners.role_ending_report import RoleEndingReport
from journal.features.organization.listeners.role_queue_feeder import RoleQueueFeeder
from journal.features.organization.listeners.role_refusal_report import RoleRefusalReport
from journal.features.organization.listeners.role_stuck_report import RoleStuckReport
from journal.features.organization.listeners.role_task_domain import RoleTaskDomain
from journal.features.organization.listeners.split_part_wake import SplitPartWake
from journal.features.organization.organization_conduct import OrganizationConduct
from journal.features.organization.organization_nudges import OrganizationNudges
from journal.features.organization.organization_part import OrganizationPart
from journal.features.organization.role_conduct import RoleConduct
from journal.features.organization.states.role_work import RoleWork
from journal.features.organization.support.organization_data import OrganizationData
from journal.features.organization.support.organization_data_reader import OrganizationDataReader
from journal.features.organization.support.organization_seat_routing import OrganizationSeatRouting
from journal.support.agent_role import AgentRole


class OrganizationFeature(Feature[OrganizationData]):
    name = OrganizationPart.name
    title = "Agentic organization"
    help = "The domains and Roles of an agentic organization are read from the folder the Settings page names; journal holds no list of them. Each Role is one value that solo and seats both use: a worker dispatched to a Role works inside its tools and approvals, and a solo Plan agent takes on one Role at a time as a pushed state. A task handed or queued to a Role is linked to its domain, so each domain has a board of the plans with tasks there, each standing in the phase that domain's tasks reached. A Role that is stuck, refused or ends without clocking out is reported up the hub: to its Domain agent, else the Plan agent, else the user."
    skill = OrganizationSeatRouting.skill
    commands = (OrganizationCommand, RoleCommand)
    states = (RoleWork,)
    conduct = (OrganizationConduct, HubConduct)
    listeners = (RoleTaskDomain, RoleQueueFeeder, BoardStandingRecord, DomainCountRecord, RoleEndingReport, RoleClockOutWake, PlanTaskCompletionWake, SplitPartWake, SplitCompletion)
    data = (OrganizationDataReader,)
    helper_conduct = {AgentRole.WORKER: (RoleConduct,)}
    helper_listeners = {AgentRole.WORKER: (RoleStuckReport, RoleRefusalReport)}
    nudges = (OrganizationNudges.ROLE_WRITES_NOTHING, OrganizationNudges.ACTION_WAITS_FOR_USER, OrganizationNudges.ACTING_AS_ROLE, OrganizationNudges.ROLE_TOOL_REFUSED, OrganizationNudges.ONE_ROLE_AT_A_TIME, OrganizationNudges.ROLE_REPORTED, OrganizationNudges.ROLE_TASK_RETURN, OrganizationNudges.PLAN_TASK_AWAITS_HANDOFF, OrganizationNudges.UNREAD_HANDOFF, OrganizationNudges.ROLE_WORK_AWAITS_CHECK, OrganizationNudges.SPLIT_PART_WAITING_FOR_MERGE, OrganizationNudges.TASK_CAN_BE_SPLIT, OrganizationNudges.SPLIT_PART_READY, OrganizationNudges.SPLIT_ALL_PARTS_CANCELLED, OrganizationNudges.SPLIT_TASK_COMPLETED, OrganizationNudges.SPLIT_HANDOFF_REQUIRED, OrganizationNudges.SPLIT_OTHER_DOMAIN)
