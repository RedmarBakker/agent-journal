import math


METHOD_VERSION = "bayesian-log-linear-duration-v1"
MINIMUM_MODEL_OUTCOMES = 10
MINIMUM_REFERENCE_OUTCOMES = 3
RECENCY_HALF_LIFE_DAYS = 180
P85_NORMAL_QUANTILE = 1.0364333894937898
COHORT_DIMENSIONS = ("environment_id", "domain", "size_scale_version", "criteria_version", "model", "tier", "cohort_version")
STAGES = ("execution_cycle", "delivery_delay")


class LearnedDurationRanges:
    """Estimates elapsed execution and delivery durations within a frozen outcome cohort."""

    def estimate(self, observations: list[dict], cohort: dict, size_points: int | None, as_of: float,
                 recency_half_life_days: float = RECENCY_HALF_LIFE_DAYS) -> dict:
        results = {stage: self.stage(observations, cohort, size_points, as_of, stage, recency_half_life_days)
                   for stage in STAGES}
        statuses = [row["status"] for row in results.values()]
        status = "forecast" if "forecast" in statuses else "not_enough_history"
        return {"status": status, "method_version": METHOD_VERSION, "cohort": self.cohort(cohort),
                "size_points": size_points, "as_of": as_of, "stages": results,
                "wait_accounting": "execution and delivery use separate elapsed intervals; waits are not added again"}

    def estimate_task(self, observations: list[dict], task: dict, as_of: float) -> dict:
        task_id = task.get("task_id")
        history = [row for row in observations if row.get("task_id") != task_id]
        return self.estimate(history, task.get("cohort") or {}, task.get("size_points"), as_of)

    def stage(self, observations: list[dict], cohort: dict, size_points: int | None, as_of: float,
              stage: str, recency_half_life_days: float) -> dict:
        if not self.valid_cohort(cohort) or not self.positive(size_points):
            return self.empty("incomplete cohort or unknown size")
        changed = [row for row in observations if self.matches(row, cohort, stage, as_of) and row.get("cohort_changed") is True]
        rows = [row for row in observations if self.matches(row, cohort, stage, as_of) and row.get("cohort_changed") is not True]
        completed = [row for row in rows if not row["right_censored"]]
        censored = [row for row in rows if row["right_censored"]]
        weights = [self.weight(as_of - row["observed_at"], recency_half_life_days) for row in completed]
        effective = self.effective_sample_count(weights)
        if len(completed) < MINIMUM_REFERENCE_OUTCOMES:
            return {**self.empty("not enough comparable completed outcomes"),
                    "completed_samples": len(completed), "censored_samples": len(censored),
                    "effective_sample_count": round(effective, 3), "cohort_changed_samples": len(changed)}
        fit = self.log_linear(completed, weights, size_points) if len(completed) >= MINIMUM_MODEL_OUTCOMES else None
        if fit is None:
            ranges = self.reference_class(completed, weights, size_points, effective)
            method = "empirical_reference_class"
            limitations = ["sparse reference class; range is widened by observed cohort variability"]
        else:
            ranges = self.predictive(fit, size_points)
            method = "bayesian_log_linear"
            limitations = []
        ranges, adjusted = self.censor_floor(ranges, fit, censored, size_points)
        if censored:
            limitations.append("right-censored work constrains the upper range as a lower bound")
        if changed:
            limitations.append("outcomes spanning a model or tier change were excluded from this cohort")
        return {"status": "forecast", "method": method, "p50_seconds": ranges[0], "p85_seconds": ranges[1],
                "completed_samples": len(completed), "censored_samples": len(censored),
                "effective_sample_count": round(effective, 3), "cohort_changed_samples": len(changed),
                "recency_half_life_days": recency_half_life_days,
                "censor_adjusted": adjusted, "wait_accounting": "elapsed stage time already includes waits",
                "limitations": limitations}

    @staticmethod
    def empty(reason: str) -> dict:
        return {"status": "not_enough_history", "method": None, "p50_seconds": None, "p85_seconds": None,
                "completed_samples": 0, "censored_samples": 0, "effective_sample_count": 0.0,
                "recency_half_life_days": RECENCY_HALF_LIFE_DAYS, "censor_adjusted": False,
                "wait_accounting": "elapsed stage time already includes waits", "limitations": [reason]}

    @staticmethod
    def cohort(value: dict) -> dict:
        return {name: value.get(name) for name in COHORT_DIMENSIONS}

    @classmethod
    def valid_cohort(cls, cohort: dict) -> bool:
        return isinstance(cohort, dict) and all(cohort.get(name) not in (None, "")
                                                for name in COHORT_DIMENSIONS[:4])

    @classmethod
    def matches(cls, row: dict, cohort: dict, stage: str, as_of: float) -> bool:
        return (isinstance(row, dict) and row.get("stage") == stage
                and cls.cohort(row.get("cohort") or {}) == cls.cohort(cohort)
                and cls.positive(row.get("size_points"))
                and cls.positive(row.get("duration_seconds"))
                and isinstance(row.get("observed_at"), (int, float))
                and not isinstance(row.get("observed_at"), bool) and row["observed_at"] <= as_of
                and isinstance(row.get("right_censored"), bool))

    @staticmethod
    def log_linear(rows: list[dict], weights: list[float], size_points: int) -> dict | None:
        sizes = {row["size_points"] for row in rows}
        if len(sizes) < 2:
            return None
        x = [math.log(row["size_points"]) for row in rows]
        y = [math.log(row["duration_seconds"]) for row in rows]
        total = sum(weights)
        x_mean = sum(value * weight for value, weight in zip(x, weights)) / total
        y_mean = sum(value * weight for value, weight in zip(y, weights)) / total
        spread = sum(weight * (value - x_mean) ** 2 for value, weight in zip(x, weights))
        covariance = sum(weight * (x_value - x_mean) * (y_value - y_mean)
                         for x_value, y_value, weight in zip(x, y, weights))
        slope = (covariance + 1.0) / (spread + 1.0)
        intercept = y_mean - slope * x_mean
        residuals = [value - (intercept + slope * x_value) for x_value, value in zip(x, y)]
        variance = max(0.0025, sum(weight * value**2 for value, weight in zip(residuals, weights)) / total)
        effective = LearnedDurationRanges.effective_sample_count(weights)
        prediction_variance = variance * (1 + 1 / max(1.0, effective) + (math.log(size_points) - x_mean) ** 2 / (spread + 1))
        return {"intercept": intercept, "slope": slope, "variance": prediction_variance}

    @staticmethod
    def predictive(fit: dict, size_points: int) -> tuple[float, float]:
        median = math.exp(fit["intercept"] + fit["slope"] * math.log(size_points))
        p85 = median * math.exp(P85_NORMAL_QUANTILE * math.sqrt(fit["variance"]))
        return median, p85

    @classmethod
    def reference_class(cls, rows: list[dict], weights: list[float], size_points: int,
                        effective: float) -> tuple[float, float]:
        per_point = [(math.log(row["duration_seconds"] / row["size_points"]), weight)
                     for row, weight in zip(rows, weights)]
        p50 = math.exp(cls.weighted_quantile(per_point, 0.5)) * size_points
        observed_p85 = math.exp(cls.weighted_quantile(per_point, 0.85)) * size_points
        sparse_widening = math.exp(P85_NORMAL_QUANTILE / math.sqrt(max(1.0, effective)))
        return p50, max(p50, observed_p85) * sparse_widening

    @classmethod
    def censor_floor(cls, ranges: tuple[float, float], fit: dict | None, censored: list[dict], size_points: int) -> tuple[tuple[float, float], bool]:
        if not censored:
            return ranges, False
        if fit:
            residuals = [math.log(row["duration_seconds"]) -
                         (fit["intercept"] + fit["slope"] * math.log(row["size_points"])) for row in censored]
            bound = ranges[0] * math.exp(max(0.0, max(residuals)))
        else:
            bound = max(row["duration_seconds"] / row["size_points"] * size_points for row in censored)
        bound = math.ceil(bound)
        return (ranges[0], max(ranges[1], bound)), bound > ranges[1]

    @staticmethod
    def weighted_quantile(values: list[tuple[float, float]], probability: float) -> float:
        ordered = sorted(values)
        boundary = probability * sum(weight for _value, weight in ordered)
        running = 0.0
        for value, weight in ordered:
            running += weight
            if running >= boundary:
                return value
        return ordered[-1][0]

    @staticmethod
    def weight(age_seconds: float, half_life_days: float) -> float:
        return math.exp(-math.log(2) * max(0.0, age_seconds) / (half_life_days * 86400))

    @staticmethod
    def effective_sample_count(weights: list[float]) -> float:
        total = sum(weights)
        return total**2 / sum(weight**2 for weight in weights) if total else 0.0

    @staticmethod
    def positive(value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0
