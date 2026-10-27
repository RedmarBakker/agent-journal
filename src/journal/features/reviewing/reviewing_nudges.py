from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class ReviewingNudges:
    REVIEWER_WRITES = Nudge("reviewing", "reviewer_changes_no_file", "you are a reviewer: change and merge nothing", "run the proofs' tests, then `journal review \"<one line per point>\"`", repeat=Timeout.seconds(0))
    REPORT_REQUEST = Nudge("reviewing", "reviewer_gives_its_report", "give your review: `journal review \"<one line per point: 1 passed, or 2 short: why; then the tests you ran>\"`", "", repeat=Timeout.seconds(0))
    REVIEW_UNDECIDED = Nudge("reviewing", "reviewer_could_not_decide", "{{reviewer}} left worker {{n}} undecided: {{report|cap=600}}", "check each point: `journal worker check {{n}} <point>`", repeat=Timeout.seconds(0), longest_characters=711, longest_reason="it contains the reviewer's report")
    REVIEWS_WAITING = Nudge("reviewing", "reviews_wait_for_a_reviewer", "reviews waiting: {{waiting|cap=15}}; reviewers: {{reviewers|cap=15}}", "if too many wait, add a reviewer: `journal reviewer add`", repeat=Timeout.seconds(300))
    REVIEW_FAILED = Nudge("reviewing", "review_failed", "worker {{n}}'s reviewer gave no report", "read `journal task show {{task}}`, then `journal worker check {{n}} <point>`", repeat=Timeout.seconds(0))
