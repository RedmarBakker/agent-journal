from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_area_control import SupervisorGrantAreaControl


@story(SupervisorGrantAreaControl, subject=AgentRole.SUPERVISOR)
def test_an_area_and_its_verb_each_have_to_be_enabled_for_the_supervisor_to_act(story):
    result = story.supervisor_runs_command(story.agents.subject, "task create 'area switch check'")
    result.expect_command_refused()
    result.expect_command_text("capability is switched off")
    story.expect_row_count_in(story.supervisor_environment, "tasks", 1)

    result = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    result.expect_viewer_passed()
    grant = story.viewer_answer["grant"]
    capabilities = {
        **grant["capabilities"],
        "area:plans-and-tasks": {"on": True, "mode": "propose"},
        "task create": {"on": True, "mode": "act"},
    }
    result = story.user_presses("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": story.viewer_answer["grant_version"],
        "change": {"kind": "configure", "grant": {**grant, "capabilities": capabilities}},
    })
    result.expect_viewer_passed()

    result = story.supervisor_runs_command(story.agents.subject, "task create 'area mode does not override verb'")
    result.expect_command_passed()
    story.expect_row_count_in(story.supervisor_environment, "tasks", 2)

    result = story.user_opens_in(story.supervisor_owner_environment, "/journal/supervisor/control")
    result.expect_viewer_passed()
    grant = story.viewer_answer["grant"]
    capabilities = {
        **grant["capabilities"],
        "area:plans-and-tasks": {"on": False, "mode": "propose"},
        "task create": {"on": True, "mode": "act"},
    }
    result = story.user_presses("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": story.grants.first,
        "expected_grant_version": story.viewer_answer["grant_version"],
        "change": {"kind": "configure", "grant": {**grant, "capabilities": capabilities}},
    })
    result.expect_viewer_passed()

    result = story.supervisor_runs_command(story.agents.subject, "task create 'disabled area check'")
    result.expect_command_refused()
    result.expect_command_text("capability is switched off")
    story.expect_row_count_in(story.supervisor_environment, "tasks", 2)
    story.expect_stack(story.agents.subject)
