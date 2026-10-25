from journal.features.plans.support.plan_testing import PlanTesting
from journal.models.plan import Plan
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.plans import Plans


class PhaseTesting:
    """The commands a plan's testing template runs at each phase end, and, once a phase has ended and the next has not begun, those whose newest run has not passed since the phase's last task closed: while any is left the next phase does not start."""

    def __init__(self, testing: PlanTesting, plans: Plans, outputs: CommandOutputs) -> None:
        self.testing, self.plans, self.outputs = testing, plans, outputs

    def commands(self, plan: Plan) -> tuple[str, ...]:
        return tuple(command for template in self.testing.chosen(plan) for command in template.commands)

    def unpassed(self, plan: Plan) -> tuple[str, ...]:
        commands = self.commands(plan)
        ended = self.plans.ended_phase(plan) if commands else None
        if ended is None:
            return ()
        closed_at = self.plans.phase_closed_at(ended.phase)
        return tuple(command for command in commands if not self.has_passed(command, closed_at))

    def has_passed(self, command: str, after: float) -> bool:
        run = self.outputs.last_run(command)
        return run is not None and run.status == 0 and run.update_time.timestamp() > after

    def refusal(self, plan: Plan) -> str:
        unpassed = self.unpassed(plan)
        return f"plan {plan.id}'s next phase starts once its testing template's commands pass after the last phase's last task: run {' and '.join(unpassed)}" if unpassed else ""
