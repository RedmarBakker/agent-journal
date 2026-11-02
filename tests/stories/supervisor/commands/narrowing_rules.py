from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_cli_role import SupervisorGrantCliProposalOnly, SupervisorGrantCliRole


def change_rule(story, version: int, action: str, rule: dict):
    return story.user_presses("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": version,
        "change": {"kind": "rule", "action": action, "rule": rule},
    })


def widening_rule_is_refused(story, version: int, rule: dict) -> None:
    refused = change_rule(story, version, "add", rule)
    refused.expect_viewer_refused("narrowing")


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_an_owner_can_require_a_supervisor_verb_to_be_proposed_and_remove_that_rule(story):
    rule = {"command": "task create", "effect": "propose"}
    added = change_rule(story, 2, "add", rule)
    added.expect_viewer_passed()
    added.expect_viewer_part(("grant_version",), 3)
    added.expect_viewer_part(("narrowing_rules", 0, "effect"), "propose")

    refused = story.supervisor_runs_command(story.agents.subject, "task create 'proposed follow-up'")
    refused.expect_command_refused()
    refused.expect_command_text("the owner requires this verb to be proposed")
    story.expect_row_count_in(story.supervisor_environment, "tasks", 1)

    removed = change_rule(story, 3, "remove", rule)
    removed.expect_viewer_passed()
    removed.expect_viewer_part(("narrowing_rules",), [])
    applied = story.supervisor_runs_command(story.agents.subject, "task create 'allowed follow-up'")
    applied.expect_command_passed()
    story.expect_row_count_in(story.supervisor_environment, "tasks", 2)
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_an_owner_can_refuse_a_supervisor_verb_on_a_named_row(story):
    rule = {"command": "plan priorities", "effect": "never", "row_id": story.plans.first}
    added = change_rule(story, 2, "add", rule)
    added.expect_viewer_passed()

    refused = story.supervisor_runs_command(
        story.agents.subject,
        f"plan priorities 'change the order' --plan {story.plans.first}",
    )
    refused.expect_command_refused()
    refused.expect_command_text("the owner refuses this verb on the named row")
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliProposalOnly, subject=AgentRole.SUPERVISOR)
def test_an_owner_cannot_save_rules_that_widen_a_grant(story):
    baseline = story.supervisor_grant_mutation_baseline()
    version = 3
    plan_id = story.plans.first + 1
    limit = story.supervisor_replacement["limits"]["max_turns_per_day"] + 1
    cap = story.supervisor_replacement["limits"]["max_cost_microusd_per_day"] + 1
    expiry = story.supervisor_replacement["valid_until_ms"] + 1
    for rule in (
        {"kind": "capability", "command": "task create", "on": True},
        {"kind": "capability", "command": "task create", "mode": "act"},
        {"kind": "limit", "name": "max_turns_per_day", "value": limit},
        {"kind": "limit", "name": "max_cost_microusd_per_day", "value": cap},
        {"kind": "plans", "add": plan_id},
        {"kind": "valid_until", "value": expiry},
    ):
        widening_rule_is_refused(story, version, rule)
    story.expect_supervisor_grant_mutation_wrote_nothing(baseline)
    story.expect_stack(story.agents.subject)
