from itertools import product
import math
import random
from statistics import mean, median
from typing import Iterable


class PairedTests:
    @staticmethod
    def mcnemar(a_success: Iterable[bool | None], b_success: Iterable[bool | None]) -> dict[str, object]:
        a_values = tuple(a_success)
        b_values = tuple(b_success)
        if not a_values or len(a_values) != len(b_values):
            raise ValueError("McNemar needs equally sized non-empty paired outcomes")
        pairs = tuple(zip(a_values, b_values))
        if any(value is not None and not isinstance(value, bool) for pair in pairs for value in pair):
            raise ValueError("McNemar outcomes must be booleans or missing")
        missing = sum(a is None or b is None for a, b in pairs)
        observed = tuple((a, b) for a, b in pairs if a is not None and b is not None)
        cells = {
            "a_success_b_success": sum(a and b for a, b in observed),
            "a_success_b_failure": sum(a and not b for a, b in observed),
            "a_failure_b_success": sum(not a and b for a, b in observed),
            "a_failure_b_failure": sum(not a and not b for a, b in observed),
        }
        discordant_improvements = cells["a_failure_b_success"]
        discordant_harms = cells["a_success_b_failure"]
        discordant = discordant_improvements + discordant_harms
        p_value = None if missing else PairedTests._binomial_upper_tail(discordant, discordant_improvements)
        return {
            "method": "exact one-sided McNemar",
            "status": "incomplete" if missing else "no_discordance" if discordant == 0 else "tested",
            "assumption": "under the equal paired marginal null, discordant B improvements are binomial with probability one half",
            "alternative": "B improves success over A",
            "cells": cells,
            "pair_count": len(pairs),
            "observed_pair_count": len(observed),
            "missing_pair_count": missing,
            "discordant_pair_count": discordant,
            "effect_percentage_points": None if missing else 100 * (discordant_improvements - discordant_harms) / len(observed),
            "p_value": p_value,
        }

    @staticmethod
    def continuous(
        differences: Iterable[float | int | None],
        *,
        random_seed: int,
        permutation_draws: int,
        exact_enumeration_cutoff: int,
        bootstrap_draws: int,
        independent_unit: str,
        null_value: float = 0.0,
        alternative: str = "greater",
    ) -> dict[str, object]:
        values = tuple(differences)
        if not values or not independent_unit.strip():
            raise ValueError("a continuous paired test needs independent paired units")
        if any(value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)) for value in values):
            raise ValueError("paired differences must be finite numbers or missing")
        if not math.isfinite(null_value) or alternative not in {"greater", "less", "two-sided"}:
            raise ValueError("the paired test needs a finite null and supported alternative")
        if permutation_draws < 1 or exact_enumeration_cutoff < 1 or bootstrap_draws < 100:
            raise ValueError("paired tests need positive permutation draws and at least one hundred bootstrap draws")
        present = tuple(float(value) for value in values if value is not None)
        missing = len(values) - len(present)
        if missing or len(present) < 2:
            return {
                "method": "paired sign-flip permutation; paired-unit percentile bootstrap",
                "status": "incomplete" if missing else "not_enough_pairs",
                "assumption": "within-pair label exchangeability under the declared sharp null; pairs or declared clusters are independent",
                "independent_unit": independent_unit,
                "alternative": alternative,
                "pair_count": len(values),
                "observed_pair_count": len(present),
                "missing_pair_count": missing,
                "effect_median": None,
                "p_value": None,
                "interval": {"status": "unavailable", "lower": None, "upper": None},
            }
        shifted = tuple(value - null_value for value in present)
        observed_statistic = mean(shifted)
        rng = random.Random(random_seed)
        exact = len(present) <= exact_enumeration_cutoff
        sign_vectors = product((-1.0, 1.0), repeat=len(present)) if exact else (
            tuple(rng.choice((-1.0, 1.0)) for _ in present) for _ in range(permutation_draws)
        )
        draws = 0
        extreme = 0
        for signs in sign_vectors:
            candidate = mean(tuple(value * sign for value, sign in zip(shifted, signs)))
            extreme += PairedTests._is_extreme(candidate, observed_statistic, alternative)
            draws += 1
        p_value = extreme / draws if exact else (extreme + 1) / (draws + 1)
        bootstrap = tuple(
            median(tuple(present[rng.randrange(len(present))] for _ in present))
            for _ in range(bootstrap_draws)
        )
        ordered = sorted(bootstrap)
        lower = ordered[max(0, math.ceil(0.025 * len(ordered)) - 1)]
        upper = ordered[max(0, math.ceil(0.975 * len(ordered)) - 1)]
        degenerate = lower == upper
        return {
            "method": "paired sign-flip permutation; paired-unit percentile bootstrap",
            "status": "tested",
            "assumption": "within-pair label exchangeability under the declared sharp null; pairs or declared clusters are independent",
            "independent_unit": independent_unit,
            "alternative": alternative,
            "tie_handling": "inclusive extreme statistic with 1e-12 absolute and relative tolerance",
            "null_value": null_value,
            "pair_count": len(values),
            "observed_pair_count": len(present),
            "missing_pair_count": 0,
            "effect_median": median(present),
            "test_statistic_mean": observed_statistic,
            "p_value": p_value,
            "permutation": {
                "enumeration": "exact" if exact else "sampled",
                "seed": random_seed,
                "draws": draws,
                "extreme": extreme,
                "p_value_rule": "extreme / draws" if exact else "(extreme + 1) / (draws + 1)",
            },
            "interval": {
                "status": "degenerate" if degenerate else "approximate_95_percentile",
                "lower": lower,
                "upper": upper,
                "draws": bootstrap_draws,
                "seed": random_seed,
            },
        }

    @staticmethod
    def holm(family: Iterable[tuple[str, float | None]], alpha: float) -> dict[str, object]:
        entries = tuple(family)
        names = tuple(name for name, _ in entries)
        if not entries or any(not name.strip() for name in names) or len(set(names)) != len(names):
            raise ValueError("Holm correction needs unique named family members")
        if not math.isfinite(alpha) or alpha <= 0 or alpha >= 1:
            raise ValueError("Holm alpha must be between zero and one")
        for _, value in entries:
            if value is not None and (not math.isfinite(value) or value < 0 or value > 1):
                raise ValueError("Holm p-values must be between zero and one or missing")
        ranked = sorted(enumerate(entries), key=lambda item: (1.0 if item[1][1] is None else item[1][1], item[0]))
        previous = 0.0
        adjusted = {}
        size = len(entries)
        for rank, (_, (name, value)) in enumerate(ranked, start=1):
            raw = 1.0 if value is None else value
            current = min(1.0, (size - rank + 1) * raw)
            previous = max(previous, current)
            adjusted[name] = {
                "p_value": value,
                "adjusted_p_value": None if value is None else previous,
                "passed": value is not None and previous <= alpha,
            }
        return {"method": "Holm step-down familywise correction", "alpha": alpha, "family_size": size, "members": adjusted}

    @staticmethod
    def _is_extreme(candidate: float, observed: float, alternative: str) -> int:
        tolerance = max(1e-12, 1e-12 * abs(observed))
        if alternative == "greater":
            return int(candidate >= observed - tolerance)
        if alternative == "less":
            return int(candidate <= observed + tolerance)
        return int(abs(candidate) >= abs(observed) - tolerance)

    @staticmethod
    def _binomial_upper_tail(total: int, observed: int) -> float:
        if observed == 0:
            return 1.0
        log_half = -total * math.log(2)
        log_probabilities = tuple(
            math.lgamma(total + 1) - math.lgamma(count + 1) - math.lgamma(total - count + 1) + log_half
            for count in range(observed, total + 1)
        )
        largest = max(log_probabilities)
        probability = math.exp(largest) * math.fsum(math.exp(value - largest) for value in log_probabilities)
        return min(1.0, max(float.fromhex("0x0.0000000000001p-1022"), probability))
