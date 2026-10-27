"""Replays the last seven days of the worker queue of this journal's newest worked environment through the band rule, read-only, for candidate margins and least stays, and prints each candidate's band changes an hour and longest stay in each band, with the margins it chooses for each mode: at the shortest stay that keeps to one change an hour, the margin with the fewest changes, no wider than half the way between the high and the low levels; run it as PYTHONPATH=src python3 scripts/band_replay.py."""

import shutil
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from journal.app import App
from journal.config import Config
from journal.features.workers.support.band_rule import BandRule
from journal.features.workers.support.load_items import LoadItems
from journal.features.workers.support.load_meter import WORKER_REF
from journal.features.workers.support.load_series import LoadSeries
from journal.features.workers.workers_options import WorkersOptions
from journal.models.support.pressure_band import PressureBand
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows

ROOT = Path(__file__).resolve().parents[1]
DAYS = 7
EMPTY_QUEUE_SECONDS = 300.0
MODE_ENTRIES = {"orchestrator": (0.8, 0.5), "builder": (0.5, 0.3)}
MARGINS = (0.0, 0.05, 0.1, 0.15, 0.2)
STAY_MINUTES = (0, 2, 5, 10, 15, 20, 30)
LEAST_CHANGES_HOURLY = 1.0


def copied_journal() -> Path:
    root = Path(tempfile.mkdtemp(prefix="band-replay-"))
    (root / ".journal").mkdir()
    with sqlite3.connect(f"file:{ROOT / '.journal' / 'journal.db'}?mode=ro", uri=True) as live, sqlite3.connect(root / ".journal" / "journal.db") as copy:
        live.backup(copy)
    return root


def kept_days(database: Path) -> list[str]:
    with sqlite3.connect(database) as connection:
        return [row[0] for row in connection.execute("SELECT DISTINCT substr(created_at, 1, 10) FROM entries WHERE entry_type = 'load_inputs' ORDER BY 1")]


def newest_environment(database: Path) -> int:
    with sqlite3.connect(database) as connection:
        return connection.execute("SELECT environment_id FROM agents WHERE role = 'main' ORDER BY updated_at DESC LIMIT 1").fetchone()[0]


def replayed(points: tuple[tuple[float, float, float], ...], rule: BandRule) -> tuple[float, dict[PressureBand, float]]:
    band, changed_at, empty_since, changes = PressureBand.NORMAL, points[0][0], points[0][0], 0
    longest = {PressureBand.LOW: 0.0, PressureBand.NORMAL: 0.0, PressureBand.HIGH: 0.0}
    for moment, rho, waiting in points:
        empty_since = empty_since if waiting == 0 else moment
        moved = rule.moved(band, rho, moment - changed_at, moment - empty_since)
        if moved != band:
            longest[band] = max(longest[band], moment - changed_at)
            band, changed_at, changes = moved, moment, changes + 1
    longest[band] = max(longest[band], points[-1][0] - changed_at)
    hours = (points[-1][0] - points[0][0]) / 3600
    return changes / hours, {key: value / 60 for key, value in longest.items()}


def main() -> int:
    began = time.monotonic()
    root = copied_journal()
    try:
        app = App(Config(root, port=0))
        now, start = time.time(), time.time() - DAYS * 86400
        with app.container.get(Scope).environment(newest_environment(root / ".journal" / "journal.db")):
            items, _ = app.container.get(LoadItems).read(start)
            settings = app.container.get(SettingRows)
            series = LoadSeries(settings.decimal(WorkersOptions.WORKLOAD_WINDOW_MINUTES), settings.decimal(WorkersOptions.WORKLOAD_SMOOTHING_MINUTES), 1.0, 0.0)
        work_items = [item for item in items if item.ref.startswith(WORKER_REF)]
        kept = kept_days(root / ".journal" / "journal.db")
        print(f"days kept as load inputs: {', '.join(kept) or 'none'}; every day of the {DAYS} rebuilt from the workers' rows, with today's clearings (a send-back ends an item, it does not clear it)")
        print(f"worker items: {len(work_items)}, from {datetime.fromtimestamp(start, timezone.utc):%Y-%m-%d} to {datetime.fromtimestamp(now, timezone.utc):%Y-%m-%d}")
        points = series.walk(work_items, now, now - start).points
        for mode, (high_entry, low_entry) in MODE_ENTRIES.items():
            print(f"\n{mode}: high at {high_entry}, low under {low_entry}")
            print(f"{'margin':>6} {'stay':>5} {'changes/h':>9} {'longest low':>11} {'longest normal':>14} {'longest high':>12}")
            results = []
            for stay in STAY_MINUTES:
                for margin in (margin for margin in MARGINS if margin <= (high_entry - low_entry) / 2 + 1e-9):
                    rule = BandRule(high_entry, high_entry - margin, low_entry, low_entry + margin, stay * 60.0, EMPTY_QUEUE_SECONDS)
                    hourly, longest = replayed(points, rule)
                    results.append((stay, margin, hourly))
                    print(f"{margin:>6.2f} {stay:>5} {hourly:>9.2f} {longest[PressureBand.LOW]:>11.0f} {longest[PressureBand.NORMAL]:>14.0f} {longest[PressureBand.HIGH]:>12.0f}")
            passing = [result for result in results if result[2] <= LEAST_CHANGES_HOURLY]
            shortest = min((result[0] for result in passing), default=None)
            chosen = min((result for result in passing if result[0] == shortest), key=lambda result: (result[2], -result[1]), default=None)
            print(f"chosen for {mode}: margin {chosen[1]:.2f}, least stay {chosen[0]} minutes, {chosen[2]:.2f} changes an hour" if chosen else f"no candidate keeps {mode} to one change an hour")
        print(f"\nreplayed in {time.monotonic() - began:.1f} seconds")
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
