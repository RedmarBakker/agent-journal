from journal.features.feature import Feature
from journal.features.sequences.support.sequences_data_reader import SequencesDataReader
from journal.features.sequences.support.sequences_data import SequencesData
from journal.support.skill import Skill
from journal.features.sequences.commands.sequence_command import SequenceCommand
from journal.features.sequences.listeners.session_run_transfer import SessionRunTransfer
from journal.features.sequences.listeners.cancelled_row_run_end import CancelledRowRunEnd
from journal.features.sequences.listeners.deleted_row_run_end import DeletedRowRunEnd
from journal.features.sequences.listeners.deleted_sequence_run_end import DeletedSequenceRunEnd
from journal.features.sequences.listeners.record_run_changes import RecordRunChanges
from journal.features.sequences.listeners.step_command_match import StepCommandMatch
from journal.features.sequences.listeners.creation_start import CreationStart
from journal.features.sequences.sequences_conduct import SequencesConduct
from journal.features.sequences.seeds.builtin_sequences import BuiltinSequences
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.sequences_options import SequencesOptions
from journal.features.sequences.sequences_part import SequencesPart


class Sequences(Feature[SequencesData]):
    name = SequencesPart.name
    title = "Sequences"
    help = "Steps the agent follows one at a time."
    commands = (SequenceCommand,)
    listeners = (CreationStart, SessionRunTransfer, StepCommandMatch, DeletedSequenceRunEnd, DeletedRowRunEnd, CancelledRowRunEnd, RecordRunChanges)
    data = (SequencesDataReader,)
    conduct = (SequencesConduct,)
    seeds = (BuiltinSequences,)

    nudges = (SequencesNudges.PENDING_STEP, SequencesNudges.CURRENT_STEP, SequencesNudges.STEP_EDIT_BLOCK, SequencesNudges.STALE_STEP, SequencesNudges.SEQUENCE_PAUSED, SequencesNudges.SEQUENCE_ENDED, SequencesNudges.SEQUENCE_ABANDONED, SequencesNudges.SEQUENCE_CANNOT_FINISH, SequencesNudges.STEP_OMISSION, SequencesNudges.SEQUENCE_CANCELLED)

    options = (SequencesOptions.STALENESS_LIMIT, SequencesOptions.STEP_REPEAT_INTERVAL)

    skill = Skill("sequences", 'Follow a sequence of steps one at a time; load it when a sequence is run or written', """
# Sequences

Steps followed in order, one at a time. A running sequence stays with you through tasks, waits and new sessions
until its last step is done.

- `journal sequence run <n>` starts one and tells you step 1. Creating a plan starts Building a plan on its own.
- `journal sequence follow` takes the step in hand up: until you do, a write waits, while reads and journal commands
  go through. A command the step names, in backticks, also takes it up when you run it.
- `journal sequence next` when the step is done: you are given the next one, or that the sequence ended and what
  you were doing before it. A step never taken up cannot be moved on.
- A step taken up that stands for many writes holds the next write again: move it on, follow it again, or pause it.
- `journal sequence pause --why "<why>"` sets the run aside, its holds quiet; `journal sequence follow` resumes it.
- A sequence about a row ends only when the row is where it promises: Building a plan's last step waits for a ready
  plan. A row cancelled or deleted, or the sequence deleted, ends the run and you are informed.
- `journal sequence abandon --why "<why>"` names the steps it would leave undone; again with `--sure` it gives the run
  up and tells the user. Take the step up first.
- One started while another runs is followed first; when it ends, the other is announced again. Only the user's own
  words start a sequence by its trigger.
- A stop with a step open is shown the step once; a wait, an open question or a pending duty to the journal keeps it silent.
- `journal sequence create "<title>" --steps "first | second | third"` writes one; `--starts-on plan.created`
  makes a row you create start it on its own.
""", keywords=('sequence', 'sequences', 'steps'))
