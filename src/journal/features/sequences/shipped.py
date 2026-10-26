from journal.events.rows.plan_review_started import PlanReviewStarted
from journal.models.sequence import Sequence
from journal.models.support.sequence_step import SequenceStep
from journal.models.support.sequence_trigger import SequenceTrigger

PLAIN_WRITING = "Write what this asks for in the user's own language in plain words, plain English or plain Dutch as the user speaks, never in the voice you speak in. "

UPDATE_PHRASES = ("give me an update", "an update please", "any updates", "status update", "tldr", "tl;dr", "catch me up", "what happened since",
                "geef me een update", "update graag", "nog updates", "statusupdate", "stand van zaken", "praat me bij", "bijpraten", "wat is er gebeurd")
INSTRUCTION_CHECK_PHRASES = ("check the instruction files", "check agents.md", "check claude.md", "contradictions in the instructions",
                  "controleer de instructiebestanden", "controleer agents.md", "tegenstrijdigheden in de instructies")

PLAN_BUILDING = Sequence(
    title="Building a plan",
    triggers=(SequenceTrigger.row("plan.created"),),
    end_condition=("ready", "approved", "started", "done"),
    steps=(
        SequenceStep(title="Agree on the goal", instructions=PLAIN_WRITING + "Agree on the plan's goal: settle with the user what is true when the plan is done, and put it in the plan's brief with `journal plan brief <plan n> \"<goal>\"`", file_edits_allowed=False),
        SequenceStep(title="Add the phases", instructions="Add the plan's phases in order with `journal plan phase <plan n> \"<title>\" --when \"<complete when>\"`, and `--checkpoint` where the user should look before it goes on", file_edits_allowed=False),
        SequenceStep(title="File the tasks", instructions="File the tasks with `journal plan add <plan n> \"<title>\" --brief \"<done when>\"` and put each under its phase with `journal plan todos <plan n> <phase> <tasks>`; one task per step a person could check", file_edits_allowed=False),
        SequenceStep(title="Mark the plan ready", instructions="When every phase has its tasks, `journal plan ready <plan n>` and tell the user in one line it is ready on the plan page. Only they approve it; you are told when they do, and `journal plan start <plan n>` then, never before", file_edits_allowed=False),
    ),
)
UPDATE_WRITING = Sequence(
    title="Writing an update",
    triggers=tuple(SequenceTrigger.phrase(text) for text in UPDATE_PHRASES),
    steps=(
        SequenceStep(title="See what the update covers", instructions=PLAIN_WRITING + "See what the update covers with `journal report changes`: the rows since the last update the user read, by section; read any row you do not remember before you sum it up", file_edits_allowed=False),
        SequenceStep(title="Write the update", instructions="Write the update with `journal report recap \"<one or two sentences>\"`: what got done and what waits on the user, in plain words; the journal puts the rows under it and docks it at the bottom of the chat. Take out what does not belong with `journal report drop <n>` and add a note with `journal report note <n> \"<text>\"`", file_edits_allowed=False),
        SequenceStep(title="Tell the user", instructions="Tell the user in one short line that the update is docked above the chat, with the report's reference on a line of its own, like report 3; talk about the work, never about rows or commands", file_edits_allowed=False),
    ),
)
PLAN_REVIEW_APPLYING = Sequence(
    title="Applying a plan's reviews",
    triggers=(SequenceTrigger.row(PlanReviewStarted.moment),),
    end_condition=("ready", "approved", "started", "done"),
    steps=(
        SequenceStep(title="Wait for the reviewers", instructions=PLAIN_WRITING + "Send the plan's reviewers and read what each finds as it comes back, noting every finding with the phase it belongs in; you may work on other files meanwhile. The step moves on by itself once the last reviewer is back", ending_moment="plan.reviewed"),
        SequenceStep(title="Put the findings into the plan", instructions="Put each finding into the plan: a new task with `journal plan add <plan n> \"<title>\" --brief \"<done when>\"` placed with `journal plan todos <plan n> <phase> <tasks>`, or a wider brief on the task it belongs to with `journal task edit <n> --brief \"<brief>\"`. File edits wait until this step is done; plan, task, report and reading commands go through", file_edits_allowed=False),
        SequenceStep(title="Ready the plan", instructions="Compile the findings into one report linked to the plan, written by phase to a markdown file with a summary first: `journal report create \"<title>\" --abstract \"<what it found, in one short line>\" --file <path> --about plans:<plan n>`. Then `journal plan ready <plan n> --changed \"<what the round changed, in one line>\"`, which ends the sequence, and tell the user in one or two plain lines what the reviews found, with the report's reference on a line of its own, like report 3", ending_moment="plan.readied"),
    ),
)
INSTRUCTION_FILES_CHECK = Sequence(
    title="Checking the instruction files",
    triggers=tuple(SequenceTrigger.phrase(text) for text in INSTRUCTION_CHECK_PHRASES),
    steps=(
        SequenceStep(title="Read the instruction files", instructions=PLAIN_WRITING + "Read AGENTS.md and CLAUDE.md at the project root and the journal's block at the head of each, narrowly: grep for the headings, then sed the sections you need; note every place where two of them tell an agent opposite things, with the file and line on both sides", file_edits_allowed=False),
        SequenceStep(title="Write the report", instructions="Write what you found as a report from a markdown file with `journal report create \"Instruction files checked\" --abstract \"<what it found, in one short line>\" --file <path>`: each contradiction with both sides quoted, and the fix you propose for it; never edit the files", file_edits_allowed=True),
        SequenceStep(title="Tell the user", instructions="Tell the user in one short line how many contradictions you found, with the report's reference on a line of its own, like report 3; the user decides which fixes to make", file_edits_allowed=False),
    ),
)
DOCUMENT_SORTING = Sequence(
    title="Filing a document that is already written",
    triggers=(SequenceTrigger.row("doc.created"),),
    steps=(
        SequenceStep(title="Check the document", instructions="Check the document you filed reads as you meant: `journal doc show <doc n>` lists its sections, one for each ## heading of the file", file_edits_allowed=False),
        SequenceStep(title="Tell the user", instructions="Tell the user in one or two plain lines what the document concludes, then its reference on a line of its own, like doc 41, never in backticks", file_edits_allowed=False),
    ),
)
RETIRED = ("Sort dumped files",)
SHIPPED = (PLAN_BUILDING, PLAN_REVIEW_APPLYING, UPDATE_WRITING, INSTRUCTION_FILES_CHECK, DOCUMENT_SORTING)
