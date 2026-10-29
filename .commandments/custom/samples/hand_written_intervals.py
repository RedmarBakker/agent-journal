from journal.support.timeout import Timeout

LIMIT_SECONDS = 900


def reminded(event, settings, limit_option, started_at) -> list[str]:
    lines = []
    # @sin HandWrittenIntervalDetector
    if event.silence_seconds >= LIMIT_SECONDS:
        lines.append("quiet")
    # @sin HandWrittenIntervalDetector
    if event.uses_unanswered >= settings.integer(limit_option):
        lines.append("unanswered")
    # @sin HandWrittenIntervalDetector
    # @sin SpanWorkedOutByHandDetector
    if event.time - started_at < settings.integer(limit_option) * 60:
        lines.append("not yet")
    if Timeout.seconds(LIMIT_SECONDS).is_elapsed(event.silence_seconds):
        lines.append("waited out with a Timeout")
    return lines
