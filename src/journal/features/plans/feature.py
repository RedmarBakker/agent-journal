from journal.events.blocking import Blocking
from journal.events.rows.plan_approved import PlanApproved
from journal.features.feature import Feature
from journal.features.plans.support.plans_data_reader import PlansDataReader
from journal.features.plans.support.plans_data import PlansData
from journal.features.plans.listeners.plan_blockade import PlanBlockade
from journal.features.plans.listeners.plan_delegation import PlanDelegation
from journal.features.plans.listeners.clear_plan_waits import ClearPlanWaits
from journal.features.plans.listeners.count_plan_reviewers import CountPlanReviewers
from journal.support.skill import Skill
from journal.features.plans.commands.plan_command import PlanCommand
from journal.features.plans.listeners.advance_plan import AdvancePlan
from journal.features.plans.listeners.allowed_test_run_use import AllowedTestRunUse
from journal.features.plans.listeners.reopen_finished_plan import ReopenFinishedPlan
from journal.features.plans.listeners.plan_reopening import PlanReopening
from journal.features.plans.listeners.ended_drive_write_guard import EndedDriveWriteGuard
from journal.features.plans.listeners.session_start_plan_start import SessionStartPlanStart
from journal.features.plans.support.plan_start_task_assigner import PlanStartTaskAssigner
from journal.features.plans.support.plan_task_assigner import PlanTaskAssigner
from journal.features.plans.listeners.plan_finished_plan_start import PlanFinishedPlanStart
from journal.features.plans.plans_conduct import PlansConduct
from journal.features.plans.coordinator_conduct import CoordinatorConduct
from journal.features.plans.listeners.plan_agent_focus import PlanAgentFocus
from journal.features.plans.listeners.started_plan_focus import StartedPlanFocus
from journal.features.plans.seeds.closed_plans import ClosedPlans
from journal.features.plans.states.choosing_plan_return import ChoosingPlanReturn
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.plans_ready import PlansReady
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.engine.support.state_floor import StateFloor
from journal.features.plans.states.leading_plan import LeadingPlan
from journal.features.plans.states.leading_task import LeadingTask, LeadingTaskWorking
from journal.features.plans.listeners.plan_agent_start import PlanAgentStart
from journal.features.plans.listeners.plan_agent_pause import PlanAgentPause
from journal.features.plans.listeners.plan_agent_finish import PlanAgentFinish
from journal.features.plans.listeners.plan_agent_abandon import PlanAgentAbandon
from journal.features.plans.listeners.task_agent_start import TaskAgentStart
from journal.features.plans.listeners.task_agent_finish import TaskAgentFinish
from journal.features.plans.states.plans_working import PlansWorking
from journal.features.plans.listeners.release_plan_waits import ReleasePlanWaits
from journal.features.plans.listeners.plan_testing_default import PlanTestingDefault
from journal.features.plans.jobs.template_plan_start import TemplatePlanStart
from journal.features.plans.listeners.subagent_plan_card import SubagentPlanCard
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.plans_part import PlansPart

from journal.features.plans.states.naming_test_commands import NamingTestCommands

class Plans(Feature[PlansData]):
    name = PlansPart.name
    title = "Plans"
    help = "A plan is a goal, phases and the tasks under them, built with the user and started on their approval; following it, finishing one task starts the next."
    states = (PlansReady, PlansWorking, FollowingPlan, NamingTestCommands, ChoosingPlanReturn, CoordinatingPlans, LeadingPlan, LeadingTask, LeadingTaskWorking)
    state_floor = StateFloor(PlansOptions.PLAN_AGENTS, {True: CoordinatingPlans})
    commands = (PlanCommand,)
    answer_listeners = ((SessionStartPlanStart, Blocking.NEXT_DECISION), (PlanDelegation, Blocking.NEXT_DECISION), (AdvancePlan, Blocking.NEXT_DECISION), (ClearPlanWaits, Blocking.NEXT_DECISION), (ReleasePlanWaits, Blocking.NEXT_DECISION), (PlanBlockade, Blocking.NEXT_DECISION))
    listeners = (AllowedTestRunUse, PlanAgentFocus, StartedPlanFocus, PlanTestingDefault, CountPlanReviewers, ReopenFinishedPlan, PlanReopening, PlanFinishedPlanStart, SubagentPlanCard, PlanAgentStart, PlanAgentPause, PlanAgentFinish, PlanAgentAbandon, TaskAgentStart, TaskAgentFinish)
    assigners = (PlanStartTaskAssigner, PlanTaskAssigner)
    conduct = (PlansConduct,)
    floor_conduct = ((CoordinatingPlans, CoordinatorConduct),)
    data = (PlansDataReader,)
    seeds = (ClosedPlans,)
    jobs = (TemplatePlanStart,)

    options = (PlansOptions.TESTING, PlansOptions.TEST_COMMANDS, PlansOptions.PLAN_AGENTS)
    nudges = (PlansNudges.LEADING_PLAN, PlansNudges.PLAN_RETURN_QUESTION, PlansNudges.PLAN_TESTING_CHANGED, PlansNudges.REVIEW_ENTRY_REQUEST, PlansNudges.UNAPPROVED_PLAN, PlansNudges.NEXT_PLAN_TASK, PlansNudges.SUPERVISOR_WORK_AVAILABLE, PlansNudges.PLAN_FINISHED, PlansNudges.PLAN_MERGE_READY, PlansNudges.PLAN_AGENT_WRITE_SCOPE, PlansNudges.PLAN_STALLED, PlansNudges.PLAN_POSTPONED, PlansNudges.PLAN_ABANDONED, PlansNudges.PLAN_APPROVED, PlansNudges.PLAN_APPROVED_WITH_COMMENT, PlansNudges.CHECKPOINT_PHASE_END, PlansNudges.PHASE_END, PlansNudges.PHASE_END_TESTS, PlansNudges.PLAN_BLOCKED, PlansNudges.PLAN_REOPENED, PlansNudges.COORDINATOR_MODE, PlansNudges.COORDINATOR_WRITES_NO_CODE, PlansNudges.COORDINATOR_SENDS_NO_WORKER, PlansNudges.WORKING_TASK_ALONE, PlansNudges.PLAN_TESTING, PlansNudges.TEST_COMMANDS_NEEDED, PlansNudges.MID_PHASE_TESTS)

    skill = Skill("plans", 'Build and follow a plan of ordered tasks; load it when the user asks for a plan or a roadmap', """
# Plans

A plan is a goal, phases in order, and the tasks under each phase. The main agent builds it with the user; the user
approves it before work starts. Each plan has a mode: an organization Plan agent coordinates Domain agents and Roles,
while a solo Plan agent takes on Roles one at a time.

- `journal plan create "<title>" --brief "<goal>"` drafts it; `journal plan brief <n> "<goal>"` replaces the goal.
- `journal plan phase <n> "<title>" --when "<complete when>"` adds a phase, `--checkpoint` where the user
  should review before the plan continues. A checkpoint stops the plan only when auto mode is off; in auto mode the plan
  continues straight on.
- `journal plan add <n> "<task title>" --brief "<done when>" --phase <k>` files a task under a phase, numbered from 1.
- `journal plan add <n> "<task title>" --size <points>` records its estimate from `estimates.size_scale`.
- `journal plan add <n> "<task title>" --after <task> --reason "<why>"` records a prerequisite.
- `journal plan add <n> "<task title>" --domain <domain>` assigns an organization task to a Domain.
- `journal plan add <n> "<task title>" --delivery-gate-for <task>` requires accepted delivery evidence before the task can proceed.
- `journal plan todos <n> <phase> <tasks…>` moves tasks to another phase. Set priority with `journal task edit <task> --priority <level>`.
- `journal plan mode <n> organization|solo` chooses how the plan is worked. An organization Plan agent coordinates Domain agents and Roles; a solo Plan agent does the work itself, one Role at a time.
- Before `journal plan ready <n>`, check that every phase has tasks and that each task has the relevant size, prerequisite, Domain and delivery gate. Only the user approves, on the plan page or with
  `journal plan approve <n>`; you are informed, and `journal plan start <n>` begins its first task, and also continues past a checkpoint.
  The main agent works through one plan at a time. With Plan agents on, each started plan has its own agent, and the main
  agent can coordinate several plans at once. A plan one of whose tasks goes to a worker while you hold none of its tasks
  is delegated: it is no started plan, so you may start another beside it; starting one of its tasks yourself makes it
  started again, and when its last worker task closes it is paused.
- Before readying a plan, open a review with `journal plan review <n>` and send a `journal-plan-reviewer` to review it.
  In review it cannot be approved,
  and `journal plan ready <n>` waits until every subagent is back. Put what they find straight into the plan as tasks
  under its phases, then mark it ready again with `--changed "<what the round changed, in one line>"`: each round is stored on the
  plan, with its reviewers, the reports filed about the plan while it ran, and that line.
- `journal plan show <n>` lists its phases and tasks; `journal plan list` every plan; `journal plan pause <n>` puts it aside.
- With Plan agents on, a started plan runs in its own environment plan-<n> with its own agent and chat; pausing or
  ending it stops that agent, and `journal plan show <n>` names the environment and whether its agent runs.
  You run plans only through their Plan agents, writing no code and sending no worker of your own:
  `journal plan tell <n> "<what>"` says it to plan n's agent in its chat, and a Plan agent answers you with
  `journal plan report "<how the plan stands>"`; each arrives as a message to read and answer.
- When a solo Plan agent finishes, the journal merges its branch into the project and removes its worktree. If a conflict or uncommitted file stops the merge, fix it and run `journal plan merge <n>`.
- Work outside every plan can stay a standalone task: `journal task start <n>` gives it an agent of its own in task-<n>,
  worked alone as a one-task plan with no plan row; its close stops that agent.
- A blocked task never blocks its plan: go on with the tasks that can be done. When every task left is blocked, the plan
  blocks itself and opens again when one opens. When one thing stops all of the plan's work, block the plan on it:
  `journal plan block <n> "<why>"` takes the waits of a task's block (the tasks skill); `journal plan unblock <n>` opens it.
- A plan's testing template, set on its plan page or by the setting plans.testing for new plans, says how its work is
  tested; it comes with the plan's start and with each task the plan hands you, and you are told when the user changes
  it: follow it, such as writing each task's tests and running them only at a phase's end.
- `journal plan cancel <n>` abandons it, with the tasks that belong to it alone; tasks another active plan has stay.
""", keywords=('plan', 'plans', 'roadmap', 'phases'), required_states=('following_plan',), commands=('plan',), events=(PlanApproved,))
