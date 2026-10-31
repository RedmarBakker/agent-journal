from datetime import datetime
import math
from statistics import median

from journal.features.estimates.support.learned_duration_ranges import (
    MINIMUM_REFERENCE_OUTCOMES,
    RECENCY_HALF_LIFE_DAYS,
    LearnedDurationRanges,
)


class DurationRangeCalibration:
    """Replays saved duration forecasts against later immutable outcome facts."""

    def __init__(self, minimum_calibration_samples: int = 5, minimum_drift_samples: int = 5) -> None:
        self.minimum_calibration_samples = minimum_calibration_samples
        self.minimum_drift_samples = minimum_drift_samples

    def replay(self, forecasts: list[dict], outcomes: list[dict], as_of: float) -> dict:
        eligible = [row for row in self.predictions(forecasts) if self.valid_forecast(row, as_of)]
        scored = [self.score(row, outcomes, as_of) for row in eligible]
        predictions = [self.calibrate(row, scored, outcomes) for row in scored]
        observed = [row for row in predictions if row.get("actual_seconds") is not None and not row["censored"]]
        censored = sum(row.get("censored") is True for row in scored)
        empirical = [row for row in observed if row.get("empirical_p50_seconds") is not None]
        coverage = {name: self.coverage(observed, name) for name in ("p50_seconds", "p85_seconds", "calibrated_p85_seconds")}
        coverage.update({name: self.coverage(empirical, name) for name in ("empirical_p50_seconds", "empirical_p85_seconds")})
        coverage = {self.coverage_name(name): value for name, value in coverage.items()}
        drift = self.drift(observed)
        return {"status": "measured" if observed else "not_enough_history", "method_version": "rolling-duration-calibration-v1",
                "label": "How often past tasks finished inside their range; 85% is the aim, not a promise.",
                "prediction_count": len(eligible), "observed_count": len(observed), "censored_predictions": censored,
                "minimum_calibration_samples": self.minimum_calibration_samples, "coverage": coverage,
                "sizing_bias": {stage: self.sizing_bias(observed, stage)
                                for stage in ("execution_cycle", "delivery_delay")},
                "drift": drift, "predictions": predictions}

    def sizing_bias(self, rows: list[dict], stage: str) -> dict:
        ratios = [math.log(row["actual_seconds"] / row["p50_seconds"]) for row in rows
                  if row.get("stage") == stage and self.positive(row.get("actual_seconds"))
                  and self.positive(row.get("p50_seconds"))]
        enough = len(ratios) >= self.minimum_calibration_samples
        ratio = math.exp(median(ratios)) if enough else None
        return {"status": "measured" if enough else "not_enough_history", "observed": len(ratios),
                "actual_to_predicted_p50_ratio": ratio}

    @classmethod
    def predictions(cls, forecasts: list[dict]) -> list[dict]:
        rows = []
        for forecast in forecasts:
            if isinstance(forecast, dict) and "task_id" in forecast:
                rows.append(forecast)
                continue
            rows.extend(cls.snapshot_predictions(forecast))
        unique = {}
        for row in rows:
            key = (row.get("task_id"), row.get("stage"), row.get("captured_at"), row.get("input_cut"))
            unique[key] = row
        return list(unique.values())

    @classmethod
    def snapshot_predictions(cls, snapshot) -> list[dict]:
        if isinstance(snapshot, dict):
            data = snapshot.get("data", {})
            captured_at = cls.moment(snapshot.get("captured_at"))
            snapshot_id = snapshot.get("id", 0)
        else:
            data = getattr(snapshot, "data", {})
            captured_at = getattr(snapshot, "captured_at", 0.0)
            snapshot_id = getattr(snapshot, "id", 0)
        ranges = (data.get("forecast", {}).get("duration_ranges") or {}) if isinstance(data, dict) else {}
        if ranges.get("status") != "forecast":
            return []
        return [{"task_id": task.get("task_id"), "stage": stage, "cohort": task.get("cohort", {}),
                 "size_points": task.get("size_points"), "captured_at": captured_at,
                 "input_cut": ranges.get("input_cut"), "method_version": ranges.get("method_version"),
                 "snapshot_id": snapshot_id, "p50_seconds": result.get("p50_seconds"),
                 "p85_seconds": result.get("p85_seconds")}
                for task in ranges.get("tasks", ()) for stage, result in task.get("stages", {}).items()
                if result.get("status") == "forecast"]

    def score(self, forecast: dict, outcomes: list[dict], as_of: float) -> dict:
        actual = self.actual(forecast, outcomes, as_of)
        return {**forecast, "actual_seconds": actual.get("duration_seconds") if actual else None,
                "actual_at": actual.get("observed_at") if actual else None,
                "censored": bool(actual and actual.get("right_censored"))}

    def calibrate(self, forecast: dict, scored: list[dict], outcomes: list[dict]) -> dict:
        prior = [row for row in scored if row["task_id"] != forecast["task_id"]
                 and row["stage"] == forecast["stage"]
                 and self.same_cohort(row["cohort"], forecast["cohort"])
                 and row["captured_at"] < forecast["captured_at"]
                 and row.get("actual_at") is not None
                 and row["actual_at"] <= forecast["captured_at"]
                 and row.get("actual_seconds") is not None and not row["censored"]]
        residuals = [math.log(row["actual_seconds"] / row["p50_seconds"]) for row in prior]
        enough = len(residuals) >= self.minimum_calibration_samples
        if enough:
            residual = self.quantile(residuals, 0.85)
            p85 = max(forecast["p85_seconds"], forecast["p50_seconds"] * math.exp(residual))
        else:
            p85 = forecast["p85_seconds"]
        empirical = self.empirical_reference(forecast, outcomes)
        return {"task_id": forecast["task_id"], "stage": forecast["stage"], "input_cut": forecast["input_cut"],
                "captured_at": forecast["captured_at"], "calibration_status": "measured" if enough else "not_enough_history",
                "calibration_samples": len(residuals), "p50_seconds": forecast["p50_seconds"],
                "p85_seconds": forecast["p85_seconds"], "calibrated_p85_seconds": p85,
                "empirical_samples": empirical["samples"], "empirical_p50_seconds": empirical["p50_seconds"],
                "empirical_p85_seconds": empirical["p85_seconds"],
                "actual_seconds": forecast.get("actual_seconds"), "actual_at": forecast.get("actual_at"),
                "censored": forecast["censored"]}

    @classmethod
    def empirical_reference(cls, forecast: dict, outcomes: list[dict]) -> dict:
        rows = [row for row in outcomes if row.get("task_id") != forecast["task_id"]
                and row.get("stage") == forecast["stage"]
                and cls.same_cohort(row.get("cohort") or {}, forecast["cohort"])
                and row.get("cohort_changed") is not True
                and row.get("right_censored") is False
                and isinstance(row.get("observed_at"), (int, float))
                and not isinstance(row.get("observed_at"), bool)
                and row["observed_at"] < forecast["captured_at"]
                and LearnedDurationRanges.positive(row.get("size_points"))
                and LearnedDurationRanges.positive(row.get("duration_seconds"))]
        if len(rows) < MINIMUM_REFERENCE_OUTCOMES:
            return {"samples": len(rows), "p50_seconds": None, "p85_seconds": None}
        weights = [LearnedDurationRanges.weight(forecast["captured_at"] - row["observed_at"],
                                                RECENCY_HALF_LIFE_DAYS) for row in rows]
        effective = LearnedDurationRanges.effective_sample_count(weights)
        p50, p85 = LearnedDurationRanges.reference_class(rows, weights, forecast["size_points"], effective)
        return {"samples": len(rows), "p50_seconds": p50, "p85_seconds": p85}

    @classmethod
    def actual(cls, forecast: dict, outcomes: list[dict], as_of: float) -> dict | None:
        matches = [row for row in outcomes if row.get("task_id") == forecast["task_id"]
                   and row.get("stage") == forecast["stage"]
                   and cls.same_cohort(row.get("cohort") or {}, forecast["cohort"])
                   and isinstance(row.get("observed_at"), (int, float))
                   and not isinstance(row.get("observed_at"), bool)
                   and forecast["captured_at"] < row["observed_at"] <= as_of
                   and isinstance(row.get("duration_seconds"), (int, float))
                   and not isinstance(row.get("duration_seconds"), bool) and row["duration_seconds"] > 0]
        return min(matches, key=lambda row: row["observed_at"]) if matches else None

    @classmethod
    def valid_forecast(cls, row: dict, as_of: float) -> bool:
        return (isinstance(row, dict) and isinstance(row.get("task_id"), int) and row.get("task_id") > 0
                and row.get("stage") in ("execution_cycle", "delivery_delay")
                and LearnedDurationRanges.valid_cohort(row.get("cohort") or {})
                and all(cls.positive(row.get(name)) for name in
                        ("captured_at", "size_points", "p50_seconds", "p85_seconds"))
                and row["captured_at"] <= as_of and row.get("input_cut"))

    @staticmethod
    def same_cohort(left: dict, right: dict) -> bool:
        return LearnedDurationRanges.cohort(left) == LearnedDurationRanges.cohort(right)

    @classmethod
    def coverage(cls, rows: list[dict], name: str) -> dict:
        covered = sum(row["actual_seconds"] <= row[name] for row in rows)
        total = len(rows)
        return {"covered": covered, "observed": total, "percent": round(covered * 100 / total) if total else None}

    def drift(self, rows: list[dict]) -> dict:
        residuals = [math.log(row["actual_seconds"] / row["p50_seconds"]) for row in
                     sorted(rows, key=lambda row: (row["captured_at"], row["task_id"]))]
        middle = len(residuals) // 2
        earlier, recent = residuals[:middle], residuals[middle:]
        if len(earlier) < self.minimum_drift_samples or len(recent) < self.minimum_drift_samples:
            return {"status": "not_enough_history", "earlier_samples": len(earlier), "recent_samples": len(recent),
                    "recent_to_earlier_residual_ratio": None}
        earlier_mean = sum(earlier) / len(earlier)
        recent_mean = sum(recent) / len(recent)
        return {"status": "measured", "earlier_samples": len(earlier), "recent_samples": len(recent),
                "recent_to_earlier_residual_ratio": math.exp(recent_mean - earlier_mean)}

    @staticmethod
    def quantile(values: list[float], probability: float) -> float:
        ordered = sorted(values)
        return ordered[max(0, math.ceil(probability * len(ordered)) - 1)]

    @staticmethod
    def coverage_name(name: str) -> str:
        return {"p50_seconds": "p50", "p85_seconds": "raw_p85", "calibrated_p85_seconds": "calibrated_p85",
                "empirical_p50_seconds": "empirical_p50", "empirical_p85_seconds": "empirical_p85"}[name]

    @staticmethod
    def positive(value: object) -> bool:
        return (isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and value > 0)

    @staticmethod
    def moment(value) -> float | None:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        if isinstance(value, str) and value:
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
            except ValueError:
                return None
        return None
