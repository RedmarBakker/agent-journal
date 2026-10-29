from journal.support.timeout import Timeout


def test_a_span_is_elapsed_at_its_amount_and_exceeded_only_past_it():
    span = Timeout.seconds(30).started(100.0)
    assert not span.is_elapsed(129.0) and span.is_elapsed(130.0) and not span.is_exceeded(130.0) and span.is_exceeded(130.5)


def test_a_span_is_active_from_its_start_until_just_before_its_end():
    span = Timeout.seconds(30).started(100.0)
    assert not span.is_active(99.0) and span.is_active(100.0) and span.is_active(129.9) and not span.is_active(130.0)
