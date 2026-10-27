from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class DumpsNudges:
    DUMP_ARRIVAL = Nudge("dumps", "dump_arrived_file_it", "file dump {{n}} ({{count}}): `journal dump items {{n}}`", "log with `journal dump log`, ask only with `journal dump ask`", repeat=Timeout.seconds(300))
    DUMP_OPEN_REMINDER = Nudge("dumps", "dump_still_open_carry_on", "dump {{n}} is not filed; what is left: `journal dump items {{n}}`", "ask only what you cannot tell: `journal dump ask`", repeat=Timeout.seconds(0))
    DUMP_ANSWER = Nudge("dumps", "the_user_answered_on_the_dump", "dump {{n}}: to \"{{question}}\" the user answered {{answer}}", "act on it and log it on the dump", repeat=Timeout.seconds(0))
    DUMP_SUMMARY_REQUEST = Nudge("dumps", "dump_filed_sum_it_up", "dump {{n}} filed ({{outcome}}); sum it up, start nothing: `journal dump propose {{n}} '[{\"ask\": \"<question>\", \"label\": \"<button>\"}]' --summary \"<what you filed and where>\"`, `'[]'` for no buttons", "", repeat=Timeout.seconds(0))
    DUMP_STEP_CHOICE = Nudge("dumps", "the_user_chose_a_step", "the user chose {{label}} for dump {{n}}", "do that step and log it on the dump", repeat=Timeout.seconds(0))
    DUMP_HANDOVER = Nudge("dumps", "dump_left_to_you_finish_it", "the user left dump {{n}} to you", "take each next step yourself and log it with `journal dump log`", repeat=Timeout.seconds(0))
