from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.supervisor_grant_cli_role import (
    SupervisorGrantCliProposalOnly,
    SupervisorGrantCliAlias,
    SupervisorGrantCliRole,
    SupervisorGrantUnwatchedPlan,
)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_a_supervisor_runs_a_switched_on_tier_one_verb_as_its_own_actor(story):
    result = story.supervisor_runs_command(story.agents.subject, "task create 'supervisor follow-up'")
    result.expect_command_passed()
    story.expect_row_in(story.supervisor_environment, "tasks", story.task_number(), {"creator": "plugin:journal-supervisor"})
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliProposalOnly, subject=AgentRole.SUPERVISOR)
def test_a_supervisor_cannot_run_a_propose_only_verb(story):
    result = story.supervisor_runs_command(story.agents.subject, "task create 'unapproved follow-up'")
    result.expect_command_refused()
    result.expect_command_text("the capability is set to propose")
    story.expect_row_count_in(story.supervisor_environment, "tasks", 1)
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantUnwatchedPlan, subject=AgentRole.SUPERVISOR)
def test_a_supervisor_cannot_run_a_verb_on_an_unwatched_plan(story):
    result = story.supervisor_runs_command(story.agents.subject, f"plan priorities 'finish this first' --plan {story.plans.second}")
    result.expect_command_refused()
    result.expect_command_text("unwatched plan")
    story.expect_row_in(story.supervisor_environment, "plans", story.plans.second, {"priorities": ""})
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliRole, subject=AgentRole.SUPERVISOR)
def test_a_supervisor_cli_call_with_the_wrong_grant_credential_is_refused(story):
    result = story.supervisor_runs_command(story.agents.subject, "task create 'bad credential task'", grant_credential="wrong")
    result.expect_command_refused()
    result.expect_command_text("supervisor service credential is invalid or revoked")
    story.expect_row_count_in(story.supervisor_environment, "tasks", 1)
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliProposalOnly, subject=AgentRole.SUPERVISOR)
def test_a_supervisor_reads_with_a_propose_only_grant(story):
    result = story.supervisor_runs_command(story.agents.subject, "task list")
    result.expect_command_passed()
    story.expect_stack(story.agents.subject)


@story(SupervisorGrantCliAlias, subject=AgentRole.SUPERVISOR)
def test_a_supervisor_cannot_run_a_shell_alias_outside_its_grant(story):
    result = story.supervisor_runs_command(story.agents.subject, story.aliases.first)
    result.expect_command_refused()
    result.expect_command_text("a supervisor may not run the alias")
    story.expect_stack(story.agents.subject)
