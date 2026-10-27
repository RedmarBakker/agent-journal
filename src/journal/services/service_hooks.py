import json
import sys
import threading
import urllib.request

from journal.services.service_event import ServiceEvent
from journal.services.service_registration import ServiceRegistration

POST_SECONDS = 5.0


class ServiceHooks:
    """The services registered with the journal server, each at its address for the events it named: an event is posted to every service that wants it on a thread of its own, so no write waits on a service, and a question waits until each service has answered that it did what it asks; a service registers again when the server starts again, so the server keeps none on disk."""

    def __init__(self) -> None:
        self._registrations: dict[str, ServiceRegistration] = {}
        self._lock = threading.Lock()

    def register(self, registration: ServiceRegistration) -> None:
        with self._lock:
            self._registrations[registration.name] = registration

    def registrations(self) -> list[ServiceRegistration]:
        with self._lock:
            return list(self._registrations.values())

    def wanting(self, event: ServiceEvent) -> list[ServiceRegistration]:
        return [registration for registration in self.registrations() if registration.wants(event.name)]

    def post(self, event: ServiceEvent) -> None:
        for registration in self.wanting(event):
            threading.Thread(target=self.sent, args=(registration, event, POST_SECONDS), name=f"post {event.name} to {registration.name}", daemon=True).start()

    def succeeded(self, event: ServiceEvent, seconds: float) -> bool:
        return all([self.sent(registration, event, seconds) for registration in self.wanting(event)])

    @staticmethod
    def sent(registration: ServiceRegistration, event: ServiceEvent, seconds: float) -> bool:
        request = urllib.request.Request(registration.address, data=json.dumps(event.body()).encode(), method="POST", headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=seconds) as answer:
                return answer.status == 200
        except OSError as down:
            sys.stderr.write(f"the {registration.name} service at {registration.address} did not take {event.name}: {down}\n")
            return False
