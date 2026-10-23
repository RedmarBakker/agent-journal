from journal.support.timeout import Timeout

LIMIT_SECONDS = 900


def reminded(event, settings, limit_option, started_at) -> list[str]:
    said = []
    # @sin HandWrittenIntervalDetector
    if event.silence_seconds >= LIMIT_SECONDS:
        said.append("quiet")
    # @sin HandWrittenIntervalDetector
    if event.uses_unanswered >= settings.integer(limit_option):
        said.append("unanswered")
    # @sin HandWrittenIntervalDetector
    if event.time - started_at < settings.integer(limit_option) * 60:
        said.append("not yet")
    if Timeout.seconds(LIMIT_SECONDS).is_elapsed(event.silence_seconds):
        said.append("waited out with a Timeout")
    return said
