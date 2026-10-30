import tomllib
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

from tests.lab.measurement import Measurement
from tests.lab.network_reading import NetworkReading
from tests.lab.run_reading import RunReading
from tests.lab.run_record import RunRecord
from tests.lab.run_request import RunRequest


NO_EFFECT_REASON = "deterministic paired null replay; no agent work or treatment effect was simulated"
EPOCH = datetime(2020, 1, 1, tzinfo=timezone.utc)


def run_one(request: RunRequest) -> RunRecord:
    scenario, business = scenario_data(request)
    task_count = sum(len(phase["tasks"]) for phase in scenario["phases"])
    expectation_count = len(scenario["expected"])
    role_count = len(business["roles"])
    route_latencies = tuple(float(draw(request, f"route:{index}", 40) + 1) for index in range(task_count))
    service_exposure = tuple(
        (draw(request, f"service:{index}", 5) + 1, float(scenario["budget"]["simulated_minutes"]))
        for index in range(role_count)
    )
    queue_waits = tuple(float(draw(request, f"wait:{index}", 60) + 1) for index in range(task_count))
    network = NetworkReading.from_simulator_observations(
        route_latencies,
        0,
        task_count,
        task_count,
        service_exposure,
        role_count,
        queue_waits,
        task_count,
        request.metric_schema_version,
    )
    reading = RunReading.missing(NO_EFFECT_REASON, request.metric_schema_version)
    goal = bool(draw(request, "goal", 2))
    met = draw(request, "expectations", expectation_count + 1)
    references = tuple(f"null-simulator:expectation:{index}" for index in range(expectation_count))
    reading = reading.with_measurement(
        "goal_reached",
        Measurement(goal, "observed", NO_EFFECT_REASON, 1, 1, (f"null-simulator:goal:{request.scenario.name}:{request.seed}",), request.metric_schema_version),
    )
    reading = reading.with_measurement(
        "expectations_met_share",
        Measurement(met / expectation_count, "observed", NO_EFFECT_REASON, expectation_count, expectation_count, references, request.metric_schema_version),
    )
    reading = reading.with_measurement(
        "cost_dollars",
        Measurement(0.0, "observed", "VoidProvider made no provider calls; this is not an invoice estimate", 1, 1, (f"null-simulator:zero-provider-cost:{request.run_id}",), request.metric_schema_version),
    )
    offset = draw(request, "timestamp", 1_000_000)
    started_at = EPOCH + timedelta(seconds=offset)
    ended_at = started_at + timedelta(minutes=int(scenario["budget"]["simulated_minutes"]))
    setup = Measurement(0.0, "observed", NO_EFFECT_REASON, 1, 1, (f"null-simulator:setup:{request.run_id}",), request.metric_schema_version)
    return RunRecord(
        request.run_id,
        request.attempt,
        request.scenario.name,
        request.scenario.version,
        request.scenario.business_type,
        request.design.digest,
        request.design.settings_digest,
        request.seed,
        request.source_commit,
        request.organization_commit,
        request.provider,
        request.model,
        True,
        request.metric_schema_version,
        started_at,
        ended_at,
        "completed",
        setup,
        reading,
        network,
    )


def scenario_data(request: RunRequest) -> tuple[dict, dict]:
    business_id, scenario_id = request.scenario.name.split("/", 1)
    scenario_path = Path(__file__).with_name("scenarios") / business_id / f"{scenario_id}.toml"
    business_path = Path(__file__).with_name("business_types") / f"{business_id}.toml"
    scenario_bytes = scenario_path.read_bytes()
    scenario = tomllib.loads(scenario_bytes.decode("utf-8"))
    business = tomllib.loads(business_path.read_text(encoding="utf-8"))
    if (
        sha256(scenario_bytes).hexdigest() != request.scenario.checksum
        or request.scenario.version != "1"
        or scenario["id"] != scenario_id
        or scenario["business_type"] != business_id
        or business["id"] != business_id
    ):
        raise ValueError("the simulator inputs differ from their pinned scenario identity")
    return scenario, business


def draw(request: RunRequest, label: str, limit: int) -> int:
    material = f"paired-null-v1:{request.scenario.checksum}:{request.seed}:{label}".encode()
    return int.from_bytes(sha256(material).digest()[:8], "big") % limit
