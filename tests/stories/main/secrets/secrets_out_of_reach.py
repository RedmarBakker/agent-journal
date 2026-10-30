from pathlib import Path

from journal.features.secrets.secrets_nudges import SecretsNudges
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from journal.support.secret_values import SecretValues
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

GITHUB = "secret create Github --kind 'api key' --brief 'Run `curl -H @- https://api.github.com/user`, with GITHUB_KEY'"


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_agent_is_refused_every_read_of_the_secrets_and_the_mcp_keys(story):
    values = story.app.container.get(SecretValues).path
    keys = Path.home() / ".journal" / "keys"
    result = story.agent_reads(story.agents.subject, str(values))
    result.expect_refused(story.agents.subject, SecretsNudges.PRIVATE_SECRETS)
    result = story.agent_runs_in_the_shell(story.agents.subject, f"cat {values.parent}/*.env")
    result.expect_refused(story.agents.subject, SecretsNudges.PRIVATE_SECRETS)
    result = story.agent_uses_the_providers_tool(story.agents.subject, "Grep", pattern="KEY", path=str(keys))
    result.expect_refused(story.agents.subject, SecretsNudges.PRIVATE_SECRETS)
    result = story.agent_reads(story.agents.subject, "../" * len(story.app.config.root.resolve().parts) + str(keys.resolve()).lstrip("/") + "/x.json")
    result.expect_refused(story.agents.subject, SecretsNudges.PRIVATE_SECRETS)
    result = story.agent_reads(story.agents.subject, str(story.app.config.root / "a.py"))
    result.expect_allowed()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
def test_the_agent_is_told_when_the_user_allows_a_program_its_secret_proposed(story):
    story.agent_runs(story.agents.subject, GITHUB)
    secret = story.created_number("secret")
    story.user_posted(f"/journal/secrets/{secret}", {"programs": ["curl"], "proposed": []})
    story.expect_typed(SecretsNudges.SECRET_PROGRAM_GRANT.create(n=secret, programs="curl"))
    story.expect_stack(story.agents.subject, Ready)
