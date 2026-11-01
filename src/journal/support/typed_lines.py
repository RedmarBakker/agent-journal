from journal.support.timeout import Timeout
from journal.support.queued_line import QueuedLine
from journal.support.typed_line import TypedLine
from journal.support.time_source import TimeSource

RECENT_SECONDS = 60.0
JOURNAL_PREFIX = "[journal]"

class TypedLines:
    """The lines for the agents, held until a hook's answer carries them, and the first of them typed into a stopped agent's terminal, waking it so its prompt carries the rest: the typed line is confirmed by the prompt that contains its words, and until then it may have been lost; a woken agent counts as working until it stops again, so no second line is ever typed meanwhile. An environment paused holds every line until it is resumed; one disabled drops every line until it is enabled; clear empties what it holds: what the agent missed, the read at its next start tells it."""

    def __init__(self, time_source: TimeSource) -> None:
        self.time_source = time_source
        self._waiting: list[TypedLine] = []
        self._held: list[QueuedLine] = []
        self._recent: list[TypedLine] = []
        self._disabled_ids: set[int] = set()
        self._paused_ids: set[int] = set()
        self._working_ids: set[int] = set()
        self._refused_stop_ids: set[int] = set()

    def disable(self, environment_id: int) -> None:
        self._disabled_ids.add(environment_id)

    def enable(self, environment_id: int) -> None:
        self._disabled_ids.discard(environment_id)

    def is_disabled(self, environment_id: int) -> bool:
        return environment_id in self._disabled_ids

    def pause(self, environment_id: int) -> None:
        self._paused_ids.add(environment_id)

    def resume(self, environment_id: int) -> None:
        self._paused_ids.discard(environment_id)

    def is_paused(self, environment_id: int) -> bool:
        return environment_id in self._paused_ids

    def work(self, environment_id: int) -> None:
        self._working_ids.add(environment_id)
        self._refused_stop_ids.discard(environment_id)

    def refuse_stop(self, environment_id: int) -> None:
        self._working_ids.add(environment_id)
        self._refused_stop_ids.add(environment_id)

    def is_stop_refused(self, environment_id: int) -> bool:
        return environment_id in self._refused_stop_ids

    def rest(self, environment_id: int) -> None:
        self._working_ids.discard(environment_id)
        self._refused_stop_ids.discard(environment_id)

    def is_working(self, environment_id: int) -> bool:
        return environment_id in self._working_ids

    def pending_lines(self, environment_id: int) -> list[str]:
        return self.matching_lines(lambda h: h.environment_id == environment_id)

    def pending_remarks(self, environment_id: int) -> list[str]:
        return self.matching_lines(lambda h: h.environment_id == environment_id and h.is_remark)

    def pending_instructions(self, environment_id: int) -> list[str]:
        return self.matching_lines(lambda h: h.environment_id == environment_id and not h.is_remark)

    def matching_lines(self, wanted) -> list[str]:
        lines = [h.line.removeprefix(JOURNAL_PREFIX).strip() for h in self._held if wanted(h)]
        self._held = [h for h in self._held if not wanted(h)]
        return lines

    def clear(self, environment_id: int) -> None:
        self._held = [h for h in self._held if h.environment_id != environment_id]

    def discard(self, environment_id: int) -> None:
        self.clear(environment_id)
        self._waiting = [line for line in self._waiting if line.environment_id != environment_id]
        self._recent = [line for line in self._recent if line.environment_id != environment_id]
        self._disabled_ids.discard(environment_id)
        self._paused_ids.discard(environment_id)
        self._working_ids.discard(environment_id)
        self._refused_stop_ids.discard(environment_id)

    def is_waiting(self, environment_id: int) -> bool:
        return any(t.environment_id == environment_id for t in self._waiting)

    def queue(self, line: QueuedLine) -> None:
        if any(h.environment_id == line.environment_id and h.line == line.line for h in self._held):
            return
        self._held.append(line)

    def first_instruction(self, environment_id: int) -> QueuedLine | None:
        first = next((h for h in self._held if h.environment_id == environment_id and not h.is_remark), None)
        if first is not None:
            self._held.remove(first)
        return first

    def typed(self, environment_id: int, line: str) -> None:
        moment = self.time_source.seconds()
        self._waiting.append(TypedLine(environment_id, line, moment))
        self._recent = [t for t in self._recent if not Timeout.seconds(RECENT_SECONDS).started(t.time).is_elapsed(moment)] + [TypedLine(environment_id, line, moment)]

    def contains(self, environment_id: int, prompt: str) -> bool:
        return any(t.matches_prompt(environment_id, prompt) for t in self._recent if not Timeout.seconds(RECENT_SECONDS).started(t.time).is_elapsed(self.time_source.seconds()))

    def confirm(self, environment_id: int, prompt: str) -> bool:
        matches = [t for t in self._waiting if t.matches_prompt(environment_id, prompt)]
        self._waiting = [t for t in self._waiting if t not in matches]
        return bool(matches)

    def waiting_count(self, environment_id: int) -> int:
        return sum(1 for t in self._waiting if t.environment_id == environment_id)

    def overdue(self, environment_id: int, previous: float) -> list[TypedLine]:
        return [t for t in self._waiting if t.environment_id == environment_id and t.time <= previous]

    def retry(self, keystrokes: TypedLine, time: float) -> TypedLine:
        repeat = TypedLine(keystrokes.environment_id, keystrokes.line, time, keystrokes.tries + 1)
        self._waiting[self._waiting.index(keystrokes)] = repeat
        self._recent = [t for t in self._recent if not Timeout.seconds(RECENT_SECONDS).started(t.time).is_elapsed(time)] + [repeat]
        return repeat

    def abandon(self, keystrokes: TypedLine) -> None:
        self._waiting.remove(keystrokes)
