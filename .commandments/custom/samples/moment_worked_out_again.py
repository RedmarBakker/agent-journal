def current_use_reads(messages, agent) -> tuple[int, ...]:
    # @sin MomentWorkedOutAgainDetector
    return tuple(m.row_id for m in messages if m.read_at and m.read_position == agent.tool_uses)


def line_use(entry, agent) -> bool:
    # @sin MomentWorkedOutAgainDetector
    return entry.data["tool_use"] == agent.tool_uses


def interval_end(agent, last_use: int, interval: int) -> bool:
    # @righteous MomentWorkedOutAgainDetector
    # @sin SpanWorkedOutByHandDetector
    return agent.tool_uses - last_use >= interval
