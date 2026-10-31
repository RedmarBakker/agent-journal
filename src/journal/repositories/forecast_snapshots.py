import hashlib
import json

from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.forecast_snapshot import ForecastSnapshot
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource


FORECAST_SCOPE = "delivery_forecast_scope"


class ForecastSnapshots(ScopedRepository[ForecastSnapshot]):
    """The append-only forecast record used for later out-of-sample comparison."""

    model = ForecastSnapshot

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, time_source: TimeSource, links: Links) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.links = links

    def capture(self, scope: Model, source: dict, forecast: dict, actor: Actor) -> dict:
        if forecast["status"] != "forecast" and not self.has_duration_forecast(forecast):
            return forecast
        key = self.key(scope, forecast)
        with self.writing():
            rows = self.matching(snapshot_key=key)
            if rows:
                return {**forecast, "forecast_snapshot_id": rows[0].row_id}
            row = self.save(ForecastSnapshot(snapshot_key=key, input_cut=forecast["input_cut"],
                                             captured_at=self.time_source.seconds(), seed=forecast["seed"],
                                             method_version=forecast["method_version"],
                                             data={"forecast": forecast, "input_snapshot": source}), actor)
            self.links.linked(Ref.build(row), Ref.build(scope), FORECAST_SCOPE, actor)
        return {**forecast, "forecast_snapshot_id": row.row_id}

    def for_scope(self, scope: Model) -> list[ForecastSnapshot]:
        return sorted((self.find(ref.id) for ref in self.links.sources(scope, FORECAST_SCOPE)),
                      key=lambda row: (row.captured_at, row.row_id))

    def save(self, row: ForecastSnapshot, actor: Actor) -> ForecastSnapshot:
        if not row.is_new:
            raise Rejection("forecast snapshots are immutable")
        return super().save(row, actor)

    def delete(self, row: ForecastSnapshot, actor: Actor) -> None:
        raise Rejection("forecast snapshots are immutable")

    @staticmethod
    def key(scope: Model, forecast: dict) -> str:
        duration = forecast.get("duration_ranges") or {}
        value = {"scope": [scope.table(), scope.row_id], "input_cut": forecast["input_cut"],
                 "method_version": forecast["method_version"], "as_of": forecast["as_of"],
                 "duration_input_cut": duration.get("input_cut"),
                 "duration_method_version": duration.get("method_version")}
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def has_duration_forecast(forecast: dict) -> bool:
        return (forecast.get("duration_ranges", {}).get("status") == "forecast"
                and bool(forecast.get("duration_ranges", {}).get("input_cut")))
