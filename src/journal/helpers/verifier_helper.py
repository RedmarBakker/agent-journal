from journal.features.plugins.listeners.plugin_agent_relay import PluginAgentRelay
from journal.features.verification.commands.verdict_command import VerdictCommand
from journal.features.verification.feature import Verification
from journal.features.verification.states.verifying import Verifying
from journal.features.helper import Helper
from journal.support.agent_role import AgentRole


class VerifierHelper(Helper):
    """A verifier: judges a dismissal yes or no with one reason, verifying from its first hook; the plugins hear it."""

    role = AgentRole.VERIFIER
    first_state = Verifying
    features = (Verification,)
    commands = (
        (VerdictCommand, "give"),
        (VerdictCommand, "model"),
    )
    listeners = (PluginAgentRelay,)
