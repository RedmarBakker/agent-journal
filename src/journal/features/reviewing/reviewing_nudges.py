from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class ReviewingNudges:
    REVIEWER_WRITES = Nudge("reviewing", "reviewer_changes_no_file", "you are a reviewer: you change no file and merge nothing", "read, run the tests the proofs name and judge the changes, then give your report with journal review \"<one line per point>\"", repeat=Timeout.seconds(0))
    REPORT_REQUEST = Nudge("reviewing", "reviewer_gives_its_report", "your review is not given yet", "journal review \"<one line per point: 1 passed, or 2 short: why; then the tests you ran>\"", repeat=Timeout.seconds(0))
    REVIEW_UNDECIDED = Nudge("reviewing", "reviewer_could_not_decide", "reviewer {{reviewer}} could not decide worker {{n}} on task {{task}}:\n{{report}}", "decide the points it left: journal worker check {{n}} <point>, or --short \"<what is missing>\", then journal worker merge {{n}}", repeat=Timeout.seconds(0))
    REVIEWS_WAITING = Nudge("reviewing", "reviews_wait_for_a_reviewer", "reviews waiting for a reviewer: {{waiting}}; reviewers: {{reviewers}}", "add one with journal reviewer add when they pile up; journal reviewer list names them in their order", repeat=Timeout.seconds(300))
    REVIEW_FAILED = Nudge("reviewing", "review_failed", "the reviewer of worker {{n}} ended without a report: task {{task}} waits for your own check", "journal task show {{task}}, then journal worker check {{n}} <point>, or --short \"<what is missing>\"", repeat=Timeout.seconds(0))
