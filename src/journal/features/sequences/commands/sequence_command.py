from argparse import Namespace

from journal.console.command import Command
from journal.support.caller import Caller
from journal.events.announcer import Announcer
from journal.events.moments.sequence_abandoned import SequenceAbandoned
from journal.features.sequences.support.run_tracker import RunTracker
from journal.models.sequence import Sequence
from journal.models.support.sequence_step import SequenceStep
from journal.models.support.sequence_trigger import LINE_FORMS, SequenceTrigger
from journal.models.support.sequence_trigger_type import SequenceTriggerType
from journal.features.sequences.support.step_argument import STEPS_DESTINATION, StepArgument
from journal.features.sequences.support.step_guard_argument import StepGuardArgument
from journal.repositories.scope import Scope
from journal.support.sequence_run import SequenceRun
from journal.support.rejection import Rejection
from journal.repositories.sequences import Sequences
from journal.features.sequences.sequences_nudges import SequencesNudges


class SequenceCommand(Command):
    noun = "sequence"
    uncut_verbs = frozenset({"run", "follow", "next"})

    def __init__(self, sequences: Sequences, active: RunTracker, scope: Scope, announcer: Announcer) -> None:
        self.sequences, self.running, self.scope, self.announcer = sequences, active, scope, announcer

    def arguments(self, verbs) -> None:
        creation = self.verb(verbs, "create", "write a sequence of steps and what starts it")
        creation.add_argument("title")
        self.step_arguments(creation)
        editing = self.verb(verbs, "edit", "write a sequence's steps anew, each with its guards, or its triggers anew, or both")
        editing.add_argument("n", type=int)
        self.step_arguments(editing)
        self.verb(verbs, "run", "start a sequence at its first step").add_argument("n", type=int)
        self.verb(verbs, "follow", "take the step in hand up, and resume a paused run")
        self.verb(verbs, "next", "the step in hand is done; the next one, or the end")
        self.verb(verbs, "pause", "set the run aside, its holds quiet until it is followed again").add_argument("--why", required=True)
        abandon = self.verb(verbs, "abandon", "give the run up, its remaining steps undone; the user is told")
        abandon.add_argument("--why", required=True)
        abandon.add_argument("--sure", action="store_true", help="go through, once the steps it skips are read")
        self.verb(verbs, "list", "every sequence")
        self.verb(verbs, "show", "a sequence's steps, each with its guards").add_argument("n", type=int)

    @staticmethod
    def step_arguments(parser) -> None:
        parser.add_argument("--steps", default="", help="steps separated by |, each its instructions with file edits allowed")
        parser.add_argument("--step", action=StepArgument, nargs=None, help="a step, 'title | instructions'; the guards after it are its own; give one --step per step, in order")
        parser.add_argument("--hold-edits", action=StepGuardArgument, nargs=0, help="file edits wait while the step before it is in hand")
        parser.add_argument("--allow-commands", action=StepGuardArgument, help="a pattern of a shell line the step before it lets through while its file edits wait")
        parser.add_argument("--trigger", action="append", default=[], help=f"what starts it on its own, one --trigger each: {LINE_FORMS}")

    @staticmethod
    def argument_steps(args: Namespace) -> tuple[SequenceStep, ...]:
        return getattr(args, STEPS_DESTINATION, None) or tuple(SequenceStep(instructions=text.strip()) for text in args.steps.split("|") if text.strip())

    @staticmethod
    def argument_triggers(args: Namespace) -> tuple[SequenceTrigger, ...]:
        return tuple(SequenceTrigger.line_trigger(line) for line in args.trigger)

    def required_steps(self, args: Namespace) -> tuple[SequenceStep, ...]:
        steps = self.argument_steps(args)
        if not steps:
            raise Rejection("a sequence has at least one step: give --step 'title | instructions' for each, or --steps 'first | second'")
        return steps

    def create(self, args: Namespace, caller: Caller) -> int:
        steps = self.required_steps(args)
        sequence = self.sequences.save(Sequence(title=args.title, steps=steps, triggers=self.argument_triggers(args)), caller.actor)
        print(f"sequence {sequence.id}: {sequence.title}, {len(steps)} steps")
        return 0

    def edit(self, args: Namespace, caller: Caller) -> int:
        current = self.sequences.find(args.n).unlocked()
        steps, triggers = self.argument_steps(args), self.argument_triggers(args)
        if not steps and not triggers:
            raise Rejection("give the steps anew with --step or --steps, the triggers anew with --trigger, or both")
        sequence = self.sequences.save(current.with_(steps=steps or current.steps, triggers=triggers or current.triggers), caller.actor)
        print("\n".join(self.sequence_lines(sequence)))
        return 0

    @staticmethod
    def step_line(number: int, step: SequenceStep) -> str:
        guards = "file edits wait" if not step.file_edits_allowed else "file edits allowed"
        allowed = f", lets through {', '.join(step.allowed_commands)}" if step.allowed_commands else ""
        return f"{number}. {step.heading()} ({guards}{allowed}): {step.instructions}"

    def run(self, args: Namespace, caller: Caller) -> int:
        sequence = self.sequences.find(args.n)
        agent = self.running.sessions.agent(caller.agent_session, self.scope.id)
        top = self.running.states.stack(agent).top()
        if not top.takes_pushes():
            raise Rejection(f"you are in {(top.title or top.name).lower()} now: start sequence {sequence.id} once that is over")
        print(self.running.start(sequence, caller.agent_session, self.scope.id) or f"sequence {sequence.id} is running already")
        return 0

    def follow(self, args: Namespace, caller: Caller) -> int:
        self.current_run(caller)
        run = self.running.follow(caller.agent_session, self.scope.id)
        print(self.running.line(self.running.sessions.agent(caller.agent_session, self.scope.id), SequencesNudges.CURRENT_STEP.create(n=run.sequence_id, step=run.step + 1, text=run.text)))
        return 0

    def next(self, args: Namespace, caller: Caller) -> int:
        run = self.current_run(caller)
        if not run.adopted_at:
            raise Rejection(f"step {run.step + 1} of sequence {run.sequence_id} was never taken up: `journal sequence follow` first")
        print(self.running.next(caller.agent_session, self.scope.id))
        return 0

    def pause(self, args: Namespace, caller: Caller) -> int:
        self.current_run(caller)
        run = self.running.pause(caller.agent_session, self.scope.id, args.why)
        print(f"sequence {run.sequence_id} paused at step {run.step + 1}: {args.why}. `journal sequence follow` resumes it")
        return 0

    def abandon(self, args: Namespace, caller: Caller) -> int:
        run = self.current_run(caller)
        if not run.adopted_at:
            raise Rejection(f"step {run.step + 1} of sequence {run.sequence_id} was never taken up: `journal sequence follow` first, then abandon it if it cannot be done")
        skipped = "; ".join(f"{run.step + i + 1}. {step.instructions}" for i, step in enumerate(run.skipped))
        if not args.sure:
            raise Rejection(f"abandoning sequence {run.sequence_id}, {run.title}, leaves undone: {skipped}. again with --sure to go through")
        run, line = self.running.abandon(caller.agent_session, self.scope.id, args.why)
        self.announcer.announce(SequenceAbandoned(environment_id=self.scope.id, session=caller.agent_session, sequence_id=run.sequence_id, title=run.title, step=run.step, explanation=args.why, skipped=skipped))
        print(line)
        return 0

    def current_run(self, caller: Caller) -> SequenceRun:
        run = self.running.current(caller.agent_session, self.scope.id)
        if run is None:
            raise Rejection("no sequence is running")
        return run

    def show(self, args: Namespace, caller: Caller) -> int:
        print("\n".join(self.sequence_lines(self.sequences.find(args.n))))
        return 0

    def sequence_lines(self, sequence: Sequence) -> list[str]:
        starts = f"starts on {', '.join(trigger.line() for trigger in sequence.triggers)}" if sequence.triggers else "starts by hand only"
        return [f"sequence {sequence.id}: {sequence.title}, {starts}", *(self.step_line(i, step) for i, step in enumerate(sequence.steps, 1))]

    def list(self, args: Namespace, caller: Caller) -> int:
        for sequence in self.sequences.all():
            starts = f", starts on {self.triggers_summary(sequence)}" if sequence.triggers else ""
            print(f"{sequence.id:>4}  {sequence.title} ({len(sequence.steps)} steps{starts})")
        return 0

    @staticmethod
    def triggers_summary(sequence: Sequence) -> str:
        phrases = [trigger for trigger in sequence.triggers if trigger.trigger_type == SequenceTriggerType.PHRASE]
        lines = [trigger.line() for trigger in sequence.triggers if trigger.trigger_type != SequenceTriggerType.PHRASE]
        counted = [phrases[0].line()] if len(phrases) == 1 else [f"{len(phrases)} phrases"] if phrases else []
        return ", ".join([*lines, *counted])
