from journal.support.card_family import CardFamily
from journal.support.mark_kind import MarkKind
from journal.support.mark_kinds import JOURNAL
from journal.support.card_kind import CardKind
from journal.features.feature import Feature
from journal.features.sequences.support.sequences_data_reader import SequencesDataReader
from journal.features.sequences.support.sequences_data import SequencesData
from journal.support.skill import Skill
from journal.features.sequences.commands.sequence_command import SequenceCommand
from journal.features.sequences.listeners.session_run_transfer import SessionRunTransfer
from journal.features.sequences.listeners.cancelled_row_run_end import CancelledRowRunEnd
from journal.features.sequences.listeners.deleted_row_run_end import DeletedRowRunEnd
from journal.features.sequences.listeners.deleted_sequence_run_end import DeletedSequenceRunEnd
from journal.features.sequences.listeners.run_start_card import RunStartCard
from journal.features.sequences.listeners.run_step_card import RunStepCard
from journal.features.sequences.listeners.run_end_card import RunEndCard
from journal.features.sequences.listeners.run_skip_card import RunSkipCard
from journal.features.sequences.listeners.run_cancel_card import RunCancelCard
from journal.features.sequences.listeners.step_command_match import StepCommandMatch
from journal.features.sequences.listeners.creation_start import CreationStart
from journal.features.sequences.listeners.review_start import ReviewStart
from journal.features.sequences.listeners.prompt_phrase_start import PromptPhraseStart
from journal.features.sequences.listeners.message_phrase_start import MessagePhraseStart
from journal.features.sequences.listeners.call_start import CallStart
from journal.features.sequences.listeners.abandoned_run_card import AbandonedRunCard
from journal.features.sequences.sequences_conduct import SequencesConduct
from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.sequences.seeds.builtin_sequences import BuiltinSequences
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.sequences_options import SequencesOptions
from journal.features.sequences.sequences_part import SequencesPart


class Sequences(Feature[SequencesData]):
    name = SequencesPart.name
    card_families = (CardFamily("sequences", "Sequences", "list", JOURNAL),)
    card_kinds = (MarkKind(CardKind.SEQUENCES, "Sequences starting and finishing", "sequences"), MarkKind(CardKind.SEQUENCE_STEPS, "Every step of a sequence", "sequences", main=False, shown=False),)
    title = "Sequences"
    help = "Steps the agent follows one at a time."
    commands = (SequenceCommand,)
    listeners = (CreationStart, ReviewStart, PromptPhraseStart, MessagePhraseStart, CallStart, SessionRunTransfer, StepCommandMatch, DeletedSequenceRunEnd, DeletedRowRunEnd, CancelledRowRunEnd, RunStartCard, RunStepCard, RunSkipCard, RunCancelCard, RunEndCard, AbandonedRunCard)
    data = (SequencesDataReader,)
    states = (FollowingSequence,)
    conduct = (SequencesConduct,)
    seeds = (BuiltinSequences,)

    nudges = (SequencesNudges.PENDING_STEP, SequencesNudges.CURRENT_STEP, SequencesNudges.STEP_EDIT_BLOCK, SequencesNudges.STEP_EDITS_WAIT, SequencesNudges.SEQUENCE_PAUSED, SequencesNudges.SEQUENCE_ENDED, SequencesNudges.SEQUENCE_ABANDONED, SequencesNudges.SEQUENCE_CANNOT_FINISH, SequencesNudges.STEP_OMISSION, SequencesNudges.SEQUENCE_CANCELLED)

    options = (SequencesOptions.STEP_REPEAT_INTERVAL,)

    skill = Skill("sequences", 'Follow a sequence of steps one at a time; load it when a sequence is run or written', """
# Sequences

Steps followed in order, one at a time. A running sequence stays with you through tasks, waits and new sessions
until its last step is done.

- `journal sequence run <n>` starts one and tells you step 1. Creating a plan starts Building a plan on its own.
- `journal sequence follow` takes the step in hand up: until you do, a write and a command that runs anything but a read
  wait, while reads, journal commands and a subagent's dispatch go through. A command the step names, in backticks, also takes it up when you run it.
- `journal sequence next` when the step is done: you are given the next one, or that the sequence ended and what
  you were doing before it. A step never taken up cannot be moved on.
- `journal sequence pause --why "<why>"` sets the run aside, its holds quiet; `journal sequence follow` resumes it.
- A sequence about a row ends only when the row is where it promises: Building a plan's last step waits for a ready
  plan. A row cancelled or deleted, or the sequence deleted, ends the run and you are informed.
- `journal sequence abandon --why "<why>"` names the steps it would leave undone; again with `--sure` it gives the run
  up and tells the user. Take the step up first.
- Sequences stack: one started while another runs is the top, and only the top is held to and followed, moved on
  or abandoned; when it ends, the one beneath is announced again, its step taken up as it was, and carries on. Only the user's own
  words start a sequence by its trigger.
- A stop with a step open is shown the step once; a wait, an open question or a pending duty to the journal keeps it silent.
- `journal sequence create "<title>" --steps "first | second | third"` writes one. A step with a title and guards is
  `--step "<title> | <instructions>"`, followed by `--hold-edits` when file edits wait while it is in hand and
  `--allow-commands '<pattern>'` for each shell line it lets through; reads and journal commands always go through.
- `--trigger` starts it on its own, one each: `row:plan.created` when a row you create is made, `phrase:'<words>'` when
  the user's message is those words, `command:'<pattern>'` when a shell line matches, `file:'<glob>'` when a file is
  edited, `file-text:'<glob>':'<text>'` when an edit's new text holds the text, `tool:<name>:'<pattern>'` when a tool's
  input matches. Only the main agent's own actions start one; a worker's or a subagent's never do.
- `journal sequence edit <n>` writes the steps or the triggers anew the same way, and `journal sequence show <n>` lists
  its triggers and its steps with their guards.
""", keywords=('sequence', 'sequences', 'steps'), commands=('sequence',))
