from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class DumpsNudges:
    DUMP_ARRIVAL = Nudge("dumps", "dump_arrived_file_it", "dump {{n}} has {{count}} to file: journal dump items {{n}}", "file it step by step, log each step with journal dump log, and ask only in the dump window", repeat=Timeout.seconds(300))
    DUMP_OPEN_REMINDER = Nudge("dumps", "dump_still_open_carry_on", "dump {{n}} is not filed yet", "journal dump items {{n}} shows what is left; ask only what you cannot tell, with journal dump ask", repeat=Timeout.seconds(0))
    DUMP_ANSWER = Nudge("dumps", "the_user_answered_on_the_dump", "the user answered on dump {{n}}: {{answer}}", "the question was: {{question}}", repeat=Timeout.seconds(0))
    DUMP_SUMMARY_REQUEST = Nudge("dumps", "dump_filed_sum_it_up", "dump {{n}} is filed ({{outcome}}) - sum it up for the user", """sum up what you filed and where in two or three lines, with any next step worth taking as a button on the dump: journal dump propose {{n}} '[{"ask": "Want me to plan the mobile layout?", "label": "Plan it"}]' --summary "<what you filed and where>", or '[]' for none. Start nothing yourself.""", repeat=Timeout.seconds(0))
    DUMP_STEP_CHOICE = Nudge("dumps", "the_user_chose_a_step", "the user chose {{label}} for dump {{n}}", "carry that step out, and log it on the dump.", repeat=Timeout.seconds(0))
    DUMP_HANDOVER = Nudge("dumps", "dump_left_to_you_finish_it", "the user left dump {{n}} to you: finish it", "take the next step yourself and log each on the dump", repeat=Timeout.seconds(0))
