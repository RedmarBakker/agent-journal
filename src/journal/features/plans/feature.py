from journal.features.feature import Feature
from journal.features.plans.support.plans_data_reader import PlansDataReader
from journal.features.plans.support.task_succession_reader import TaskSuccessionReader
from journal.features.plans.support.plans_data import PlansData
from journal.features.plans.listeners.plan_blockade import PlanBlockade
from journal.features.plans.listeners.clear_plan_waits import ClearPlanWaits
from journal.features.plans.listeners.count_plan_reviewers import CountPlanReviewers
from journal.support.skill import Skill
from journal.features.plans.commands.plan_command import PlanCommand
from journal.features.plans.listeners.advance_plan import AdvancePlan
from journal.features.plans.listeners.reopen_finished_plan import ReopenFinishedPlan
from journal.features.plans.listeners.plan_reopening import PlanReopening
from journal.features.plans.plans_conduct import PlansConduct
from journal.features.plans.seeds.closed_plans import ClosedPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.plans_ready import PlansReady
from journal.features.plans.states.plans_working import PlansWorking
from journal.features.plans.listeners.release_plan_waits import ReleasePlanWaits
from journal.features.plans.listeners.plan_testing_default import PlanTestingDefault
from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.plans_part import PlansPart


class Plans(Feature[PlansData]):
    name = PlansPart.name
    title = "Plans"
    help = "A plan is a goal, phases and the tasks under them, built with the user and started on their approval; following it, finishing one task starts the next."
    states = (PlansReady, PlansWorking, FollowingPlan)
    commands = (PlanCommand,)
    listeners = (PlanTestingDefault, PlanBlockade, ClearPlanWaits, ReleasePlanWaits, CountPlanReviewers, AdvancePlan, ReopenFinishedPlan, PlanReopening)
    conduct = (PlansConduct,)
    data = (PlansDataReader, TaskSuccessionReader)
    seeds = (ClosedPlans,)

    options = (PlansOptions.REVIEW_TOOL_USE_LIMIT, PlansOptions.TESTING)
    nudges = (PlansNudges.REVIEW_ENTRY_REQUEST, PlansNudges.REVIEW_ENTRY_BLOCK, PlansNudges.UNAPPROVED_PLAN, PlansNudges.APPROVED_UNSTARTED, PlansNudges.NEXT_PLAN_TASK, PlansNudges.PLAN_FINISHED, PlansNudges.PLAN_STALLED, PlansNudges.PLAN_POSTPONED, PlansNudges.PLAN_ABANDONED, PlansNudges.PLAN_APPROVED, PlansNudges.CHECKPOINT_PHASE_END, PlansNudges.PHASE_END, PlansNudges.PLAN_BLOCKED, PlansNudges.PLAN_REOPENED, PlansNudges.BUILDER_MODE, PlansNudges.PLAN_TESTING)

    skill = Skill("plans", 'Build and follow a plan of ordered tasks; load it when the user asks for a plan or a roadmap', """
# Plans

A plan is a goal, phases in order, and the tasks under each phase. It is built with the user, marked ready
by you, approved by them, and then followed: finishing one task starts the next until the last.

- `journal plan create "<title>" --brief "<goal>"` drafts it; `journal plan brief <n> "<goal>"` replaces the goal.
- `journal plan phase <n> "<title>" --when "<complete when>"` adds a phase, `--checkpoint` where the user
  should review before the plan continues. A checkpoint stops the plan only when auto mode is off; in auto mode the plan
  continues straight on.
- `journal plan add <n> "<task title>" --brief "<done when>"` files a task; `journal plan todos <n> <phase> <tasks…>`
  puts tasks under a phase by its number from 1.
- `journal plan ready <n>` when every phase has its tasks. Only the user approves, on the plan page or with
  `journal plan approve <n>`; you are informed, and `journal plan start <n>` begins its first task, and also continues past a checkpoint.
- Asked for a review of a plan: `journal plan review <n>` before the reviewers go out. In review it cannot be approved,
  and `journal plan ready <n>` waits until every subagent is back. Put what they find straight into the plan as tasks
  under its phases, then mark it ready again with `--changed "<what the round changed, in one line>"`: each round is stored on the
  plan, with its reviewers, the reports filed about the plan while it ran, and that line.
- `journal plan show <n>` lists its phases and tasks; `journal plan list` every plan; `journal plan pause <n>` puts it aside.
- A blocked task never blocks its plan: go on with the tasks that can be done. When every task left is blocked, the plan
  blocks itself and opens again when one opens. When one thing stops all of the plan's work, block the plan on it:
  `journal plan block <n> "<why>"`, with `--on question:N`, `--on task:N` or `--until "<command>"` as for a task, so it
  opens by itself; `journal plan unblock <n>` opens it by hand.
- `journal plan cancel <n>` abandons it, with the tasks that belong to it alone; tasks another active plan has stay.
""", keywords=('plan', 'plans', 'roadmap', 'phases'), required_states=('following_plan', 'orchestrating_plan'))
