from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import tomllib

from journal.features.workers.organization_options import OrganizationOptions
from tests.lab.metric_rule import MetricRule
from tests.lab.scenario_pin import ScenarioPin
from tests.lab.trial_setting import TrialSetting


SEEDS = (20401, 20402, 20403)
BUSINESS_SCENARIOS = (
    ("software_company", "production_incident"),
    ("accountancy_firm", "payroll_tax_change"),
    ("dental_practice", "patient_records_breach"),
)
REAL_RUN_CAP_USD = 1.0
REAL_BATCH_CAP_USD = 20.0
MAX_RUNS_PER_BATCH = 20
RULE_VERSION = "doc10-section19-simulator-feasibility-v1"
FREEZE_DATE = "2026-10-30"
OWNER = "journal owner/operator"
NO_REAL_HISTORY = "not enough history: no calibrated real-run readings exist for these settings and business types"
PILOT_ONLY = "not applicable: simulator feasibility only; no real effectiveness decision or default change"


@dataclass(frozen=True)
class TrialBrief:
    """One frozen exploratory trial plan with a paired sample that stays within the selected cost caps."""

    trial_id: str
    question: str
    setting: TrialSetting
    primary: MetricRule
    scenarios: tuple[ScenarioPin, ...]
    hard_gates: tuple[str, ...]
    guard_metrics: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.trial_id.strip() or not self.question.strip():
            raise ValueError("a trial brief needs its ID and question")
        if self.primary.role != "primary":
            raise ValueError("a trial brief needs its one primary metric")
        if len(self.scenarios) != len(BUSINESS_SCENARIOS) or {scenario.business_type for scenario in self.scenarios} != {business for business, _ in BUSINESS_SCENARIOS}:
            raise ValueError("the first trial sample needs one pinned scenario for each selected business type")
        if self.paired_units != 9 or self.run_count != 18 or self.run_count > MAX_RUNS_PER_BATCH:
            raise ValueError("the exploratory sample must fit the selected per-batch run cap")
        if self.run_count * REAL_RUN_CAP_USD > REAL_BATCH_CAP_USD:
            raise ValueError("the exploratory sample exceeds the selected USD caps")
        if not self.hard_gates or any(not item.strip() for item in (*self.hard_gates, *self.guard_metrics)):
            raise ValueError("a trial brief needs named gates and guards")

    @property
    def paired_units(self) -> int:
        return len(self.scenarios) * len(SEEDS)

    @property
    def run_count(self) -> int:
        return self.paired_units * 2

    def manifest(self) -> dict[str, object]:
        settings = self.setting.manifest()
        design_a, design_b = self.setting.designs("A", "B", {})
        body = {
            "trial": {
                "id": self.trial_id,
                "rule_version": RULE_VERSION,
                "frozen_at": FREEZE_DATE,
                "question": self.question,
                "kind": "comparative simulator feasibility pilot",
                "authority": "user controls the setting; this pilot authorizes no real spend or default change",
                "setting": settings,
                "design_a": design_a.manifest(),
                "design_b": design_b.manifest(),
            },
            "inputs": [asdict(scenario) for scenario in self.scenarios],
            "population": {
                "business_types": [scenario.business_type for scenario in self.scenarios],
                "weights": "one scenario per type, equal descriptive weight; no pooling across types",
            },
            "paired_unit": "scenario and seed",
            "primary": asdict(self.primary),
            "hard_gates": list(self.hard_gates),
            "guard_metrics": [
                {"metric": metric, "margin": "not_applicable", "reason": PILOT_ONLY}
                for metric in self.guard_metrics
            ],
            "exploratory": "simulator readings are feasibility evidence only and cannot justify keeping a change",
            "analysis": {
                "method": "not_applicable",
                "reason": PILOT_ONLY,
                "confirmatory_alpha": 0.05,
                "confirmatory_family": "the four primaries and every statistical guard used to keep a candidate, with Holm FWER alpha 0.05 after real evidence and guard margins are approved",
            },
            "history": NO_REAL_HISTORY,
            "sample": {
                "seeds_per_scenario": list(SEEDS),
                "paired_units": self.paired_units,
                "run_count": self.run_count,
                "target_power_and_precision": "not_applicable: feasibility pilot; no powered confirmatory sample is claimed",
                "run_order": "A then B within each scenario and seed; fixed for reproducible simulator runs",
            },
            "missing_and_capped": {
                "missing_pair": "exclude from descriptive paired difference and retain as missing; any missing real evidence is inconclusive",
                "capped_run": "retain terminal record; no replacement in this pilot",
                "coverage": "every scenario and seed must have both designs for a complete pair",
            },
            "budgets": {
                "provider": "VoidProvider",
                "model": "paired-null-simulator",
                "model_scope": "deterministic paired null replay; it does not execute agent work or estimate treatment effects",
                "simulator_cost_usd": 0,
                "real_max_usd_per_run": REAL_RUN_CAP_USD,
                "real_max_usd_per_batch": REAL_BATCH_CAP_USD,
                "planned_run_count": self.run_count,
                "maximum_if_real_usd": self.run_count * REAL_RUN_CAP_USD,
                "max_runs_per_batch": MAX_RUNS_PER_BATCH,
                "real_batch_approval": "not approved; task 213 key launcher is unavailable and question 30 non-cost caps remain owner_pending",
            },
            "stop_rule": "stop on a simulator fault, missing pair, or run cap; no early efficacy look and no default change",
            "keep": "not_applicable to simulator; real calibrated evidence, all gates and owner approval are required",
            "drop": "not_applicable to simulator; a real predeclared hard-gate failure or unacceptable harm requires rollback",
            "inconclusive": "all simulator-only outcomes and all real comparisons before an approved real batch",
            "disposition": "retain the candidate behind its owner setting; record the pilot; re-freeze before any real confirmatory batch",
            "result": None,
        }
        digest = sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        return {**body, "decision_rule_digest": digest}


def first_trial_briefs() -> tuple[TrialBrief, ...]:
    scenarios = pinned_scenarios()
    return (
        TrialBrief(
            "hub-route-strategy",
            "Does same-domain peer routing lower the median time to a delivered handoff without violating a route?",
            TrialSetting(OrganizationOptions.HUB_ROUTE_STRATEGY, OWNER, "containment", "same_domain_peers"),
            MetricRule("handoff_latency_median_minutes", "continuous", "lower", "primary", 0.1),
            scenarios,
            ("complete delivery-linked route identity coverage", "zero unauthorized route violations"),
            (),
        ),
        TrialBrief(
            "shared-role-queue-order",
            "Does arrival order improve Jain fairness for a shared journal Role without excessive queue wait?",
            TrialSetting(OrganizationOptions.SHARED_ROLE_QUEUE_ORDER, OWNER, "plans_in_turn", "arrival"),
            MetricRule(
                "queue_fairness_jain", "continuous", "higher", "primary", 0.01,
                ratio_formula="Jain index of service starts per eligible backlogged minute",
                zero_unknown_denominator_rule="no eligible demand or all-zero starts is not_applicable; unknown exposure is missing",
            ),
            scenarios,
            ("every eligible Role is represented, including zero-service contenders",),
            ("role_queue_wait_p85_minutes",),
        ),
        TrialBrief(
            "domain-agent-model-tier",
            "Does the lowest user-allowed Domain agent model tier improve the share of expectations met?",
            TrialSetting(OrganizationOptions.DOMAIN_AGENT_MODEL_TIER, OWNER, "contract", "lowest_allowed"),
            MetricRule(
                "expectations_met_share", "continuous", "higher", "primary", 0.01,
                ratio_formula="met expectations / required expectations",
                zero_unknown_denominator_rule="zero required expectations is not_applicable; unknown requirements are missing",
            ),
            scenarios,
            ("provider, model and reasoning effort are pinned for each paired run",),
            ("cost_dollars",),
        ),
        TrialBrief(
            "solo-versus-organization-by-type",
            "Does solo mode improve goal completion for each business type without breaking invariants, approvals or write scope?",
            TrialSetting(OrganizationOptions.PLAN_MODE, OWNER, "organization", "solo"),
            MetricRule("goal_reached", "binary", "higher", "primary", 1.0),
            scenarios,
            ("journal invariants hold", "approval scope is respected", "writes stay inside the assigned worktree"),
            ("cost_dollars",),
        ),
    )


def pinned_scenarios() -> tuple[ScenarioPin, ...]:
    root = Path(__file__).with_name("scenarios")
    pins = []
    for business, name in BUSINESS_SCENARIOS:
        path = root / business / f"{name}.toml"
        content = path.read_bytes()
        data = tomllib.loads(content.decode("utf-8"))
        pins.append(ScenarioPin(
            f"{business}/{name}", business, "1", sha256(content).hexdigest(), int(data["budget"]["simulated_minutes"]),
        ))
    return tuple(pins)
