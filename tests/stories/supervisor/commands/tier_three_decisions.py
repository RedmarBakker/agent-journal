from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_capabilities import configure_grant_capabilities
from tests.stories.fixtures.main.supervisor_grant_cli_role import SupervisorGrantCliRole


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
def test_a_tier_three_verb_defaults_to_propose_only(story):
    result = story.supervisor_runs_command(story.agents.subject, "alias add proposed 'task list'")
    result.expect_command_refused()
    result.expect_command_text("capability is set to propose")
    listing = story.supervisor_runs_command(story.agents.subject, "alias list")
    listing.expect_command_passed()
    listing.expect_command_text_without("proposed")
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_a_tier_three_verb_runs_when_the_owner_sets_may_act(story):
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
def test_control_lists_every_tier_three_command(story):
    story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    story.expect_viewer_passed()
    tier_three_count = sum(
        tier == "tier 3"
        for commands in CAPABILITY_CATALOGUE.values()
        for verbs in commands.values()
        for tier in verbs.values()
    )
    story.expect_viewer_count("needs_decision", tier_three_count)
    story.expect_stack(story.agents.subject)
