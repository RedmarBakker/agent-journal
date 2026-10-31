from pathlib import Path

from journal.features.workers.organization_options import OrganizationOptions
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.main.working_agent import WorkingAgent


class OrganizationSetup(WorkingAgent):
    """The main agent read the overview after the organization folder was set."""

    parent = NewSession
    settings = ((OrganizationOptions.FOLDER, str(Path(__file__).resolve().with_name("organization_hub"))),)
