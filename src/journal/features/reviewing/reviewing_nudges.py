from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


class ReviewingNudges:
    REVIEWER_WRITES = Nudge("reviewing", "reviewer_changes_no_file", "you are a reviewer: you change no file and merge nothing", "read, run the tests the proofs name and judge the changes, then give your report with journal review \"<one line per point>\"", repeat=Timeout.seconds(0))
    REVIEW_OWED = Nudge("reviewing", "reviewer_gives_its_report", "your review is not given yet", "journal review \"<one line per point: 1 passed, or 2 short: why; then the tests you ran>\"", repeat=Timeout.seconds(0))
    WORK_REVIEWED = Nudge("reviewing", "work_reviewed", "reviewer {{reviewer}} reviewed worker {{n}}, {{name}}, on task {{task}}:\n{{report}}", "send what is short back with journal worker check {{n}} <point> --short \"<what is missing>\", or check each point with journal worker check {{n}} <point> and merge with journal worker merge {{n}}", repeat=Timeout.seconds(0))
    REVIEW_FAILED = Nudge("reviewing", "review_failed", "the reviewer of worker {{n}}, {{name}}, ended without a report: task {{task}} waits for your own check", "journal task show {{task}}, then journal worker check {{n}} <point>, or --short \"<what is missing>\"", repeat=Timeout.seconds(0))
