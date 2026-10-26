from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class SequencesNudges:
    """The nudges of the sequences feature."""

    PENDING_STEP = Nudge("sequences", "step_to_follow", "sequence {{n}}, step {{step}}: {{text}}", "`journal sequence follow`, then `journal sequence next` when it is done", repeat=Timeout.seconds(0))
    CURRENT_STEP = Nudge("sequences", "following_the_step", "following sequence {{n}}, step {{step}}: {{text}}", "`journal sequence next` when it is done", repeat=Timeout.seconds(0))
    STEP_EDIT_BLOCK = Nudge("sequences", "write_held_for_the_step", "a write waits for sequence {{n}}, step {{step}}: {{text}}", "`journal sequence follow`, or `journal sequence pause --why \"<why>\"`", repeat=Timeout.seconds(0))
    STEP_EDITS_WAIT = Nudge("sequences", "file_edits_wait_for_the_step", "step {{step}} of sequence {{n}}, {{heading}}, lets no file edit through", "finish it first with `journal sequence next`; it lets reads and journal commands through{{allowed}}", repeat=Timeout.seconds(0))
    SEQUENCE_PAUSED = Nudge("sequences", "sequence_paused", "sequence {{n}} is paused at step {{step}}: {{why}}", "`journal sequence follow` resumes it", repeat=Timeout.seconds(0))
    SEQUENCE_ENDED = Nudge("sequences", "sequence_ended", "sequence {{n}} ran its last step", repeat=Timeout.seconds(0))
    SEQUENCE_ABANDONED = Nudge("sequences", "sequence_abandoned", "sequence {{n}} abandoned", repeat=Timeout.seconds(0))
    SEQUENCE_CANNOT_FINISH = Nudge("sequences", "sequence_cannot_finish", "sequence {{n}} ended: {{why}}", repeat=Timeout.seconds(0))
    STEP_OMISSION = Nudge("sequences", "the_user_skipped_a_step", "the user skipped step {{step}} of sequence {{n}}", repeat=Timeout.seconds(0))
    SEQUENCE_CANCELLED = Nudge("sequences", "the_user_ended_the_sequence", "the user ended sequence {{n}}", repeat=Timeout.seconds(0))
