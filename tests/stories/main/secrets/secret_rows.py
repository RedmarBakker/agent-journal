from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import story
from tests.stories.fixtures.main.working_agent import WorkingAgent

GITHUB = "secret create Github --kind 'api key' --brief 'Run `curl -H @- https://api.github.com/user` or `bash -c x`, with GITHUB_KEY'"


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_secret_made_waits_for_the_user_and_proposes_the_programs_it_names_but_never_a_shell(story):
    story.agent_runs(GITHUB)
    secret = story.created_number("secret")
    story.expect_command_text(f"secret {secret} made: Github, waiting for the user to fill key on the Secrets page; proposed for the user to allow: curl")
    story.expect_command_text_without("bash")
    story.agent_runs(f"secret show {secret}")
    story.expect_command_text("GITHUB_KEY")
    story.expect_command_text("waiting for the user, hidden")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_secret_is_filled_by_the_user_never_by_a_command(story):
    story.agent_runs(GITHUB)
    secret = story.created_number("secret")
    story.agent_runs(f"secret fill {secret}")
    story.expect_command_text("filled by the user on the Secrets page, never by a command")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_value_the_agent_made_is_stored_from_its_file_and_the_file_taken_away(story):
    story.agent_runs(GITHUB)
    secret = story.created_number("secret")
    story.project_file_holding("made.txt", "  generated-password-value  \n")
    story.agent_runs(f"secret store {secret} key {story.project_root()}/made.txt")
    story.expect_command_passed()
    story.expect_no_project_file("made.txt")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_requested_secret_is_listed_and_a_deleted_one_comes_back_when_restored(story):
    story.agent_runs("secret request Stripe --why 'to read the invoices'")
    secret = story.created_number("secret")
    story.agent_runs("secret list")
    story.expect_command_text("Stripe")
    story.agent_runs(f"secret delete {secret}")
    story.agent_runs("secret list")
    story.expect_command_text_without("Stripe")
    story.agent_runs(f"secret restore {secret}")
    story.agent_runs("secret list")
    story.expect_command_text("Stripe")
    story.expect_stack(Ready)


@story(WorkingAgent, mode=BUILDER_MODE, scope=AgentRole.MAIN)
def test_a_secret_retitled_is_listed_by_its_new_title_and_the_folder_names_its_file(story):
    story.agent_runs(GITHUB)
    secret = story.created_number("secret")
    story.agent_runs(f"secret update {secret} --title GitHub")
    story.agent_runs("secret list")
    story.expect_command_text("GitHub")
    story.agent_runs("secret folder")
    story.expect_command_text(".env")
    story.expect_stack(Ready)
