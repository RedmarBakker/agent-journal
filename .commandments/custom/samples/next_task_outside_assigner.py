class StopLines:
    def __init__(self, settings, tasks) -> None:
        self.settings, self.tasks = settings, tasks

    def next_line(self, agent):
        # @sin NextTaskOutsideAssignerDetector
        if self.settings.option(TasksOptions.AUTO):
            # @sin NextTaskOutsideAssignerDetector
            return self.tasks.next_open_task()
        # @righteous NextTaskOutsideAssignerDetector
        return self.settings.option(UpdatesOptions.AUTO)
