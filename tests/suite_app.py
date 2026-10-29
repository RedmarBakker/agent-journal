from journal.app import App
from journal.support.listener_queue import ListenerQueue
from tests.suite_console import SuiteConsole


class SuiteApp(App):
    """The journal as the tests boot it: its console waits for the work a command leaves for after its answer."""

    def console(self) -> SuiteConsole:
        return SuiteConsole(super().console(), self.container.get(ListenerQueue))
