from dataclasses import dataclass
from collections.abc import Callable

from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.features.workers.support.worker_runner import WorkerRunner
from tests.lab.simulated_seats import SimulatedSeats
from tests.shared_journal import SharedJournal
from tests.stories.fixtures.state_fixture import StateFixture


@dataclass(frozen=True)
class FixtureCopy:
    """A state fixture as its seeder left the journal: its rows, files, services and OpenRig simulation, the fixture rows, agent sessions and lines, put back for every later story that starts from it."""

    journal: SharedJournal
    fixture: StateFixture
    line_keys: frozenset[str]
    main_session_id: str
    session_environments: tuple[tuple[str, str], ...]
    worker_sessions: tuple[tuple[int, str], ...]
    openrig: SimulatedSeats | None
    worker_runner_start: Callable[..., None]

    @staticmethod
    def journal_copy(story, fixture: StateFixture) -> "FixtureCopy":
        return FixtureCopy(
            SharedJournal(story.app), fixture, frozenset(story.line_keys), story.main_session_id,
            tuple(story.session_environments.items()), tuple(story.worker_sessions.items()),
            story.openrig.copied() if story.openrig is not None else None, WorkerRunner.start,
        )

    def restore(self, story) -> StateFixture:
        self.journal.put_back()
        story.openrig = self.openrig.copied() if self.openrig is not None else None
        story.monkeypatch.setattr(WorkerRunner, "start", self.worker_runner_start)
        if story.openrig is not None:
            story.monkeypatch.setattr(story.app.container.get(SeatRuntime), "execute", story.openrig.execute)
        story.team_servers_restarted()
        story.line_keys |= self.line_keys
        environments = dict(self.session_environments)
        story.session_environments = environments
        story.worker_sessions = dict(self.worker_sessions)
        story.replace_main_session(self.main_session_id, story.provider,
                                   environments.get(self.main_session_id, "main"))
        return self.fixture.copied()
