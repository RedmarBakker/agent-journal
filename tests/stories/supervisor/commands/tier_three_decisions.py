from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_capabilities import configure_grant_capabilities
from tests.stories.fixtures.main.supervisor_grant_cli_role import SupervisorGrantCliRole
from tests.stories.fixtures.main.supervisor_grant_cli_role_with_task import SupervisorGrantCliRoleWithTask


def owner_sets_decision(story, command: str, decision: str, version: int = 2):
    return story.user_presses("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": version,
        "change": {"kind": "decision", "command": command, "decision": decision},
    }, f"the owner sets {command} to {decision.replace('_', ' ')}")


def expect_control_catalogue(result, decisions: dict[str, str] | None = None) -> None:
    decisions = decisions or {}
    expected = [
        {
            "area": area,
            "noun": noun,
            "verb": verb,
            "command": f"{noun} {verb}",
            "decision": decisions.get(f"{noun} {verb}", "propose_only"),
        }
        for area, nouns in CAPABILITY_CATALOGUE.items()
        for noun, verbs in nouns.items()
        for verb, tier in verbs.items()
        if tier == "tier 3"
    ]
    never_allowed = [
        {"area": area, "noun": noun, "verb": verb, "command": f"{noun} {verb}", "decision": "never"}
        for area, nouns in CAPABILITY_CATALOGUE.items()
        for noun, verbs in nouns.items()
        for verb, tier in verbs.items()
        if tier == "never"
    ]
    result.expect_viewer_part(("tier_three_decisions",), expected)
    result.expect_viewer_part(("never_allowed",), never_allowed)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_a_tier_three_verb_is_refused_when_the_owner_sets_not_allowed(story):
    configure_grant_capabilities(story, story.fixture.supervisor_authority, story.grants.first, {
        "plan approve": {"on": False, "mode": "act"},
    })

    result = story.supervisor_runs_command(story.agents.subject, f"plan approve {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text("capability is switched off")
    story.expect_row_in(story.supervisor_owner_environment, "plans", story.plans.first, {"state": "started"})
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_a_tier_three_alias_add_defaults_to_propose_only(story):
    result = story.supervisor_runs_command(story.agents.subject, "alias add proposed 'task list'")
    result.expect_command_refused()
    result.expect_command_text("the owner requires this verb to be proposed")
    listing = story.supervisor_runs_command(story.agents.subject, "alias list")
    listing.expect_command_passed()
    listing.expect_command_text_without("proposed")
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_a_tier_three_plan_cancel_defaults_to_propose_only(story):
    result = story.supervisor_runs_command(story.agents.subject, f"plan cancel {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text("the owner requires this verb to be proposed")
    story.expect_row_in(story.supervisor_owner_environment, "plans", story.plans.first, {"state": PlanState.STARTED})
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_an_owner_can_refuse_a_tier_three_plan_cancel(story):
    saved = owner_sets_decision(story, "plan cancel", "not_allowed")
    saved.expect_viewer_passed()
    saved.expect_viewer_part(("grant_version",), 3)

    result = story.supervisor_runs_command(story.agents.subject, f"plan cancel {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text("the capability is switched off")
    story.expect_row_in(story.supervisor_owner_environment, "plans", story.plans.first, {"state": PlanState.STARTED})
    control = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    control.expect_viewer_passed()
    expect_control_catalogue(control, {"plan cancel": "not_allowed"})
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_an_owner_can_allow_a_tier_three_plan_cancel_to_act(story):
    saved = owner_sets_decision(story, "plan cancel", "may_act")
    saved.expect_viewer_passed()

    result = story.supervisor_runs_command(story.agents.subject, f"plan cancel {story.plans.first}")
    result.expect_command_passed()
    story.expect_row_in(story.supervisor_owner_environment, "plans", story.plans.first, {"state": PlanState.CANCELLED})
    control = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    control.expect_viewer_passed()
    expect_control_catalogue(control, {"plan cancel": "may_act"})
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRoleWithTask, subject=AgentRole.SUPERVISOR)
def test_an_owner_sets_tier_three_decisions_and_cannot_change_its_own_grant(story):
    refused = owner_sets_decision(story, "plan approve", "not_allowed")
    refused.expect_viewer_passed()
    refused.expect_viewer_part(("grant_version",), 3)
    result = story.supervisor_runs_command(story.agents.subject, f"plan approve {story.plans.first}")
    result.expect_command_refused()
    result.expect_command_text("the capability is switched off")
    story.expect_row_in(story.supervisor_owner_environment, "plans", story.plans.first, {"state": PlanState.STARTED})

    allowed = owner_sets_decision(story, "plan cancel-phase", "may_act", 3)
    allowed.expect_viewer_passed()
    allowed.expect_viewer_part(("grant_version",), 4)
    result = story.supervisor_runs_command(
        story.agents.subject, f'plan cancel-phase {story.plans.first} 1 --why "the owner allowed this"',
    )
    result.expect_command_passed()
    story.expect_task_in(story.supervisor_owner_environment, story.tasks.first, TaskState.CANCELLED)

    baseline = story.supervisor_grant_mutation_baseline()
    refused = owner_sets_decision(story, "grant change", "may_act", 4)
    refused.expect_viewer_refused("Never")
    story.expect_supervisor_grant_mutation_wrote_nothing(baseline)
    story.expect_supervisor_grant_state(story.grants.first, False, False)
    control = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    control.expect_viewer_passed()
    expect_control_catalogue(control, {"plan approve": "not_allowed", "plan cancel-phase": "may_act"})
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_a_tier_three_alias_add_runs_when_the_owner_sets_may_act(story):
    configure_grant_capabilities(story, story.fixture.supervisor_authority, story.grants.first, {
        "alias add": {"on": True, "mode": "act"},
    })

    result = story.supervisor_runs_command(story.agents.subject, "alias add allowed 'task list'")
    result.expect_command_passed()
    listing = story.supervisor_runs_command(story.agents.subject, "alias list")
    listing.expect_command_passed()
    listing.expect_command_text("allowed")
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_the_owner_cannot_enable_the_tier_never_grant_change(story):
    baseline = story.supervisor_grant_mutation_baseline()
    control = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    control.expect_viewer_passed()
    grant = story.viewer_answer["grant"]
    capabilities = {
        **grant["capabilities"],
        "grant change": {"on": True, "mode": "act"},
    }

    result = story.user_presses_in(story.supervisor_owner_environment, "/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": story.viewer_answer["grant_version"],
        "change": {"kind": "configure", "grant": {**grant, "capabilities": capabilities}},
    })
    result.expect_viewer_refused("mode exceeds its safety tier")
    story.expect_supervisor_grant_mutation_wrote_nothing(baseline)
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_an_owner_cannot_set_the_never_grant_change_decision(story):
    baseline = story.supervisor_grant_mutation_baseline()
    refused = owner_sets_decision(story, "grant change", "may_act")
    refused.expect_viewer_refused("Never")
    story.expect_supervisor_grant_mutation_wrote_nothing(baseline)
    story.expect_supervisor_grant_state(story.grants.first, False, False)
    control = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    control.expect_viewer_passed()
    expect_control_catalogue(control)
    story.expect_stack(story.agents.subject)
