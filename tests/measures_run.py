"""A long run, not in the default suite: plays every scenario of last week's history with its known policy at follow rates 0, 0.5, 0.8 and 1.0, prints one row per run, and judges the measures on settling, quiet and score."""

import os
from dataclasses import replace
from pathlib import Path

import pytest

from journal.features.workers.fitness_options import FitnessOptions
from journal.features.workers.support.mode_measures import ModeMeasures
from journal.repositories.setting_rows import SettingRows
from journal.repositories.scope import Scope
from tests.simulation.known_policy import KnownPolicy
from tests.simulation.scenario_run import POLICIES, ScenarioRun
from tests.simulation.scenarios import HISTORY, KNOWN_PAIRS
from tests.simulation.settling import Settling
from tests.simulation_run import fresh
from tests.test_features import MAIN

SEED = int(os.environ.get("SIM_SEED", "1035"))
MINUTES = int(os.environ.get("SIM_MINUTES", "0"))
MODES = tuple(filter(None, os.environ.get("SIM_MODES", "").split(",")))
FOLLOW_RATES = (0.0, 0.5, 0.8, 1.0)


def settled(folder: Path, monkeypatch, scenario, follow_rate: float) -> Settling:
    simulator = fresh(folder, monkeypatch)
    try:
        with simulator.app.container.get(Scope).environment(MAIN):
            played = replace(scenario, minutes=MINUTES or scenario.minutes)
            run = ScenarioRun(simulator, played, SEED, KnownPolicy(POLICIES[played.policy](), follow_rate, SEED))
            trace = run.played()
            specs, warmup = simulator.app.container.get(ModeMeasures).specs(played.mode), simulator.app.container.get(SettingRows).decimal(FitnessOptions.SCORE_WARMUP_MINUTES) * 60
            return Settling(played, tuple(trace), tuple(run.samples), lambda states: ModeMeasures.scored(states, specs, warmup))
    finally:
        simulator.app.runtime().stop()


def test_the_measures_settle_score_by_following_and_stay_quiet_over_last_weeks_history(tmp_path, monkeypatch):
    failing: list[str] = []
    print(f"\n{'scenario':60} {'follow':>6} {'score':>6} {'lines/h':>8} {'measure/h':>9} {'band/h':>6}  failing")
    for scenario in (scenario for scenario in HISTORY if not MODES or scenario.mode in MODES):
        scores = []
        for rate in FOLLOW_RATES:
            run = settled(tmp_path / f"{len(failing)}-{scenario.name}-{rate}".replace(" ", "_"), monkeypatch, scenario, rate)
            scores.append(run.mean_score())
            print(f"{scenario.name:60} {rate:6.1f} {run.mean_score():6.1f} {run.lines_hourly():8.1f} {run.measure_lines_hourly():9.1f} {run.band_changes_hourly():6.1f}  {'; '.join(run.failures())}")
            failing.extend(f"{scenario.name} at {rate}: {failure}" for failure in run.failures())
        if scores != sorted(scores):
            failing.append(f"{scenario.name}: the score does not rise with the follow rate: {[round(score, 1) for score in scores]}")
        if scores[2] < 80:
            failing.append(f"{scenario.name}: a follower at 0.8 scores {scores[2]:.1f}, under 80")
        if scores[0] > 60:
            failing.append(f"{scenario.name}: a policy that ignores the lines scores {scores[0]:.1f}, over 60")
    for good, bad in (pair for pair in KNOWN_PAIRS if not MODES or pair[0].mode in MODES):
        good_score, bad_score = (settled(tmp_path / f"pair-{scenario.name}".replace(" ", "_"), monkeypatch, scenario, 0.8).mean_score() for scenario in (good, bad))
        if good_score <= bad_score:
            failing.append(f"{good.name} scores {good_score:.1f}, not above {bad.name}'s {bad_score:.1f}")
    print("\n".join(["", "failing checks:", *failing]) if failing else "\nevery check holds")
    assert not failing, "\n".join(failing)
