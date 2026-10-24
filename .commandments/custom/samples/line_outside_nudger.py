class Greeter:
    """A sample for line-outside-nudger: the first line skips the Nudger, the second goes through it."""

    def __init__(self, nudger, supervisor, nudge) -> None:
        self.nudger, self.supervisor, self.nudge = nudger, supervisor, nudge

    def typed(self, environment_id: int) -> None:
        self.supervisor.type(environment_id, self.nudge.rendered())

    def delivered(self, agent, environment_id: int) -> None:
        line = self.nudger.deliver(agent, self.nudge)
        if line:
            self.supervisor.type(environment_id, line)
