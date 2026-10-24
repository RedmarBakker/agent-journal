from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.secret_allowed import SecretAllowed
from journal.features.secrets.secrets_nudges import SecretsNudges
from journal.features.secrets.secrets_part import SecretsPart


class SecretsConduct(Conduct):
    """The secrets feature's conduct in every state: no tool of the agent's touches the secrets folder or the MCP keys, by any spelling that resolves there, and the agent is given what a secret may now be sent to when the user allows it."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return self.refuse(SecretsNudges.PRIVATE_SECRETS.create()) if event.data.part(SecretsPart).reaches(event.call.input) else self.none()

    def on_secret_allowed(self, event: SecretAllowed, settings: Settings) -> Transition:
        return self.none(SecretsNudges.SECRET_PROGRAM_GRANT.create(n=event.secret_id, title=event.title, programs=", ".join(event.programs)))
