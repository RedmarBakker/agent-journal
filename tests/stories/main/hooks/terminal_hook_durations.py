from journal.features.briefing.briefing_nudges import BriefingNudges
from journal.features.faults.faults_options import FaultsOptions
from journal.features.tasks.states.ready import Ready
from journal.features.workers.workers_options import BUILDER_MODE
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from journal.support.agent_role import AgentRole
from tests.stories.builder.story_marks import provider, setting, story
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.working_agent import WorkingAgent


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@provider(Claude)
@setting(FaultsOptions.HOOK_TIME_COPY, True)
def test_each_hook_shows_its_duration_to_the_user_alone_until_the_setting_is_switched_off(story):
    result = story.agent_reads(story.agents.subject)
    result.expect_hook_duration_shown()
    story.user_sets(FaultsOptions.HOOK_TIME_COPY, False)
    story.agent_reads(story.agents.subject)
    story.expect_no_hook_duration()
    story.expect_stack(story.agents.subject, Ready)


@story(NewSession, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@provider(Claude)
@setting(FaultsOptions.HOOK_TIME_COPY, True)
def test_a_refused_hook_shows_its_duration_to_the_user_and_keeps_it_out_of_the_refusal(story):
    result = story.agent_writes(story.agents.subject, "footer.py")
    result.expect_refused(story.agents.subject, BriefingNudges.OVERVIEW_REQUEST)
    result.expect_hook_duration_shown()
    story.expect_stack(story.agents.subject, Ready)


@story(WorkingAgent, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@provider(Codex)
@setting(FaultsOptions.HOOK_TIME_COPY, True)
def test_a_codex_stop_shows_its_duration_to_the_user_alone(story):
    result = story.agent_stops(story.agents.subject)
    result.expect_hook_duration_shown()
    story.expect_stack(story.agents.subject, Ready)
