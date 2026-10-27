from journal.models.command_output import CommandOutput
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.tasks import TEST_LINK, Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class TaskTestRuns:
    """The tasks waiting in testing on a run: attached to it, and settled once the run has ended: each completes when the run passed, and is in progress again, the failure named to its agent, when it did not."""

    def __init__(self, tasks: Tasks, links: Links, time_source: TimeSource) -> None:
        self.tasks, self.links, self.time_source = tasks, links, time_source

    def attach(self, tasks: list[Task], output: CommandOutput, actor: Actor) -> None:
        for task in tasks:
            self.links.linked(Ref.build(task), Ref.build(output), TEST_LINK, actor)
        if output.is_resolved():
            self.finish_tests(output, actor)

    def finish_tests(self, output: CommandOutput, actor: Actor) -> None:
        moment = self.time_source.moment()
        for ref in self.links.ref_sources(Ref.build(output), TEST_LINK):
            task = self.tasks.find(ref.id)
            if not task.is_testing():
                continue
            result = task.test_passed(moment, output.outcome()) if output.is_success() else task.test_failed(moment, output.row_id, output.outcome())
            self.tasks.save(result, actor)
