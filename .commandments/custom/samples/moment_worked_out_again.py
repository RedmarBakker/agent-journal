def read_this_use(messages, agent) -> tuple[int, ...]:
    # @sin MomentWorkedOutAgainDetector
    return tuple(m.row_id for m in messages if m.read_at and m.read_position == agent.tool_uses)


def told_at(entry, agent) -> bool:
    # @sin MomentWorkedOutAgainDetector
    return entry.data["tool_use"] == agent.tool_uses


def interval_passed(agent, last_use: int, every: int) -> bool:
    # @righteous MomentWorkedOutAgainDetector
    return agent.tool_uses - last_use >= every
