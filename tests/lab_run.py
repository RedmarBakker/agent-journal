"""Opt-in lab checks for readings, batches, paired comparisons and child-process runs."""

import json
from dataclasses import asdict, replace
from datetime import datetime, timezone
import os
from pathlib import Path
import stat

import pytest

from journal.features.organization.support.hub_traffic_audit import HubTrafficFinding
from journal.features.organization.support.organization import Organization
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.support.ref import Ref
from journal.features.workers.organization_options import OrganizationOptions
from journal.models.worker import Worker
from journal.models.plan_mode import PlanMode
from journal.repositories.proofs import Proofs
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.lab.actors.domain_agent_actor import DomainAgentActor
from tests.lab.batch import Batch
from tests.lab.batch_runner import BatchRunner
from tests.lab.business_type import BusinessType
from tests.lab.design import Design
from tests.lab.lab_journal import LabJournal
from tests.lab.lab_scenario import LabScenario
from tests.lab.measurement import Measurement
from tests.lab.network_reading import NETWORK_METRICS, NetworkReading, nearest_rank
from tests.lab.primary_role_route import PrimaryRoleRoute
from tests.lab.actors.role_actor import RoleActor
from tests.lab.run_reading import RUN_METRICS, SETUP_CHECKS, RunReading
from tests.lab.run_record import RunRecord
from tests.lab.run_request import RunRequest
from tests.lab.scenario_pin import ScenarioPin
from tests.lab.simulation_caps import SimulationCaps
from tests.simulation.shrinker import Shrinker
from tests.simulation.trace_entry import TraceEntry
from tests.simulation.trace_file import TraceFile


RUN_METRIC_CONTRACT = {
    "goal_reached", "expectations_met_share", "work_on_main", "approvals_respected",
    "writes_outside_worktree", "judge_score", "minutes_to_done", "critical_path_ratio",
    "cost_units", "cost_dollars", "agent_turns", "tool_uses", "send_backs", "short_proofs",
    "reopened_tasks", "wait_releases", "blocks_count", "blocked_minutes_share", "longest_wait_minutes",
    "idle_seat_minutes", "nudges_per_hour", "refusals_per_hour", "invariants_broken", "faults",
}

NETWORK_METRIC_CONTRACT = {
    "messages_per_edge_kind", "hops_per_handoff", "hops_per_handoff_median", "hops_per_handoff_p85",
    "unaccepted_handoffs", "uncorrelated_handoffs", "route_violations", "unresolved_route_identities",
    "handoff_latency_median_minutes", "handoff_latency_p85_minutes", "censored_handoffs",
    "handoff_rework_count", "handoff_rework_share", "censored_rework_followups", "escalations",
    "escalation_resolution_minutes", "escalation_resolution_median_minutes", "escalation_resolution_p85_minutes",
    "open_escalations", "role_queue_wait_minutes", "role_queue_wait_median_minutes", "role_queue_wait_p85_minutes",
    "pending_role_queue_wait_minutes", "cancelled_role_queue_jobs", "queue_fairness_jain", "domain_fan_out",
    "plan_message_share",
}


def measurement(value, status="observed", observed=1, expected=1, reason="evidence recorded", sources=("source:1",)):
    return Measurement(value, status, reason, observed, expected, sources, "1")


def lab_journal_request(root: Path, home: Path, plan_mode: PlanMode | None = None) -> RunRequest:
    settings = {"workers.cost_cap_dollars": 3}
    if plan_mode is not None:
        settings[OrganizationOptions.PLAN_MODE.key] = plan_mode.value
    return RunRequest(
        "a" * 32, 1, ScenarioPin("production_incident", "software_company", "1", "b" * 64, 420),
        Design.from_mapping("baseline", settings), 17, "VoidProvider", "synthetic-tier",
        "c" * 40, "d" * 40, "1", 420, root, home, root / "result.json",
    )


def lab_task_domains(scenario, scenario_rows) -> dict[int, str]:
    return {
        scenario_rows["task_ids"][task["id"]]: task["domain"]
        for phase in scenario.phases
        for task in phase["tasks"]
    }


def lab_task_prerequisites(scenario, scenario_rows) -> dict[int, tuple[int, ...]]:
    task_ids = scenario_rows["task_ids"]
    return {
        task_ids[task["id"]]: tuple(task_ids[prerequisite] for prerequisite in task["prerequisites"])
        for phase in scenario.phases
        for task in phase["tasks"]
    }


def lab_behaviour_profile(agent_kind, model_tier, line_follow, escalation, handoff_error, out_of_route, out_of_worktree):
    from tests.lab.behaviour_profile import BehaviourProfile
    from tests.simulation.scenarios import JOB_DECILES

    def observations(rate):
        if not 0 <= rate <= 1:
            raise ValueError("a test profile rate is between zero and one")
        count = round(rate * 100)
        return (True,) * count + (False,) * (100 - count)

    samples = {
        "job_length_minutes": tuple(value for value in JOB_DECILES for _ in range(10)),
        "send_back_count": (0,) * 70 + (1,) * 22 + (2,) * 5 + (3,) * 3,
        "line_followed": observations(line_follow),
        "escalated": observations(escalation),
        "handoff_error": observations(handoff_error),
        "outside_route": observations(out_of_route),
        "outside_worktree": observations(out_of_worktree),
    }
    refs = {metric: (f"synthetic://lab-test/{agent_kind}/{model_tier}/{metric}",) for metric in samples}
    return BehaviourProfile.fit(agent_kind, model_tier, samples, refs)


def lab_role_worker(lab, role, task, session):
    actor = Actor.system()
    worker = lab.app.container.get(Workers).save(Worker(
        environment_id=task.environment_id,
        name=role.title,
        brief=task.brief,
        role=role.id,
        contract=lab.app.container.get(Organization).contracts().version,
        plan_id=lab.scenario_rows["plan_id"],
        session=session,
        worktree=True,
    ), actor)
    lab.app.container.get(Tasks).handover(task, Ref.build(worker), actor)
    return worker


def test_a_lab_journal_loads_its_scenario_and_replaces_process_and_openrig_calls(tmp_path, monkeypatch):
    from journal.engine.agent_launcher import AgentLauncher
    from journal.features.organization.support.seat_runtime import SeatRuntime
    from journal.features.plans.plans_options import PlansOptions
    from journal.features.workers.organization_options import OrganizationOptions
    from journal.models.plan_state import PlanState
    from journal.repositories.plans import Plans
    from journal.repositories.setting_rows import SettingRows
    from tests.lab.business_type import BusinessType
    from tests.lab.lab_journal import LabJournal
    from tests.lab.lab_scenario import LabScenario

    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    run = lab_journal_request(tmp_path / "root", tmp_path / "home")

    with LabJournal(run, scenario, business, monkeypatch) as lab:
        settings = lab.app.container.get(SettingRows)
        assert settings.option(PlansOptions.PLAN_AGENTS) is True
        assert settings.option(OrganizationOptions.FOLDER) == str(lab.organization_folder)
        plan = lab.app.container.get(Plans).find(lab.scenario_rows["plan_id"])
        assert plan.state is PlanState.APPROVED
        assert len(lab.scenario_rows["task_ids"]) == 3
        assert (lab.organization_folder / "domains" / "engineering" / "AGENTS.md").is_file()

        launcher = lab.app.container.get(AgentLauncher)
        assert launcher.start_in_worktree("scenario-plan", "claude", ("--resume", "native"), ("repo",)) > 0
        assert lab.launches[-1] == {
            "environment": "scenario-plan", "agent": "claude", "resume": ("--resume", "native"), "repositories": ("repo",),
        }
        runtime = lab.app.container.get(SeatRuntime)
        assert runtime.version() == "0.7.5"
        assert lab.seats.calls[-1] == ("--version",)
        spec = lab.root / ".journal" / "runtime" / "rigs" / "simulated" / "rig.yaml"
        runtime.start_rig(spec)
        assert runtime.rig_exists("simulated")
        assert ("up", str(spec), "--json") in lab.seats.calls


def test_a_lab_journal_refuses_to_reuse_a_root_with_a_journal(tmp_path, monkeypatch):
    from tests.lab.business_type import BusinessType
    from tests.lab.lab_journal import LabJournal
    from tests.lab.lab_scenario import LabScenario

    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    run = lab_journal_request(tmp_path / "root", tmp_path / "home")
    (run.root / ".journal").mkdir(parents=True)

    with pytest.raises(ValueError, match="fresh journal root"):
        LabJournal(run, scenario, business, monkeypatch)


def test_the_coordinator_starts_plans_and_a_solo_plan_agent_works_as_one_role_at_a_time(tmp_path, monkeypatch):
    from journal.features.organization.states.role_work import RoleWork
    from tests.lab.actors.coordinator_actor import CoordinatorActor
    from tests.lab.actors.plan_agent_actor import PlanAgentActor
    from tests.lab.business_type import BusinessType
    from tests.lab.lab_journal import LabJournal
    from tests.lab.lab_scenario import LabScenario

    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    run = lab_journal_request(tmp_path / "root", tmp_path / "home", PlanMode.SOLO)

    with LabJournal(run, scenario, business, monkeypatch) as lab:
        coordinator = CoordinatorActor(lab.simulator)
        assert not coordinator.session_start().is_refused()
        main = lab.app.container.get(Environments).lookup("main")
        assert lab.app.container.get(Agents).session_agent(coordinator.session_id).environment_id == main.row_id
        started = coordinator.start_plans((lab.scenario_rows["plan_id"],))
        assert len(started) == 1
        assert started[0].answer[0] == 0

        plan = lab.app.container.get(Plans).find(lab.scenario_rows["plan_id"])
        environment = lab.app.container.get(PlanAgents).environment(plan)
        assert plan.mode == PlanMode.SOLO
        assert lab.launches[-1]["environment"] == environment.name
        agent = PlanAgentActor(
            lab.simulator, plan.id, environment.name, plan.mode,
            lab_task_domains(scenario, lab.scenario_rows), lab_task_prerequisites(scenario, lab.scenario_rows),
        )
        assert not agent.session_start().is_refused()
        assert lab.app.container.get(Agents).session_agent(agent.session_id).environment_id == environment.row_id
        with pytest.raises(RuntimeError, match="organization Plan agent"):
            agent.handoffs()

        first = agent.take_role("engineering_lead")
        assert first.answer[0] == 0
        assert first.stack[-1] == RoleWork.name
        with pytest.raises(RuntimeError, match="one Role at a time"):
            agent.take_role("software_engineer")

        ended = agent.finish_role()
        assert ended.answer[0] == 0
        assert RoleWork.name not in ended.stack
        second = agent.take_role("software_engineer")
        assert second.answer[0] == 0
        agent.finish_role()


def test_an_organization_plan_agent_hands_tasks_to_domains_and_cannot_take_a_role(tmp_path, monkeypatch):
    from tests.lab.actors.coordinator_actor import CoordinatorActor
    from tests.lab.actors.plan_agent_actor import PlanAgentActor
    from tests.lab.business_type import BusinessType
    from tests.lab.lab_journal import LabJournal
    from tests.lab.lab_scenario import LabScenario

    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    run = lab_journal_request(tmp_path / "root", tmp_path / "home", PlanMode.ORGANIZATION)

    with LabJournal(run, scenario, business, monkeypatch) as lab:
        coordinator = CoordinatorActor(lab.simulator)
        assert not coordinator.session_start().is_refused()
        started = coordinator.start_plans((lab.scenario_rows["plan_id"],))
        assert len(started) == 1
        assert started[0].answer[0] == 0

        plan = lab.app.container.get(Plans).find(lab.scenario_rows["plan_id"])
        environment = lab.app.container.get(PlanAgents).environment(plan)
        assert plan.mode == PlanMode.ORGANIZATION
        assert any(call[0] == "up" for call in lab.seats.calls)
        agent = PlanAgentActor(
            lab.simulator, plan.id, environment.name, plan.mode,
            lab_task_domains(scenario, lab.scenario_rows), lab_task_prerequisites(scenario, lab.scenario_rows),
        )
        assert not agent.session_start().is_refused()
        assert lab.app.container.get(Agents).session_agent(agent.session_id).environment_id == environment.row_id

        tasks = lab.scenario_rows["task_ids"]
        assert agent.handoffs() == ((tasks["assess_customer_impact"], "customer_success"),)
        assert agent.handoffs((tasks["assess_customer_impact"],)) == ((tasks["restore_service_health"], "engineering"),)
        assert agent.handoffs((tasks["assess_customer_impact"], tasks["restore_service_health"])) == ((tasks["write_postmortem"], "security"),)
        refused = agent.take_role("engineering_lead")
        assert refused.answer[0] != 0
        assert agent.active_role == ""


def test_a_behaviour_profile_uses_measured_week_samples_for_one_agent_and_tier():
    import random

    from tests.lab.behaviour_profile import BehaviourProfile
    from tests.simulation.scenarios import JOB_DECILES, SEND_BACK_SHARES

    profile = lab_behaviour_profile("domain", "sonnet", 0.8, 0.8, 0.8, 0.8, 0.8)
    same = lab_behaviour_profile("domain", "sonnet", 0.8, 0.8, 0.8, 0.8, 0.8)
    first_random, same_random = random.Random(31), random.Random(31)

    assert (profile.agent_kind, profile.model_tier) == ("domain", "sonnet")
    assert profile.metrics["job_length_deciles_minutes"]["value"] == JOB_DECILES
    assert profile.metrics["send_back_shares"]["value"] == SEND_BACK_SHARES
    assert [profile.job_seconds(first_random) for _ in range(3)] == [same.job_seconds(same_random) for _ in range(3)]
    assert profile.follows_line(random.Random(1))
    assert profile.escalates(random.Random(1))
    assert profile.misses_handoff(random.Random(1))
    assert profile.routes_outside(random.Random(1))
    assert profile.writes_outside_worktree(random.Random(1))
    with pytest.raises(ValueError, match="observations must be true or false"):
        BehaviourProfile.fit("domain", "sonnet", {"line_followed": (1.1,)}, {"line_followed": ("synthetic://invalid",)})


def test_a_domain_agent_routes_by_contract_or_its_sampled_route_error(tmp_path, monkeypatch):
    from journal.features.organization.support.organization import Organization
    from tests.lab.actors.domain_agent_actor import DomainAgentActor
    from tests.lab.business_type import BusinessType
    from tests.lab.behaviour_profile import BehaviourProfile
    from tests.lab.lab_journal import LabJournal
    from tests.lab.lab_scenario import LabScenario

    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    run = lab_journal_request(tmp_path / "root", tmp_path / "home", PlanMode.ORGANIZATION)

    with LabJournal(run, scenario, business, monkeypatch) as lab:
        domain = lab.app.container.get(Organization).contracts().domain("engineering")
        followed = lab_behaviour_profile("domain", "sonnet", 1.0, 1.0, 0.0, 0.0, 0.0)
        errant = lab_behaviour_profile("domain", "sonnet", 1.0, 1.0, 0.0, 1.0, 0.0)
        agent = DomainAgentActor(lab.simulator, domain, "main", followed, 4)
        assert not agent.session_start().is_refused()
        assert agent.route("a product change") == "engineering_lead"
        assert agent.follows_line()
        assert agent.escalates()

        careless = DomainAgentActor(lab.simulator, domain, "main", errant, 4)
        assert careless.route("a product change") in domain.roles
        assert careless.route("a product change") != "engineering_lead"
        ignores_route = lab_behaviour_profile("domain", "sonnet", 0.0, 0.0, 0.0, 0.0, 0.0)
        inattentive = DomainAgentActor(lab.simulator, domain, "main", ignores_route, 4)
        assert inattentive.route("a product change") != "engineering_lead"


def test_a_role_writer_records_work_commit_and_proof_while_a_reader_sends_a_report(tmp_path, monkeypatch):
    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    run = lab_journal_request(tmp_path / "root", tmp_path / "home", PlanMode.ORGANIZATION)

    with LabJournal(run, scenario, business, monkeypatch) as lab:
        contracts = lab.app.container.get(Organization).contracts()
        role = contracts.role("software_engineer")
        environment_id = lab.app.container.get(Environments).lookup("main").id
        scope = lab.app.container.get(Scope)
        with scope.environment(environment_id):
            task = lab.app.container.get(Tasks).find(lab.scenario_rows["task_ids"]["restore_service_health"])
            worker = lab_role_worker(lab, role, task, "lab-role-writer")
            writer = RoleActor(
                lab.simulator,
                role,
                Caller.worker("main", worker.id, worker.session, "claude"),
                lab_behaviour_profile("role", "sonnet", 0.8, 0.0, 0.0, 0.0, 0.0),
                11,
            )
            assert not writer.session_start().is_refused()
            assert writer.clock_in().answer[0] == 0
            assert not writer.write("src/recovery.py", "RECOVERED = True\n").is_refused()
            assert not writer.commit("record recovery").is_refused()
            assert writer.prove(1, "src/recovery.py:1").answer[0] == 0
            assert lab.simulator.ledger.commits[-1][1] == "record recovery"
            assert lab.simulator.ledger.lines() == 1
            assert [proof.point for proof in lab.app.container.get(Proofs).task_proofs(task)] == [1]

        reader = RoleActor(
            lab.simulator,
            contracts.role("product_manager"),
            Caller.agent("main", "lab-role-reader", "claude"),
            lab_behaviour_profile("role", "sonnet", 0.8, 0.0, 0.0, 0.0, 0.0),
            12,
        )
        assert not reader.session_start().is_refused()
        assert reader.report("The customer impact is scoped.").answer[0] == 0


def test_a_role_receives_a_handoff_with_the_profiled_error_and_worktree_behavior(tmp_path, monkeypatch):
    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    run = lab_journal_request(tmp_path / "root", tmp_path / "home", PlanMode.ORGANIZATION)

    with LabJournal(run, scenario, business, monkeypatch) as lab:
        role = lab.app.container.get(Organization).contracts().role("software_engineer")
        environment_id = lab.app.container.get(Environments).lookup("main").id
        with lab.app.container.get(Scope).environment(environment_id):
            task = lab.app.container.get(Tasks).find(lab.scenario_rows["task_ids"]["restore_service_health"])
            worker = lab_role_worker(lab, role, task, "lab-role-careless")
        profile = lab_behaviour_profile("role", "sonnet", 0.0, 0.0, 1.0, 0.0, 1.0)
        caller = Caller.worker("main", worker.id, worker.session, "claude")
        actor = RoleActor(lab.simulator, role, caller, profile, 5)
        assert not actor.session_start().is_refused()
        assert actor.clock_in().answer[0] == 0
        received = actor.receive_handoff({"health report": "stable", "logs": "empty"})

        assert len(received) == 1
        assert len(actor.missed_inputs) == 1
        written = actor.write("src/recovery.py", "RECOVERED = True\n")
        assert not written.is_refused()
        assert lab.simulator.ledger.pending["../src/recovery.py"] == 1


def test_the_outside_world_answers_due_questions_and_the_user_can_be_away(tmp_path, monkeypatch):
    import random

    from journal.repositories.questions import Questions
    from journal.repositories.environments import Environments
    from journal.repositories.scope import Scope
    from journal.support.caller import Caller
    from tests.lab.actors.outside_world_actor import OutsideWorldActor
    from tests.lab.behaviour_profile import BehaviourProfile
    from tests.lab.business_type import BusinessType
    from tests.lab.lab_journal import LabJournal
    from tests.lab.lab_scenario import LabScenario
    from tests.simulation.user_actor import UserActor

    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    run = lab_journal_request(tmp_path / "root", tmp_path / "home")

    with LabJournal(run, scenario, business, monkeypatch) as lab:
        caller = Caller.agent("main", "lab-questioner", "claude")
        lab.simulator.hook("SessionStart", session=caller.session, environment=caller.environment, source="startup")
        for party in ("customer", "insurer", "court"):
            asked = lab.simulator.run(["question", "ask", f"What does the {party} report?"], caller)
            assert asked.answer[0] == 0
        scope = lab.app.container.get(Scope)
        main = lab.app.container.get(Environments).lookup("main")
        with scope.environment(main.id):
            questions = lab.app.container.get(Questions).open()
        profile = lab_behaviour_profile("outside_world", "external", 0.8, 0.0, 0.0, 0.0, 0.0)
        outside = OutsideWorldActor(lab.simulator, profile, 3)
        parties = ("customer", "insurer", "court")
        due = [
            outside.answer_after(question.id, f"The {party} confirms recovery.", party)
            for party, question in zip(parties, questions)
        ]
        assert all(moment > lab.simulator.source.seconds() for moment in due)
        assert outside.release_due() == ()
        lab.simulator.advance(max(due) - lab.simulator.source.seconds())
        released = outside.release_due()
        assert len(released) == 3 and all(result.answer[0] == 0 for result in released)
        expected_release_order = [parties[index] for index in sorted(range(len(due)), key=due.__getitem__)]
        assert [party for party, _, _ in outside.released] == expected_release_order
        with scope.environment(main.id):
            assert [lab.app.container.get(Questions).find(question.id).answer for question in questions] == [
                "The customer confirms recovery.", "The insurer confirms recovery.", "The court confirms recovery.",
            ]

        asked = lab.simulator.run(["question", "ask", "Can the control change proceed?"], caller)
        assert asked.answer[0] == 0
        with scope.environment(main.id):
            approval = lab.app.container.get(Questions).open()[0]

        user = UserActor(lab.simulator, random.Random(2), 3600, 1)
        user.away_for(1)
        assert user.is_away()
        assert user.maybe_message() is None
        assert user.approve(approval.id) is None
        lab.simulator.advance(60)
        assert not user.is_away()
        assert user.approve(approval.id).answer[0] == 0
        assert user.maybe_message().answer[0] == 0


def test_a_planted_domain_route_fault_is_found_shrunk_and_replayed_from_its_file(tmp_path, monkeypatch):
    scenario = LabScenario.read(Path(__file__).parent / "lab/scenarios/software_company/production_incident.toml")
    business = BusinessType.read(Path(__file__).parent / "lab/business_types/software_company.toml")
    seed = 1035

    def play(actions, folder, out_of_route_rate, trace_seed=seed):
        request = replace(
            lab_journal_request(folder / "root", folder / "home", PlanMode.ORGANIZATION),
            seed=trace_seed,
        )
        with LabJournal(request, scenario, business, monkeypatch) as lab:
            domain = lab.app.container.get(Organization).contracts().domain("engineering")
            profile = lab_behaviour_profile("domain", "sonnet", 1.0, 1.0, 0.0, out_of_route_rate, 0.0)
            actor = DomainAgentActor(lab.simulator, domain, "main", profile, trace_seed)
            assert not actor.session_start().is_refused()
            trace = []
            for second, action in enumerate(actions, 1):
                if action != "route":
                    raise ValueError(f"unknown simulated Domain action: {action}")
                role = actor.route("a product change")
                trace.append(TraceEntry(second * 30, f"domain:{domain.id}", f"route:{role}", False, (), (), 200))
            return domain.routing[0].role, trace

    primary_role, planted = play(["route", "route"], tmp_path / "planted", 1.0)
    invariant = PrimaryRoleRoute("engineering", primary_role)
    assert invariant.violated(planted)
    _, clean = play(["route"], tmp_path / "clean", 0.0)
    assert not invariant.violated(clean)

    replay_number = 0

    def replay(actions, trace_seed=seed):
        nonlocal replay_number
        replay_number += 1
        return play(actions, tmp_path / f"shrink-{replay_number}", 1.0, trace_seed)[1]

    shrunk = Shrinker(replay, invariant).shrunk(["route", "route"])
    assert shrunk == ["route"]
    shrunk_trace = replay(shrunk, seed)
    assert invariant.violated(shrunk_trace)

    path = TraceFile(tmp_path / "traces").written(
        scenario.id, seed, invariant.violated(planted), shrunk_trace, shrunk,
    )
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["scenario"] == scenario.id and stored["seed"] == seed and stored["actions"] == ["route"]
    replayed = replay(stored["actions"], stored["seed"])
    assert invariant.violated(replayed)
    assert stored["trace"] == json.loads(json.dumps([asdict(entry) for entry in replayed]))


def test_a_fully_observed_empty_count_is_zero():
    count = measurement(0, observed=4, expected=4)

    assert count.value == 0
    assert count.status == "observed"


def test_missing_telemetry_is_not_an_observed_zero():
    count = measurement(None, "missing", observed=0, expected=None, reason="observer unavailable", sources=())

    assert count.value is None
    assert count.status == "missing"


def test_incomplete_known_coverage_cannot_be_called_observed():
    with pytest.raises(ValueError, match="complete expected coverage"):
        measurement(0, "observed", observed=2, expected=3)


def test_a_censored_duration_keeps_its_lower_bound():
    duration = measurement(12.5, "censored", observed=1, expected=2, reason="the second wait remained open at cutoff")

    assert duration.value == 12.5
    assert duration.status == "censored"


def test_a_zero_denominator_is_not_applicable():
    ratio = measurement(None, "not_applicable", observed=3, expected=3, reason="there were no eligible session hours")

    assert ratio.value is None
    assert ratio.status == "not_applicable"


def test_run_and_network_readings_name_every_metric_and_leave_unread_sources_missing():
    run = RunReading.missing("source adapters have not captured this metric", "1")
    network = NetworkReading.missing("canonical transport history is not available", "1")

    assert tuple(value.name for value in run.measurements) == RUN_METRICS
    assert tuple(value.name for value in network.measurements) == NETWORK_METRICS
    assert set(RUN_METRICS) == RUN_METRIC_CONTRACT
    assert set(NETWORK_METRICS) == NETWORK_METRIC_CONTRACT
    assert all(value.measurement.status == "missing" for value in run.measurements)
    assert all(value.measurement.value is None for value in network.measurements)
    assert tuple(check.name for check in run.setup_diagnostics) == SETUP_CHECKS
    assert all(check.status == "unknown" for check in run.setup_diagnostics)


def test_a_run_reading_rejects_a_missing_metric():
    reading = RunReading.missing("source not read", "1")

    with pytest.raises(ValueError, match="all run metrics"):
        replace(reading, measurements=reading.measurements[:-1])


def test_hub_audit_findings_are_a_partial_lower_bound_and_no_findings_do_not_prove_zero():
    finding = HubTrafficFinding("q-1", "domain-a", "role-b", "session-1", "native identity")
    reading = NetworkReading.from_findings((finding, finding), "1")

    assert reading.measurement("route_violations") == measurement(
        1,
        "partial",
        observed=1,
        expected=None,
        reason="recognized HubTrafficAudit findings; complete delivery-linked coverage is unavailable",
        sources=("hub-traffic-audit:q-1",),
    )
    empty = NetworkReading.from_findings((), "1")
    assert empty.measurement("route_violations").status == "missing"
    assert empty.measurement("route_violations").value is None


def test_network_percentiles_use_nearest_rank_and_empty_samples_stay_unknown():
    assert nearest_rank((10, 20, 30, 40, 50, 60, 70, 80, 90, 100), 0.85) == 90
    assert nearest_rank((), 0.85) is None


def test_network_percentiles_reject_a_value_outside_the_nearest_rank_range():
    with pytest.raises(ValueError, match="between 0 and 1"):
        nearest_rank((1, 2), 0)


def test_a_run_record_serializes_identity_readings_and_utc_evidence_as_one_json_line():
    run = RunReading.missing("no run source evidence", "1")
    network = NetworkReading.missing("no network source evidence", "1")
    record = RunRecord(
        run_id="run-1",
        attempt=1,
        scenario="claim review",
        scenario_version="2",
        business_type="insurance",
        design_digest="design-sha256",
        settings_digest="settings-sha256",
        seed=43,
        journal_commit="journal-sha",
        organization_commit="organization-sha",
        provider="simulated",
        model="synthetic-tier",
        simulated=True,
        metric_schema_version="1",
        observation_started_at=datetime(2026, 10, 30, 9, 0, tzinfo=timezone.utc),
        observation_ended_at=datetime(2026, 10, 30, 9, 5, tzinfo=timezone.utc),
        terminal_reason="completed",
        setup_minutes=measurement(1.5),
        reading=run,
        network=network,
    )

    first = record.json_line()
    decoded = json.loads(first)

    assert first == record.json_line()
    assert decoded["observation_started_at"] == "2026-10-30T09:00:00Z"
    assert decoded["simulated"] is True
    assert {item["name"] for item in decoded["reading"]["measurements"]} == set(RUN_METRICS)
    assert {item["name"] for item in decoded["network"]["measurements"]} == set(NETWORK_METRICS)
    assert decoded["reading"]["measurements"][0]["measurement"]["status"] == "missing"


def test_a_failed_setup_has_no_work_window():
    reading = RunReading.missing("setup did not finish", "1").with_measurement(
        "minutes_to_done",
        measurement(None, "not_applicable", observed=0, expected=None, reason="setup failed before scenario release", sources=()),
    )
    record = RunRecord(
        "run-2", 1, "claim review", "2", "insurance", "design-sha256", "settings-sha256", 44,
        "journal-sha", "organization-sha", "simulated", "synthetic-tier", True, "1",
        datetime(2026, 10, 30, 9, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 30, 9, 1, tzinfo=timezone.utc), "setup_failed",
        measurement(1), reading, NetworkReading.missing("setup failed before network read", "1"),
    )

    assert record.terminal_reason == "setup_failed"


def lab_batch(batch_id="d" * 32, seeds=(11,)):
    return Batch(
        batch_id,
        (ScenarioPin("claim review", "insurance", "1", "a" * 64, 10),),
        (Design.from_mapping("baseline", {"organization.hub_route_strategy": "strict"}),),
        tuple(seeds),
        "b" * 40,
        "c" * 40,
        "organization-1",
        "d" * 64,
        ("synthetic-tier",),
        SimulationCaps(max(len(seeds), 1), 2, 64 * 1024 * 1024, 180, 30, 60),
        "1",
        "1",
        "e" * 64,
    )


def lab_run_record(request):
    if any(name.endswith(("_API_KEY", "_TOKEN")) for name in os.environ):
        raise AssertionError("provider credentials reached the simulated run")
    if os.environ.get("HOME") != str(request.home) or Path.cwd() != request.root:
        raise AssertionError("the simulated run did not receive its private home and root")
    now = datetime.now(timezone.utc)
    reason = "test adapter has no metric source history"
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
        now,
        now,
        "completed",
        Measurement(None, "missing", reason, 0, None, (), request.metric_schema_version),
        RunReading.missing(reason, request.metric_schema_version),
        NetworkReading.missing(reason, request.metric_schema_version),
    )


def regression_run_record(request):
    now = datetime.now(timezone.utc)
    reason = "deterministic regression fixture"
    reading = RunReading.missing(reason, request.metric_schema_version).with_measurement(
        "goal_reached",
        measurement(request.source_commit == "f" * 40),
    )
    return RunRecord(
        request.run_id, request.attempt, request.scenario.name, request.scenario.version,
        request.scenario.business_type, request.design.digest, request.design.settings_digest,
        request.seed, request.source_commit, request.organization_commit, request.provider,
        request.model, True, request.metric_schema_version, now, now, "completed",
        measurement(1.0), reading, NetworkReading.missing(reason, request.metric_schema_version),
    )


def test_batch_runner_writes_five_hundred_records_once_and_names_missing_metrics(tmp_path, monkeypatch):
    batch = lab_batch(seeds=tuple(range(500)))
    lab_home = tmp_path / "journal-lab"
    runner = BatchRunner(lab_run_record, lab_home, Path(__file__).resolve().parents[1], workers=2)
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")

    output = runner.run(batch)
    records = output.read_text().splitlines()
    summary = json.loads(output.with_name("summary.json").read_text())
    manifest = json.loads(output.with_name("manifest.json").read_text())
    first = output.read_text()

    assert len(records) == 500
    assert len({json.loads(line)["run_id"] for line in records}) == 500
    assert all(json.loads(line)["provider"] == "VoidProvider" for line in records)
    assert all(json.loads(line)["simulated"] is True for line in records)
    assert summary["run_count"] == 500
    assert summary["metrics"]["reading"]["goal_reached"]["missing"] == 500
    assert summary["metrics"]["network"]["route_violations"]["missing"] == 500
    assert len(manifest["root_map"]) == 500
    assert manifest["scenarios"][0]["version"] == "1"
    assert manifest["scenarios"][0]["checksum"] == "a" * 64
    assert manifest["designs"][0]["settings"] == {"organization.hub_route_strategy": "strict"}
    assert manifest["source_commit"] == "b" * 40
    assert manifest["organization"]["checksum"] == "d" * 64
    assert manifest["providers"] == ["VoidProvider"]
    assert manifest["approval_scope"] == []
    assert len(manifest["content_digest"]) == 64
    assert stat.S_IMODE(lab_home.stat().st_mode) == 0o700
    assert all(stat.S_IMODE((lab_home / name).stat().st_mode) == 0o700 for name in ("batches", "roots", "homes"))
    assert stat.S_IMODE(next((lab_home / "roots" / batch.batch_id).iterdir()).stat().st_mode) == 0o700
    assert stat.S_IMODE(next((lab_home / "homes" / batch.batch_id).iterdir()).stat().st_mode) == 0o700
    assert stat.S_IMODE(next((lab_home / "batches" / batch.batch_id / "runs").glob("*/result.json")).stat().st_mode) == 0o600
    assert lab_home not in Path(__file__).resolve().parents

    runner.run(batch)

    assert output.read_text() == first


def test_a_changed_recipe_cannot_reuse_the_same_batch_id(tmp_path):
    batch = lab_batch()
    runner = BatchRunner(lab_run_record, tmp_path / "lab", Path(__file__).resolve().parents[1], workers=1)
    runner.run(batch)
    changed = replace(batch, seeds=(12,))

    with pytest.raises(ValueError, match="manifest is immutable"):
        runner.run(changed)


def test_lab_home_inside_a_checkout_is_refused_before_writing(tmp_path):
    checkout = Path(__file__).resolve().parents[1]
    unsafe = checkout / ".lab-test-output"
    runner = BatchRunner(lab_run_record, unsafe, checkout, workers=1)

    with pytest.raises(ValueError, match="outside source checkouts"):
        runner.run(lab_batch())
    assert not unsafe.exists()


def test_the_lab_cli_lists_future_verbs_but_refuses_unimplemented_real_actions(capsys):
    from tests.lab.__main__ import VERBS, main

    assert VERBS == ("organizations", "simulate", "regression", "compare", "plan-real", "approve", "run-real", "calibrate", "report")
    assert main(["run-real"]) == 2
    assert "no real run or other action was started" in capsys.readouterr().err


def test_simulate_command_reads_a_pinned_recipe_and_uses_its_runner(tmp_path, capsys):
    from tests.lab.__main__ import main

    batch = lab_batch()
    recipe = batch.manifest(tmp_path / "lab-home")
    for key in ("content_digest", "root_map", "runs"):
        recipe.pop(key)
    path = tmp_path / "recipe.json"
    path.write_text(json.dumps(recipe))

    result = main(["simulate", "--recipe", str(path), "--runner", "tests.lab_run:lab_run_record", "--lab-home", str(tmp_path / "lab-home"), "--workers", "1"])

    assert result == 0
    assert Path(capsys.readouterr().out.strip()).is_file()


def test_scheduled_regression_runs_against_its_baseline_and_writes_an_exploratory_drift_report(tmp_path, capsys):
    from tests.lab.__main__ import main

    home = tmp_path / "lab-home"
    baseline = lab_batch(batch_id="a" * 32)
    BatchRunner(regression_run_record, home, Path(__file__).resolve().parents[1], workers=1).run(baseline)
    current = replace(
        baseline, batch_id="b" * 32, source_commit="f" * 40, organization_commit="e" * 40,
        organization_version="organization-2", organization_checksum="f" * 64,
    )
    recipe = current.manifest(home)
    for key in ("batch_id", "content_digest", "root_map", "runs"):
        recipe.pop(key)
    recipe_path = tmp_path / "regression-recipe.json"
    recipe_path.write_text(json.dumps(recipe))

    result = main([
        "regression", "--recipe", str(recipe_path), "--baseline-batch", baseline.batch_id,
        "--runner", "tests.lab_run:regression_run_record", "--lab-home", str(home), "--workers", "1",
    ])

    output = capsys.readouterr()
    assert result == 0
    report_path = Path(output.out.strip())
    report = report_path.read_text()
    assert report_path.name == "report.md"
    assert report_path.parent.name != baseline.batch_id
    assert stat.S_IMODE(report_path.stat().st_mode) == 0o600
    assert f'"manifest_digest": "{json.loads((home / "batches" / baseline.batch_id / "manifest.json").read_text())["content_digest"]}"' in report
    assert f'"source_commit": "{current.source_commit}"' in report
    assert f'"organization_commit": "{current.organization_commit}"' in report
    assert "drift_observed" in report
    assert "inconclusive" in report
    assert "exploratory" in report
    assert "no automatic setting change or rollback" in report
    assert '"cost_dollars"' in report
    assert '"setup_failures"' in report


def test_scheduled_regression_refuses_changed_seed_pins_before_running(tmp_path, capsys):
    from tests.lab.__main__ import main

    home = tmp_path / "lab-home"
    baseline = lab_batch(batch_id="a" * 32)
    BatchRunner(regression_run_record, home, Path(__file__).resolve().parents[1], workers=1).run(baseline)
    current = replace(baseline, batch_id="b" * 32, source_commit="f" * 40, seeds=(12,))
    recipe = current.manifest(home)
    for key in ("batch_id", "content_digest", "root_map", "runs"):
        recipe.pop(key)
    recipe_path = tmp_path / "changed-regression-recipe.json"
    recipe_path.write_text(json.dumps(recipe))

    result = main([
        "regression", "--recipe", str(recipe_path), "--baseline-batch", baseline.batch_id,
        "--runner", "tests.lab_run:regression_run_record", "--lab-home", str(home), "--workers", "1",
    ])

    assert result == 2
    assert "seeds" in capsys.readouterr().err
    assert {path.name for path in (home / "batches").iterdir()} == {baseline.batch_id}


def test_a_batch_deadline_before_start_records_aborted_work_and_no_setup_as_not_applicable(tmp_path, monkeypatch):
    from types import SimpleNamespace

    batch = lab_batch()
    caps = replace(batch.caps, batch_deadline_seconds=0.000001)
    batch = replace(batch, caps=caps)
    ticks = iter((0.0, 1.0))
    monkeypatch.setattr("tests.lab.batch_runner.time", SimpleNamespace(monotonic=lambda: next(ticks)))
    output = BatchRunner(lab_run_record, tmp_path / "lab-home", Path(__file__).resolve().parents[1], workers=1).run(batch)
    record = json.loads(output.read_text())
    minutes = next(item["measurement"] for item in record["reading"]["measurements"] if item["name"] == "minutes_to_done")

    assert record["terminal_reason"] == "aborted"
    assert record["setup_minutes"]["status"] == "not_applicable"
    assert minutes["status"] == "not_applicable"


def comparison_plan(metrics=None):
    from tests.lab.comparison_plan import ComparisonPlan
    from tests.lab.metric_rule import MetricRule

    selected = metrics or (MetricRule("goal_reached", "binary", "higher", "primary", 10.0),)
    return ComparisonPlan("decision-1", selected, 0.05, 8, 999, 100, 193)


def comparison_batch(plan, seeds=tuple(range(6))):
    return Batch(
        "f" * 32,
        (ScenarioPin("claim review", "insurance", "1", "a" * 64, 10),),
        (
            Design.from_mapping("A", {"hub_route_strategy": "legacy"}),
            Design.from_mapping("B", {"hub_route_strategy": "strict"}),
        ),
        tuple(seeds),
        "b" * 40,
        "c" * 40,
        "organization-1",
        "d" * 64,
        ("synthetic-tier",),
        SimulationCaps(100, 2, 64 * 1024 * 1024, 180, 30, 60),
        "1",
        plan.decision_rule_version,
        plan.digest,
    )


def comparison_records(batch, lab_home, values_by_run):
    records = []
    now = datetime(2026, 10, 30, 9, 0, tzinfo=timezone.utc)
    reason = "paired comparison test evidence"
    for request in batch.requests(lab_home):
        run_values = values_by_run(request.design.name, request.seed)
        run = RunReading.missing(reason, request.metric_schema_version)
        network = NetworkReading.missing(reason, request.metric_schema_version)
        for name, value in run_values.items():
            if name in RUN_METRICS:
                run = run.with_measurement(name, measurement(value))
            else:
                network = network.with_measurement(name, measurement(value))
        records.append(RunRecord(
            request.run_id, request.attempt, request.scenario.name, request.scenario.version,
            request.scenario.business_type, request.design.digest, request.design.settings_digest,
            request.seed, request.source_commit, request.organization_commit, request.provider,
            request.model, True, request.metric_schema_version, now, now, "completed",
            measurement(1.0), run, network,
        ))
    return tuple(records)


def test_exact_mcnemar_reports_every_cell_and_no_discordance_is_not_evidence():
    from tests.lab.paired_tests import PairedTests

    result = PairedTests.mcnemar((True, False, True, False, False), (True, True, False, False, True))
    assert result["cells"] == {
        "a_success_b_success": 1,
        "a_success_b_failure": 1,
        "a_failure_b_success": 2,
        "a_failure_b_failure": 1,
    }
    assert result["effect_percentage_points"] == 20.0
    assert result["p_value"] == pytest.approx(0.5)
    no_discordance = PairedTests.mcnemar((True, False), (True, False))
    assert no_discordance["status"] == "no_discordance"
    assert no_discordance["p_value"] == 1.0


def test_continuous_sign_flip_uses_paired_units_and_reports_degenerate_median_interval():
    from tests.lab.paired_tests import PairedTests

    result = PairedTests.continuous(
        (2, 2, 2, 2, 2, 2), random_seed=7, permutation_draws=99,
        exact_enumeration_cutoff=8, bootstrap_draws=100,
        independent_unit="seed", null_value=0, alternative="greater",
    )
    assert result["effect_median"] == 2
    assert result["test_statistic_mean"] == 2
    assert result["p_value"] == 1 / 64
    assert result["permutation"]["enumeration"] == "exact"
    assert result["interval"]["status"] == "degenerate"
    assert result["interval"]["lower"] == result["interval"]["upper"] == 2


def test_sampled_sign_flips_use_the_declared_seed_and_plus_one_p_value():
    from tests.lab.paired_tests import PairedTests

    result = PairedTests.continuous(
        (1, 2, 3, 4, 5, 6), random_seed=991, permutation_draws=50,
        exact_enumeration_cutoff=2, bootstrap_draws=100,
        independent_unit="seed",
    )
    assert result["permutation"]["enumeration"] == "sampled"
    assert result["permutation"]["seed"] == 991
    assert result["permutation"]["draws"] == 50
    assert result["permutation"]["p_value_rule"] == "(extreme + 1) / (draws + 1)"
    assert result["p_value"] > 0


def test_missing_paired_readings_remain_unpassed_instead_of_being_dropped():
    from tests.lab.paired_tests import PairedTests

    result = PairedTests.continuous(
        (1, 2, None), random_seed=7, permutation_draws=99,
        exact_enumeration_cutoff=8, bootstrap_draws=100,
        independent_unit="seed",
    )
    assert result["status"] == "incomplete"
    assert result["missing_pair_count"] == 1
    assert result["p_value"] is None


def test_holm_correction_keeps_missing_tests_in_the_frozen_family():
    from tests.lab.paired_tests import PairedTests

    corrected = PairedTests.holm((("primary", 0.02), ("guard", None), ("subgroup", 0.03)), 0.05)
    assert corrected["family_size"] == 3
    assert corrected["members"]["primary"]["adjusted_p_value"] == 0.06
    assert corrected["members"]["subgroup"]["adjusted_p_value"] == 0.06
    assert corrected["members"]["guard"]["adjusted_p_value"] is None
    assert not corrected["members"]["guard"]["passed"]


def test_ratio_rules_require_a_formula_and_zero_or_unknown_denominator_behavior():
    from tests.lab.metric_rule import MetricRule

    with pytest.raises(ValueError, match="ratio metrics need a formula"):
        MetricRule("critical_path_ratio", "continuous", "lower", "primary", 0.1)
    rule = MetricRule(
        "critical_path_ratio", "continuous", "lower", "primary", 0.1,
        ratio_formula="minutes_to_done / pinned critical path minutes",
        zero_unknown_denominator_rule="zero baseline is not_applicable; unknown baseline is missing",
    )
    assert rule.ratio_formula == "minutes_to_done / pinned critical path minutes"
    assert rule.zero_unknown_denominator_rule.startswith("zero baseline")


def test_comparison_pairs_pinned_a_b_runs_and_only_recommends_after_the_full_family_passes(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    comparison = Comparison(
        batch,
        home,
        comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"}),
        plan,
    )

    result = comparison.analyze()

    assert result["manifest_digest"] == batch.manifest(home)["content_digest"]
    assert result["decision_rule_digest"] == plan.digest
    assert result["recommendation"] == "keep_eligible"
    assert result["action_taken"] is False
    assert result["confirmatory_family"]["family_size"] == 1
    row = result["results"][0]
    assert row["analysis"]["cells"]["a_failure_b_success"] == 6
    assert row["analysis"]["p_value"] == pytest.approx(1 / 64)
    assert row["holm"]["passed"]


def test_twenty_identical_setting_batches_keep_false_findings_near_the_declared_alpha_rate(tmp_path):
    from random import Random
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    false_positives = 0
    for index in range(20):
        first_seed = index * 40
        batch = comparison_batch(plan, seeds=tuple(range(first_seed, first_seed + 40)))
        settings = {"hub_route_strategy": "strict"}
        batch = replace(
            batch,
            batch_id=f"{index:032x}",
            designs=(Design.from_mapping("A", settings), Design.from_mapping("B", settings)),
            caps=replace(batch.caps, max_runs=80),
        )
        home = tmp_path / f"aa-{index}"
        shared_world = {seed: Random(173_000_000 + seed).random() < 0.9 for seed in batch.seeds}
        observations = {
            **{("A", seed): shared_world[seed] and Random(183_000_000 + seed).random() < 0.5 for seed in batch.seeds},
            **{("B", seed): shared_world[seed] and Random(193_000_000 + seed).random() < 0.5 for seed in batch.seeds},
        }

        def values(design, seed):
            return {"goal_reached": observations[(design, seed)]}

        result = Comparison(batch, home, comparison_records(batch, home, values), plan).analyze()

        assert batch.designs[0].settings == batch.designs[1].settings
        if result["results"][0]["analysis"]["p_value"] <= plan.alpha:
            false_positives += 1

    assert false_positives <= 3


def test_planted_slowdown_is_dropped_at_the_pilot_estimates_fixed_seed_count(tmp_path):
    from tests.lab.comparison import Comparison
    from tests.lab.comparison_plan import ComparisonPlan
    from tests.lab.metric_rule import MetricRule
    from tests.lab.seed_estimate import SeedEstimate

    plan = ComparisonPlan(
        "slowdown-rule-1", (MetricRule("minutes_to_done", "continuous", "lower", "primary", 1.0),),
        0.05, 8, 999, 100, 173,
    )
    home = tmp_path / "journal-lab"
    pilot = {
        "pilot_manifest_digest": "a" * 64,
        "pilot_kind": "exploratory",
        "metric": "minutes_to_done",
        "expected_metric": "minutes_to_done",
        "primary_kind": "continuous",
        "pilot_units_by_scenario": (("claim review", (-1.0, 0.0, 1.0, 2.0, 3.0, 1.0, 2.0, 4.0)),),
        "pilot_missing_units_by_scenario": (("claim review", 0),),
        "scenario_names": ("claim review",),
        "models": ("synthetic-tier",),
        "pilot_seeds": tuple(range(1, 9)),
        "caps": SimulationCaps(100, 2, 64 * 1024 * 1024, 180, 30, 60),
        "estimated_storage_bytes_per_run": 64 * 1024,
        "estimated_run_seconds": 1.0,
        "simulated_minutes_by_scenario": (("claim review", 10),),
        "assumed_effect": 8.0,
        "practical_minimum": 1.0,
        "precision_target": 10.0,
        "required_power": 0.8,
        "alpha": plan.alpha,
        "confirmatory_family_size": 1,
        "bootstrap_draws": 100,
        "random_seed": 173,
    }

    def estimate_for(digest):
        return SeedEstimate.from_pilot(**{
            **pilot,
            "confirmatory_manifest_digest": digest,
        })

    proposed = estimate_for("b" * 64)
    planned_seeds = proposed.seeds_by_scenario[0][1]
    batch = comparison_batch(plan, seeds=planned_seeds)
    estimate = estimate_for(batch.manifest(home)["content_digest"])
    comparison = Comparison(
        batch, home,
        comparison_records(batch, home, lambda design, seed: {"minutes_to_done": 10 if design == "A" else 14}),
        plan,
    )

    result = comparison.analyze()
    primary = result["results"][0]

    assert estimate.status == "estimated"
    assert estimate.required_seed_count == len(batch.seeds)
    assert estimate.seeds_by_scenario == (("claim review", batch.seeds),)
    assert primary["analysis"]["effect_median"] == -4.0
    assert primary["analysis"]["p_value"] == 1.0
    assert result["recommendation"] == "drop"
    assert result["action_taken"] is False


def test_comparison_rejects_run_evidence_that_does_not_match_its_frozen_design_pin(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"})

    with pytest.raises(ValueError, match="pinned batch request"):
        Comparison(batch, home, (replace(records[0], seed=999), *records[1:]), plan)


def test_comparison_rejects_a_decision_rule_changed_after_the_batch_was_pinned(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"})

    with pytest.raises(ValueError, match="frozen batch manifest"):
        Comparison(batch, home, records, replace(plan, alpha=0.01))


def test_missing_batch_pair_makes_the_comparison_inconclusive_and_stays_in_holm_family(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"})
    incomplete = Comparison(batch, home, records[:-1], plan).analyze()

    assert incomplete["recommendation"] == "inconclusive"
    assert incomplete["confirmatory_family"]["family_size"] == 1
    assert incomplete["confirmatory_family"]["members"][incomplete["results"][0]["family_member"]]["p_value"] is None
    assert incomplete["results"][0]["missing_pair_reasons"][-1]["reason"] == "run result is missing from the frozen batch"


@pytest.mark.parametrize(
    "name,kind,direction,minimum,ratio_formula,denominator_rule",
    (
        ("handoff_latency_median_minutes", "continuous", "lower", 0.1, None, None),
        ("queue_fairness_jain", "continuous", "higher", 0.01, "Jain index of service starts per eligible backlogged minute", "no eligible demand or all-zero starts is not_applicable; unknown exposure is missing"),
        ("expectations_met_share", "continuous", "higher", 0.01, "met expectations / required expectations", "zero required expectations is not_applicable; unknown requirements are missing"),
        ("goal_reached", "binary", "higher", 1.0, None, None),
    ),
)
def test_each_first_trial_stays_inconclusive_without_its_primary_reading(
    tmp_path, name, kind, direction, minimum, ratio_formula, denominator_rule,
):
    from tests.lab.comparison import Comparison
    from tests.lab.metric_rule import MetricRule

    primary = MetricRule(
        name, kind, direction, "primary", minimum,
        ratio_formula=ratio_formula, zero_unknown_denominator_rule=denominator_rule,
    )
    plan = comparison_plan((primary,))
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda _design, _seed: {})

    result = Comparison(batch, home, records, plan).analyze()

    assert result["recommendation"] == "inconclusive"
    assert result["results"][0]["metric"] == name
    assert result["results"][0]["analysis"]["missing_pair_count"] > 0
    assert result["confirmatory_family"]["members"][result["results"][0]["family_member"]]["p_value"] is None


def test_known_unmet_goal_at_a_cap_remains_a_failure_with_its_terminal_reason(tmp_path):
    from tests.lab.comparison import Comparison

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    records = comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"})
    candidate = next(record for record in records if record.design_digest == batch.designs[1].digest)
    capped = replace(
        candidate,
        terminal_reason="capped",
        reading=candidate.reading.with_measurement("goal_reached", measurement(False)),
    )
    evidence = tuple(capped if record.run_id == candidate.run_id else record for record in records)

    result = Comparison(batch, home, evidence, plan).analyze()
    row = result["results"][0]

    assert row["terminal_reasons"]["B"]["capped"] == 1
    assert row["analysis"]["cells"]["a_failure_b_failure"] == 1
    assert row["analysis"]["p_value"] == 1 / 32


def test_continuous_guard_tests_the_preregistered_harm_boundary_before_holm(tmp_path):
    from tests.lab.comparison import Comparison
    from tests.lab.metric_rule import MetricRule

    plan = comparison_plan((
        MetricRule("goal_reached", "binary", "higher", "primary", 10.0),
        MetricRule("cost_units", "continuous", "lower", "guard", tolerated_harm=2.0),
    ))
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    comparison = Comparison(batch, home, comparison_records(
        batch, home,
        lambda design, seed: {"goal_reached": design == "B", "cost_units": 10.0 if design == "A" else 11.5},
    ), plan)

    guard = next(row for row in comparison.analyze()["results"] if row["metric"] == "cost_units")
    assert guard["analysis"]["null_value"] == -2.0
    assert guard["analysis"]["p_value"] == 1 / 64
    assert guard["holm"]["passed"]


def test_seed_estimate_uses_pinned_exploratory_effect_spread_and_records_exact_capped_seeds():
    from tests.lab.seed_estimate import SeedEstimate

    estimate = SeedEstimate.from_pilot(
        pilot_manifest_digest="a" * 64,
        confirmatory_manifest_digest="b" * 64,
        pilot_kind="exploratory",
        metric="minutes_to_done",
        expected_metric="minutes_to_done",
        primary_kind="continuous",
        pilot_units_by_scenario=(("claims", (-1.0, 0.0, 1.0, 2.0, 3.0, 1.0, 2.0, 4.0)),),
        pilot_missing_units_by_scenario=(("claims", 0),),
        scenario_names=("claims",),
        models=("calibrated",),
        pilot_seeds=tuple(range(1, 9)),
        caps=SimulationCaps(1000, 2, 64 * 1024 * 1024, 180, 30, 60),
        estimated_storage_bytes_per_run=64 * 1024,
        estimated_run_seconds=1.0,
        simulated_minutes_by_scenario=(("claims", 10),),
        assumed_effect=2.0,
        practical_minimum=0.5,
        precision_target=0.5,
        required_power=0.8,
        alpha=0.05,
        confirmatory_family_size=1,
        bootstrap_draws=100,
        random_seed=13,
    )

    assert estimate.status == "estimated"
    assert estimate.pilot_manifest_digest == "a" * 64
    assert estimate.required_seed_count >= 2
    assert estimate.primary_power is not None
    assert estimate.whole_keep_rule_probability is not None
    assert estimate.seed_count_uncertainty is not None
    assert estimate.seeds_by_scenario == (("claims", tuple(range(9, 9 + estimate.required_seed_count))),)


def test_seed_estimate_returns_not_enough_history_instead_of_inventing_powered_seeds():
    from tests.lab.seed_estimate import SeedEstimate

    estimate = SeedEstimate.from_pilot(
        pilot_manifest_digest=None,
        confirmatory_manifest_digest="b" * 64,
        pilot_kind="exploratory",
        metric="minutes_to_done",
        expected_metric="minutes_to_done",
        primary_kind="continuous",
        pilot_units_by_scenario=None,
        pilot_missing_units_by_scenario=(("claims", 0),),
        scenario_names=("claims",),
        models=("calibrated",),
        pilot_seeds=(),
        caps=SimulationCaps(1000, 2, 64 * 1024 * 1024, 180, 30, 60),
        estimated_storage_bytes_per_run=1024 * 1024,
        estimated_run_seconds=1.0,
        simulated_minutes_by_scenario=(("claims", 10),),
        assumed_effect=2.0,
        practical_minimum=0.5,
        precision_target=0.5,
        required_power=0.8,
        alpha=0.05,
        confirmatory_family_size=1,
    )

    assert estimate.status == "not_enough_history"
    assert estimate.required_seed_count is None
    assert estimate.seeds_by_scenario == ()
    assert "separately budgeted exploratory pilot" in estimate.reason


def test_binary_seed_estimate_uses_discordance_and_declines_a_run_count_above_approved_caps():
    from tests.lab.seed_estimate import SeedEstimate

    pairs = ((False, True), (True, False), (False, False), (True, True), (False, True), (False, False), (True, True), (True, False))
    estimate = SeedEstimate.from_pilot(
        pilot_manifest_digest="a" * 64,
        confirmatory_manifest_digest="b" * 64,
        pilot_kind="exploratory",
        metric="goal_reached",
        expected_metric="goal_reached",
        primary_kind="binary",
        pilot_units_by_scenario=(("claims", pairs),),
        pilot_missing_units_by_scenario=(("claims", 0),),
        scenario_names=("claims",),
        models=("calibrated",),
        pilot_seeds=tuple(range(1, 9)),
        caps=SimulationCaps(10, 2, 1000, 180, 30, 60),
        estimated_storage_bytes_per_run=10,
        estimated_run_seconds=1.0,
        simulated_minutes_by_scenario=(("claims", 10),),
        assumed_effect=25,
        practical_minimum=5,
        precision_target=15,
        required_power=0.8,
        alpha=0.05,
        confirmatory_family_size=1,
        bootstrap_draws=100,
        random_seed=13,
    )

    assert estimate.status == "cap_insufficient"
    assert estimate.required_seed_count > estimate.cap_fitted_seed_count
    assert estimate.cap_fitted_seed_count == 5
    assert estimate.seeds_by_scenario == (("claims", tuple(range(9, 14))),)
    assert dict(estimate.cap_limits)["max_runs_seed_capacity"] == 5


def test_seed_estimate_uses_the_preregistered_continuous_guard_margin():
    from tests.lab.guard_pilot import GuardPilot
    from tests.lab.seed_estimate import SeedEstimate

    primary = (("claims", (-1.0, 0.0, 1.0, 2.0, 3.0, 1.0, 2.0, 4.0)),)
    guard_values = (("claims", (-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, -1.0, 1.0)),)
    common = {
        "pilot_manifest_digest": "a" * 64,
        "confirmatory_manifest_digest": "b" * 64,
        "pilot_kind": "exploratory",
        "metric": "minutes_to_done",
        "expected_metric": "minutes_to_done",
        "primary_kind": "continuous",
        "pilot_units_by_scenario": primary,
        "pilot_missing_units_by_scenario": (("claims", 0),),
        "scenario_names": ("claims",),
        "models": ("calibrated",),
        "pilot_seeds": tuple(range(1, 9)),
        "caps": SimulationCaps(1000, 2, 64 * 1024 * 1024, 180, 30, 60),
        "estimated_storage_bytes_per_run": 64 * 1024,
        "estimated_run_seconds": 1.0,
        "simulated_minutes_by_scenario": (("claims", 10),),
        "assumed_effect": 2.0,
        "practical_minimum": 0.5,
        "precision_target": 0.5,
        "required_power": 0.8,
        "alpha": 0.05,
        "confirmatory_family_size": 2,
        "guard_count": 1,
        "bootstrap_draws": 100,
        "random_seed": 13,
    }
    guard_seeds = (("claims", tuple(range(1, 9))),)
    narrow = SeedEstimate.from_pilot(**common, guard_pilots=(GuardPilot("cost_units", 0.1, 0.2, guard_seeds, guard_values),))
    wide = SeedEstimate.from_pilot(**common, guard_pilots=(GuardPilot("cost_units", 2.0, 0.2, guard_seeds, guard_values),))

    assert narrow.guard_margins == (("cost_units", 0.1),)
    assert narrow.required_seed_count > wide.required_seed_count
    assert narrow.whole_keep_rule_probability is not None


def test_lab_report_writes_pinned_analysis_to_the_batch_without_filing_a_journal_report(tmp_path):
    from tests.lab.comparison import Comparison
    from tests.lab.lab_report import LabReport
    from journal.support.outline import Outline

    plan = comparison_plan()
    batch = comparison_batch(plan)
    home = tmp_path / "journal-lab"
    batch_dir = home / "batches" / batch.batch_id
    batch_dir.mkdir(parents=True)
    os.chmod(batch_dir, 0o700)
    comparison = Comparison(
        batch,
        home,
        comparison_records(batch, home, lambda design, seed: {"goal_reached": design == "B"}),
        plan,
    )

    report = LabReport.write(comparison)
    draft = LabReport.draft(comparison)
    outline = Outline.build(draft["body"])

    assert report == comparison.report_path
    assert report.stat().st_mode & 0o777 == 0o600
    assert set(draft) == {"title", "abstract", "body"}
    assert draft["title"] == f"Lab comparison {batch.batch_id}"
    assert len(draft["abstract"]) <= 200
    assert tuple(section.heading for section in outline.sections) == (
        "Summary", "Trial and pins", "Recommendation", "Results", "Confirmatory family", "Evidence and methods", "Limits",
    )
    report_text = report.read_text()
    assert report_text == draft["body"]
    assert f'"manifest_digest": "{comparison.manifest_digest}"' in report_text
    assert f'"source_commit": "{batch.source_commit}"' in report_text
    assert f'"commit": "{batch.organization_commit}"' in report_text
    assert '"providers": [' in report_text
    assert '"VoidProvider"' in report_text
    assert f'"metric_schema_version": "{batch.metric_schema_version}"' in report_text
    assert "| goal_reached |" in report_text
    assert "Action taken: no" in report_text

