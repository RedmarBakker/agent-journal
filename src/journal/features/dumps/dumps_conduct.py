from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.dump_arrived import DumpArrived
from journal.features.dumps.states.sorting_dump import SortingDump, item_count
from journal.features.dumps.dumps_nudges import DumpsNudges


class DumpsConduct(Conduct):
    """The dumps feature's conduct in every state: a dump the user drops pushes SortingDump over whatever the agent was doing, and says how many items are waiting."""

    def on_dump_arrived(self, event: DumpArrived, settings: Settings) -> Transition:
        if not event.user_origin:
            return self.none()
        return self.push(SortingDump(dump_id=event.dump_id)).typing(DumpsNudges.DUMP_ARRIVAL.create(n=event.dump_id, count=item_count(event.waiting)))
