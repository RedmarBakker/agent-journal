def test_panic_watch_line(lines):
    # @sin NudgeWordsInTestDetector
    line = "create a panic watch: a CronCreate job every 15 minutes"
    assert line in lines
