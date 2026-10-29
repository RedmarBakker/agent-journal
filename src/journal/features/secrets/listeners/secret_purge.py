import time
from datetime import datetime, timedelta, timezone

from journal.support.timeout import Timeout
from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.secrets.support.browser_logins import BrowserLogins
from journal.support.actor import Actor
from journal.support.secret_field import SecretField
from journal.repositories.secrets import Secrets
from journal.support.secret_values import SecretValues
from journal.support.time_source import TimeSource

RETENTION = timedelta(days=30)
INTERVAL_SECONDS = 3600.0


class SecretPurge(AgentListener[Ticked]):
    """A secret deleted thirty days ago is removed permanently, with its values, its saved login and its row; a value replaced thirty days ago is no longer stored for masking."""

    def __init__(self, secrets: Secrets, values: SecretValues, logins: BrowserLogins, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.secrets, self.values, self.logins = secrets, values, logins
        self._looked_at = 0.0

    def handle(self, event: Ticked) -> None:
        if not Timeout.seconds(INTERVAL_SECONDS).started(self._looked_at).is_elapsed(self.time_source.seconds()):
            return
        self._looked_at = self.time_source.seconds()
        cutoff = self.time_source.moment() - RETENTION
        for secret in self.secrets.stale_retired(cutoff):
            self.values.drop([SecretField.build(raw).variable for raw in secret.fields])
            self.logins.drop(secret.title)
            self.secrets.delete(secret, Actor.system())
        retired = self.values.retired_earlier(cutoff.timestamp())
        if retired:
            self.values.drop(retired)
