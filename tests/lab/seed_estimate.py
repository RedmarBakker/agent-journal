from dataclasses import asdict, dataclass
import math
import random
import re
from statistics import NormalDist, stdev
from typing import Literal

from tests.lab.guard_pilot import GuardPilot
from tests.lab.simulation_caps import SimulationCaps


PilotUnit = float | tuple[bool, bool]


@dataclass(frozen=True)
class SeedEstimate:
    status: Literal["estimated", "cap_insufficient", "not_enough_history", "unattainable_minimum"]
    metric: str
    method: str
    pilot_manifest_digest: str | None
    confirmatory_manifest_digest: str
    pilot_unit_counts: tuple[tuple[str, int], ...]
    guard_margins: tuple[tuple[str, float], ...]
    cap_limits: tuple[tuple[str, int | float], ...]
    analysis_parameters: tuple[tuple[str, object], ...]
    required_seed_count: int | None
    cap_fitted_seed_count: int
    primary_power: float | None
    whole_keep_rule_probability: float | None
    precision_half_width: float | None
    seed_count_uncertainty: tuple[int, int] | None
    seeds_by_scenario: tuple[tuple[str, tuple[int, ...]], ...]
    reason: str

    @classmethod
    def from_pilot(
        cls,
        *,
        pilot_manifest_digest: str | None,
        confirmatory_manifest_digest: str,
        pilot_kind: str,
        metric: str,
        expected_metric: str,
        primary_kind: Literal["binary", "continuous"],
        pilot_units_by_scenario: tuple[tuple[str, tuple[PilotUnit, ...]], ...] | None,
        pilot_missing_units_by_scenario: tuple[tuple[str, int], ...],
        scenario_names: tuple[str, ...],
        models: tuple[str, ...],
        pilot_seeds: tuple[int, ...],
        caps: SimulationCaps,
        estimated_storage_bytes_per_run: int,
        estimated_run_seconds: float,
        simulated_minutes_by_scenario: tuple[tuple[str, int], ...],
        assumed_effect: float,
        practical_minimum: float,
        precision_target: float,
        required_power: float,
        alpha: float,
        confirmatory_family_size: int,
        guard_pilots: tuple[GuardPilot, ...] = (),
        guard_count: int = 0,
        bootstrap_draws: int = 500,
        random_seed: int = 0,
    ) -> "SeedEstimate":
        cls._validate_request(
            metric, expected_metric, confirmatory_manifest_digest, primary_kind, scenario_names, models,
            pilot_seeds, pilot_missing_units_by_scenario, caps, estimated_storage_bytes_per_run, estimated_run_seconds,
            simulated_minutes_by_scenario, assumed_effect, practical_minimum, precision_target,
            required_power, alpha, confirmatory_family_size, guard_count, bootstrap_draws, random_seed,
        )
        cap_limits = cls._cap_limits(
            caps, scenario_names, models, estimated_storage_bytes_per_run,
            estimated_run_seconds, simulated_minutes_by_scenario,
        )
        if len(models) != 1:
            return cls._unready(
                metric, confirmatory_manifest_digest,
                "not enough history: estimate one calibrated model stratum at a time", pilot_manifest_digest, cap_limits,
            )
        if pilot_units_by_scenario is None:
            return cls._unready(
                metric, confirmatory_manifest_digest, "not enough history: run a separately budgeted exploratory pilot", pilot_manifest_digest, cap_limits,
            )
        cls._validate_pilot_pin(pilot_manifest_digest, confirmatory_manifest_digest, pilot_kind)
        if guard_count > len(guard_pilots):
            return cls._unready(
                metric, confirmatory_manifest_digest,
                "not enough history: joint pilot evidence for every confirmatory guard is required", pilot_manifest_digest, cap_limits,
            )
        if guard_count != len(guard_pilots):
            raise ValueError("guard pilot evidence must match the frozen confirmatory family")
        pilot_map = cls._pilot_map(pilot_units_by_scenario, scenario_names)
        missing = dict(pilot_missing_units_by_scenario)
        if len(missing) != len(pilot_missing_units_by_scenario) or set(missing) != set(scenario_names):
            raise ValueError("pilot missing-unit accounting must include every scenario exactly once")
        counts = tuple((scenario, len(pilot_map[scenario])) for scenario in scenario_names)
        if any(value != 0 for value in missing.values()):
            return cls._unready(
                metric, confirmatory_manifest_digest,
                "not enough history: pilot has missing or censored pairs that cannot be dropped", pilot_manifest_digest, cap_limits, counts,
            )
        if len(pilot_seeds) < 8 or any(count != len(pilot_seeds) or count < 8 for _, count in counts):
            return cls._unready(
                metric, confirmatory_manifest_digest,
                "not enough history: each scenario needs at least eight complete pinned pilot seeds", pilot_manifest_digest, cap_limits, counts,
            )
        cls._validate_units(pilot_map, scenario_names, primary_kind)
        cls._validate_guards(guard_pilots, scenario_names, pilot_seeds)
        guard_margins = tuple((guard.metric, guard.tolerated_harm) for guard in guard_pilots)
        analysis_parameters = (
            ("primary_kind", primary_kind),
            ("assumed_effect", assumed_effect),
            ("practical_minimum", practical_minimum),
            ("precision_target", precision_target),
            ("required_power", required_power),
            ("alpha", alpha),
            ("confirmatory_family_size", confirmatory_family_size),
            ("guard_assumed_benefits", tuple((guard.metric, guard.assumed_benefit) for guard in guard_pilots)),
            ("bootstrap_draws", bootstrap_draws),
            ("random_seed", random_seed),
            ("models", models),
            ("pilot_seeds", pilot_seeds),
            ("simulated_minutes_by_scenario", simulated_minutes_by_scenario),
        )
        effect, minimum, precision = cls._effect_units(primary_kind, assumed_effect, practical_minimum, precision_target)
        if effect <= minimum:
            return cls(
                status="unattainable_minimum", metric=metric, method="paired pilot normal approximation",
                pilot_manifest_digest=pilot_manifest_digest, confirmatory_manifest_digest=confirmatory_manifest_digest,
                pilot_unit_counts=counts, guard_margins=guard_margins, cap_limits=cap_limits,
                analysis_parameters=analysis_parameters, required_seed_count=None, cap_fitted_seed_count=0,
                primary_power=None, whole_keep_rule_probability=0.0, precision_half_width=None,
                seed_count_uncertainty=None, seeds_by_scenario=tuple((name, ()) for name in scenario_names),
                reason="the assumed improvement does not exceed the preregistered practical minimum",
            )
        if any(cls._degenerate(tuple(pilot_map[name]), primary_kind, effect) for name in scenario_names):
            return cls._unready(
                metric, confirmatory_manifest_digest,
                "not enough history: pilot paired effect spread or discordance is degenerate", pilot_manifest_digest, cap_limits, counts,
            )
        if any(stdev(differences) == 0 for guard in guard_pilots for _, differences in guard.beneficial_differences_by_scenario):
            return cls._unready(
                metric, confirmatory_manifest_digest,
                "not enough history: a guard pilot has degenerate paired spread", pilot_manifest_digest, cap_limits, counts,
            )
        if any(guard.assumed_benefit + guard.tolerated_harm <= 0 for guard in guard_pilots):
            return cls(
                status="unattainable_minimum", metric=metric, method="paired pilot normal approximation",
                pilot_manifest_digest=pilot_manifest_digest, confirmatory_manifest_digest=confirmatory_manifest_digest,
                pilot_unit_counts=counts, guard_margins=guard_margins, cap_limits=cap_limits,
                analysis_parameters=analysis_parameters, required_seed_count=None,
                cap_fitted_seed_count=0, primary_power=None, whole_keep_rule_probability=0.0,
                precision_half_width=None, seed_count_uncertainty=None,
                seeds_by_scenario=tuple((name, ()) for name in scenario_names),
                reason="a guard's assumed effect does not exceed its tolerated-harm boundary",
            )
        z_critical = NormalDist().inv_cdf(1 - alpha / confirmatory_family_size)
        z_power = NormalDist().inv_cdf(required_power)
        z_precision = NormalDist().inv_cdf(0.975)
        primary_count = max(
            cls._required_count(tuple(pilot_map[name]), primary_kind, effect, minimum, precision, z_critical, z_power, z_precision)
            for name in scenario_names
        )
        guard_counts = tuple(cls._guard_required_count(guard, z_critical, z_power) for guard in guard_pilots)
        required_count = max((primary_count, *guard_counts))
        seed_capacity = min(limit for name, limit in cap_limits if name.endswith("_seed_capacity"))
        fitted_count = min(required_count, seed_capacity)
        first_seed = max(pilot_seeds) + 1
        seed_lists = tuple((name, tuple(range(first_seed, first_seed + fitted_count))) for name in scenario_names)
        primary_power, keep_probability, half_width = cls._probabilities(
            tuple(pilot_map[name] for name in scenario_names), primary_kind, effect,
            minimum, fitted_count, z_critical, guard_pilots, scenario_names,
        )
        if primary_kind == "binary":
            half_width *= 100
        uncertainty = cls._bootstrap_uncertainty(
            pilot_map, scenario_names, primary_kind, effect, minimum, precision,
            z_critical, z_power, z_precision, guard_pilots, bootstrap_draws, random_seed,
        )
        limited = fitted_count < required_count
        limiting_caps = tuple(name for name, limit in cap_limits if name.endswith("_seed_capacity") and limit == seed_capacity)
        reason = (
            f"approved caps ({', '.join(limiting_caps)}) fit fewer paired seeds than estimated"
            if limited else "estimated count meets declared power and precision targets under the pilot spread assumption"
        )
        return cls(
            status="cap_insufficient" if limited else "estimated", metric=metric,
            method="normal approximation for paired tests and the median effect; bootstrap pilot-spread sensitivity; whole-rule probability is a Bonferroni lower bound",
            pilot_manifest_digest=pilot_manifest_digest, confirmatory_manifest_digest=confirmatory_manifest_digest,
            pilot_unit_counts=counts, guard_margins=guard_margins, cap_limits=cap_limits,
            analysis_parameters=analysis_parameters, required_seed_count=required_count,
            cap_fitted_seed_count=fitted_count, primary_power=primary_power,
            whole_keep_rule_probability=keep_probability, precision_half_width=half_width,
            seed_count_uncertainty=uncertainty, seeds_by_scenario=seed_lists, reason=reason,
        )

    def manifest(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def _validate_request(
        cls, metric: str, expected_metric: str, confirmatory_digest: str, primary_kind: str,
        scenarios: tuple[str, ...], models: tuple[str, ...], pilot_seeds: tuple[int, ...],
        missing_units: tuple[tuple[str, int], ...],
        caps: SimulationCaps, storage_per_run: int, run_seconds: float, scenario_minutes: tuple[tuple[str, int], ...],
        effect: float, minimum: float, precision: float, power: float, alpha: float, family_size: int,
        guard_count: int, bootstrap_draws: int, random_seed: int,
    ) -> None:
        if not metric.strip() or metric != expected_metric:
            raise ValueError("pilot evidence must be pinned to the selected primary metric")
        if not cls._valid_digest(confirmatory_digest):
            raise ValueError("seed estimates need a pinned confirmatory manifest digest")
        if primary_kind not in {"binary", "continuous"}:
            raise ValueError("seed estimates support binary or continuous paired primaries")
        if not math.isfinite(effect) or not math.isfinite(minimum) or minimum < 0:
            raise ValueError("seed estimates need finite assumed and practical effects")
        if not math.isfinite(precision) or precision <= 0:
            raise ValueError("the precision target must be finite and positive")
        if not math.isfinite(power) or power <= 0 or power >= 1:
            raise ValueError("the power target must be between zero and one")
        if not math.isfinite(alpha) or alpha <= 0 or alpha >= 1 or not isinstance(family_size, int) or isinstance(family_size, bool) or family_size < 1:
            raise ValueError("seed estimates need alpha and a frozen confirmatory family size")
        if not scenarios or not models or len(set(scenarios)) != len(scenarios) or len(set(models)) != len(models):
            raise ValueError("seed estimates need unique scenario and model strata")
        if any(not name.strip() for name in (*scenarios, *models)):
            raise ValueError("seed estimate scenario and model names cannot be empty")
        if len(set(pilot_seeds)) != len(pilot_seeds) or any(not isinstance(seed, int) or isinstance(seed, bool) for seed in pilot_seeds):
            raise ValueError("pilot seeds must be unique integers")
        if not isinstance(caps, SimulationCaps):
            raise ValueError("seed estimates must use the frozen simulation caps")
        if not isinstance(storage_per_run, int) or isinstance(storage_per_run, bool) or storage_per_run <= 0:
            raise ValueError("pilot storage per run must be a positive integer")
        if not math.isfinite(run_seconds) or run_seconds <= 0:
            raise ValueError("the pilot run duration must be finite and positive")
        if len(dict(scenario_minutes)) != len(scenario_minutes) or set(dict(scenario_minutes)) != set(scenarios):
            raise ValueError("simulated-minute estimates must include every scenario exactly once")
        if len(dict(missing_units)) != len(missing_units) or set(dict(missing_units)) != set(scenarios):
            raise ValueError("pilot missing-unit counts must include every scenario exactly once")
        if any(not isinstance(count, int) or isinstance(count, bool) or count < 0 for _, count in missing_units):
            raise ValueError("pilot missing-unit counts must be non-negative integers")
        if any(not isinstance(minutes, int) or isinstance(minutes, bool) or minutes <= 0 for _, minutes in scenario_minutes):
            raise ValueError("scenario simulated-minute estimates must be positive integers")
        if not isinstance(guard_count, int) or isinstance(guard_count, bool) or guard_count < 0:
            raise ValueError("guard count must be a non-negative integer")
        if bootstrap_draws < 100 or not isinstance(random_seed, int) or isinstance(random_seed, bool):
            raise ValueError("seed uncertainty needs at least one hundred draws and a declared integer seed")

    @staticmethod
    def _cap_limits(
        caps: SimulationCaps,
        scenarios: tuple[str, ...],
        models: tuple[str, ...],
        storage_per_run: int,
        run_seconds: float,
        scenario_minutes: tuple[tuple[str, int], ...],
    ) -> tuple[tuple[str, int | float], ...]:
        runs_per_seed = 2 * len(scenarios) * len(models)
        scenario_minutes_max = max(minutes for _, minutes in scenario_minutes)
        run_seed_capacity = caps.max_runs // runs_per_seed
        storage_seed_capacity = caps.max_storage_bytes // (storage_per_run * runs_per_seed)
        deadline_run_capacity = caps.max_processes * math.floor(caps.batch_deadline_seconds / run_seconds)
        deadline_seed_capacity = deadline_run_capacity // runs_per_seed
        run_timeout_capacity = caps.max_runs // runs_per_seed if run_seconds <= caps.run_deadline_seconds else 0
        simulation_capacity = caps.max_runs // runs_per_seed if scenario_minutes_max <= caps.max_simulated_minutes else 0
        return (
            ("max_runs_seed_capacity", run_seed_capacity),
            ("max_storage_seed_capacity", storage_seed_capacity),
            ("batch_deadline_seed_capacity", deadline_seed_capacity),
            ("run_deadline_seed_capacity", run_timeout_capacity),
            ("simulated_minute_seed_capacity", simulation_capacity),
            ("max_processes", caps.max_processes),
            ("max_runs", caps.max_runs),
            ("max_storage_bytes", caps.max_storage_bytes),
            ("batch_deadline_seconds", caps.batch_deadline_seconds),
            ("run_deadline_seconds", caps.run_deadline_seconds),
            ("estimated_storage_bytes_per_run", storage_per_run),
            ("estimated_run_seconds", run_seconds),
            ("max_simulated_minutes", caps.max_simulated_minutes),
            ("largest_scenario_simulated_minutes", scenario_minutes_max),
        )

    @staticmethod
    def _validate_pilot_pin(pilot_digest: str | None, confirmatory_digest: str, pilot_kind: str) -> None:
        if pilot_kind != "exploratory":
            raise ValueError("confirmatory outcomes cannot estimate a later confirmatory sample")
        if not SeedEstimate._valid_digest(pilot_digest):
            raise ValueError("pilot evidence needs a pinned exploratory manifest digest")
        if pilot_digest == confirmatory_digest:
            raise ValueError("a pilot and its confirmatory batch need different manifest digests")

    @staticmethod
    def _pilot_map(
        pilot_units: tuple[tuple[str, tuple[PilotUnit, ...]], ...], scenarios: tuple[str, ...]
    ) -> dict[str, tuple[PilotUnit, ...]]:
        result = dict(pilot_units)
        if len(result) != len(pilot_units) or set(result) != set(scenarios):
            raise ValueError("pilot evidence must include each confirmatory scenario exactly once")
        return result

    @staticmethod
    def _validate_units(pilot_map: dict[str, tuple[PilotUnit, ...]], scenarios: tuple[str, ...], primary_kind: str) -> None:
        if primary_kind == "binary" and any(
            any(not isinstance(unit, tuple) or len(unit) != 2 or any(not isinstance(value, bool) for value in unit) for unit in pilot_map[name])
            for name in scenarios
        ):
            raise ValueError("binary pilot units must be paired success outcomes")
        if primary_kind == "continuous" and any(
            any(isinstance(unit, bool) or not isinstance(unit, (int, float)) or not math.isfinite(unit) for unit in pilot_map[name])
            for name in scenarios
        ):
            raise ValueError("continuous pilot units must be finite paired beneficial differences")

    @staticmethod
    def _validate_guards(guards: tuple[GuardPilot, ...], scenarios: tuple[str, ...], pilot_seeds: tuple[int, ...]) -> None:
        if len({guard.metric for guard in guards}) != len(guards):
            raise ValueError("guard pilot metric names must be unique")
        for guard in guards:
            values = dict(guard.beneficial_differences_by_scenario)
            seed_ids = dict(guard.seed_ids_by_scenario)
            if len(values) != len(guard.beneficial_differences_by_scenario) or set(values) != set(scenarios):
                raise ValueError("each guard pilot must include every confirmatory scenario exactly once")
            if any(len(values[name]) != len(pilot_seeds) or seed_ids[name] != pilot_seeds for name in scenarios):
                raise ValueError("guard pilot pairs must use the same pinned seeds as the primary")

    @staticmethod
    def _effect_units(kind: str, effect: float, minimum: float, precision: float) -> tuple[float, float, float]:
        if kind == "continuous":
            return effect, minimum, precision
        if effect < 0 or effect > 100 or minimum > 100 or precision > 100:
            raise ValueError("binary effect and precision values are percentage points between zero and one hundred")
        return effect / 100, minimum / 100, precision / 100

    @staticmethod
    def _required_count(
        units: tuple[PilotUnit, ...], kind: str, effect: float, minimum: float,
        precision: float, z_critical: float, z_power: float, z_precision: float,
    ) -> int:
        if kind == "continuous":
            spread = stdev(tuple(float(value) for value in units))
            if spread == 0:
                return 2**31
            median_factor = 1.253
            primary_n = ((z_critical + z_power) * spread / effect) ** 2
            keep_n = ((z_critical + z_power) * median_factor * spread / (effect - minimum)) ** 2
            precision_n = (z_precision * median_factor * spread / precision) ** 2
        else:
            differences = tuple(int(b) - int(a) for a, b in units)
            discordance = sum(value != 0 for value in differences) / len(differences)
            variance = max(0.0, discordance - effect * effect)
            if discordance == 0 or variance == 0:
                return 2**31
            primary_n = ((z_critical + z_power) * math.sqrt(discordance) / effect) ** 2
            keep_n = ((z_critical + z_power) * math.sqrt(variance) / (effect - minimum)) ** 2
            precision_n = (z_precision * math.sqrt(variance) / precision) ** 2
        return max(2, math.ceil(primary_n), math.ceil(keep_n), math.ceil(precision_n))

    @staticmethod
    def _guard_required_count(guard: GuardPilot, z_critical: float, z_power: float) -> int:
        boundary_effect = guard.assumed_benefit + guard.tolerated_harm
        if boundary_effect <= 0:
            return 2**31
        required = []
        for _, differences in guard.beneficial_differences_by_scenario:
            spread = stdev(differences)
            if spread == 0:
                return 2**31
            required.append(math.ceil(((z_critical + z_power) * spread / boundary_effect) ** 2))
        return max(2, *required)

    @staticmethod
    def _probabilities(
        units_by_scenario: tuple[tuple[PilotUnit, ...], ...], kind: str, effect: float,
        minimum: float, count: int, z_critical: float, guards: tuple[GuardPilot, ...],
        scenarios: tuple[str, ...],
    ) -> tuple[float, float, float]:
        if count < 1:
            return 0.0, 0.0, 0.0
        normal = NormalDist()
        primary_powers = []
        keep_lower_bounds = []
        half_widths = []
        for units in units_by_scenario:
            if kind == "continuous":
                spread = stdev(tuple(float(value) for value in units))
                test_error = spread / math.sqrt(count)
                estimate_error = 1.253 * test_error
            else:
                differences = tuple(int(b) - int(a) for a, b in units)
                discordance = sum(value != 0 for value in differences) / len(differences)
                test_error = math.sqrt(discordance / count)
                estimate_error = math.sqrt(max(0.0, discordance - effect * effect) / count)
            test_power = 1 - normal.cdf((z_critical * test_error - effect) / test_error)
            minimum_power = 1 - normal.cdf((minimum - effect) / estimate_error) if estimate_error else float(effect >= minimum)
            primary_powers.append(test_power)
            keep_lower_bounds.append(max(0.0, test_power + minimum_power - 1))
            half_widths.append(normal.inv_cdf(0.975) * estimate_error)
        for guard in guards:
            differences = dict(guard.beneficial_differences_by_scenario)
            for scenario in scenarios:
                test_error = stdev(differences[scenario]) / math.sqrt(count)
                boundary_effect = guard.assumed_benefit + guard.tolerated_harm
                keep_lower_bounds.append(1 - normal.cdf((z_critical * test_error - boundary_effect) / test_error))
        whole_rule_lower_bound = max(0.0, 1 - sum(1 - value for value in keep_lower_bounds))
        return min(primary_powers), whole_rule_lower_bound, max(half_widths)

    @classmethod
    def _bootstrap_uncertainty(
        cls, pilot_map: dict[str, tuple[PilotUnit, ...]], scenarios: tuple[str, ...], kind: str,
        effect: float, minimum: float, precision: float, z_critical: float, z_power: float,
        z_precision: float, guards: tuple[GuardPilot, ...], draws: int, seed: int,
    ) -> tuple[int, int]:
        rng = random.Random(seed)
        counts = []
        for _ in range(draws):
            sampled = tuple(
                tuple(units[rng.randrange(len(units))] for _ in units)
                for units in (pilot_map[name] for name in scenarios)
            )
            primary_count = max(
                cls._required_count(units, kind, effect, minimum, precision, z_critical, z_power, z_precision)
                for units in sampled
            )
            guard_counts = tuple(
                cls._guard_required_count(
                    GuardPilot(
                        guard.metric, guard.tolerated_harm, guard.assumed_benefit,
                        tuple((name, tuple(range(len(values)))) for name, values in guard.beneficial_differences_by_scenario),
                        tuple(
                            (name, tuple(values[rng.randrange(len(values))] for _ in values))
                            for name, values in guard.beneficial_differences_by_scenario
                        ),
                    ),
                    z_critical, z_power,
                )
                for guard in guards
            )
            counts.append(max((primary_count, *guard_counts)))
        counts.sort()
        return (
            counts[max(0, math.ceil(0.025 * len(counts)) - 1)],
            counts[max(0, math.ceil(0.975 * len(counts)) - 1)],
        )

    @classmethod
    def _unready(
        cls,
        metric: str,
        confirmatory_digest: str,
        reason: str,
        pilot_digest: str | None,
        cap_limits: tuple[tuple[str, int | float], ...],
        counts: tuple[tuple[str, int], ...] = (),
    ) -> "SeedEstimate":
        return cls(
            status="not_enough_history", metric=metric, method="unavailable",
            pilot_manifest_digest=pilot_digest, confirmatory_manifest_digest=confirmatory_digest,
            pilot_unit_counts=counts, guard_margins=(), cap_limits=cap_limits, analysis_parameters=(), required_seed_count=None,
            cap_fitted_seed_count=0, primary_power=None, whole_keep_rule_probability=None,
            precision_half_width=None, seed_count_uncertainty=None, seeds_by_scenario=(), reason=reason,
        )

    @staticmethod
    def _valid_digest(value: str | None) -> bool:
        return value is not None and re.fullmatch(r"[0-9a-f]{64}", value) is not None

    @staticmethod
    def _degenerate(units: tuple[PilotUnit, ...], kind: str, effect: float) -> bool:
        if kind == "continuous":
            return stdev(tuple(float(value) for value in units)) == 0
        differences = tuple(int(b) - int(a) for a, b in units)
        discordance = sum(value != 0 for value in differences) / len(differences)
        return discordance == 0 or discordance <= effect * effect
