from journal.engine.nudge import Nudge
from journal.features.dumps.commands.dump_command import DumpCommand
from journal.features.dumps.states.sorting_dump import SortingDump
from journal.features.feature import Feature
from journal.features.dumps.dumps_conduct import DumpsConduct
from journal.features.dumps.support.dumps_data_reader import DumpsDataReader
from journal.features.dumps.support.dumps_data import DumpsData
from journal.support.skill import Skill


class DumpsFeature(Feature[DumpsData]):
    name = "dumps"
    title = "Dumps"
    help = "The agent sorts files you drop together by subject and files each as a row of its own."
    commands = (DumpCommand,)
    states = (SortingDump,)
    data = (DumpsDataReader,)
    conduct = (DumpsConduct,)

    DUMP_ARRIVAL = Nudge(name, "dump_arrived_file_it", "dump {{n}} has {{count}} to file: journal dump items {{n}}", "file it step by step, log each step with journal dump log, and ask only in the dump window", repeat_interval=300)
    DUMP_OPEN_REMINDER = Nudge(name, "dump_still_open_carry_on", "dump {{n}} is not filed yet", "journal dump items {{n}} shows what is left; ask only what you cannot tell, with journal dump ask", repeat_interval=0)
    DUMP_ANSWER = Nudge(name, "the_user_answered_on_the_dump", "the user answered on dump {{n}}: {{answer}}", "the question was: {{question}}", repeat_interval=0)
    DUMP_SUMMARY_REQUEST = Nudge(name, "dump_filed_sum_it_up", "dump {{n}} is filed ({{outcome}}) - sum it up for the user", """sum up what you filed and where in two or three lines, with any next step worth taking as a button on the dump: journal dump propose {{n}} '[{"ask": "Want me to plan the mobile layout?", "label": "Plan it"}]' --summary "<what you filed and where>", or '[]' for none. Start nothing yourself.""", repeat_interval=0)
    DUMP_STEP_CHOICE = Nudge(name, "the_user_chose_a_step", "the user chose {{label}} for dump {{n}}", "carry that step out, and log it on the dump.", repeat_interval=0)
    DUMP_HANDOVER = Nudge(name, "dump_left_to_you_finish_it", "the user left dump {{n}} to you: finish it", "take the next step yourself and log each on the dump", repeat_interval=0)
    nudges = (DUMP_ARRIVAL, DUMP_OPEN_REMINDER, DUMP_ANSWER, DUMP_SUMMARY_REQUEST, DUMP_STEP_CHOICE, DUMP_HANDOVER)

    skill = Skill("dumps", 'File what the user dropped in a dump: sort the material by subject into rows of their own; load it when a dump arrives', """
# Dumps

A dump holds pasted text and dropped files; each is an item. Sort the material by subject: one document per subject,
named for what it is about, never after the file it was received in. One dump is worked at a time; the next waits until it closes.

1. `journal dump items <n>` lists the status of every item.
2. Read each item, then `journal dump note <n> <item> "<what it is>"`.
3. Write what it becomes (a doc, a plan, a task), then
   `journal dump filed <n> <item> "<what it did>" --refs "doc:2, plans:1" --added "doc:3"` (`--added` names rows you wrote
   without being asked, also listed in refs), or `journal dump failed <n> <item> "<why>"`. What you file is in the journal at once.
4. `journal dump name <n> "<name>"` names the dump for what its items are about; `journal dump log <n> "<status>"`
   (at most 40 characters, `--detail` for the sentence) shows the user what you are doing.
5. `journal dump split <n> "<part>, <part>"` splits pasted text into parts, one item each.
6. `journal dump ask <n> "<question>" --guesses "a|b"` asks the user in the dump window; they answer there.
   What the user writes in the dump reaches you as a message about it: answer with `journal dump reply <n> "<text>"`
   (at most 600 characters), never in the chat; the chat shows a small mark that you answered in the dump.
7. The dump closes by itself once every item is filed or failed. Then sum it up with
   `journal dump propose <n> '[{"ask": "Want me to plan the mobile layout?", "label": "Plan it"}]' --summary "<what you filed and where>"`
   (`'[]'` for no next step) and start nothing yourself.
8. Only the user stops, removes, or chooses a next step. `journal dump reopen <n>` works a closed dump again.
""", keywords=("dump", "dumps", "dumped"))
