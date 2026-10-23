import threading
from functools import partial
from typing import Callable

from journal.models.author import Author
from journal.models.message import Message
from journal.repositories.environments import Environments
from journal.repositories.messages import Messages
from journal.repositories.pool_jobs import PoolJobs
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.sync.team_server_link import TeamServerLink
from sync_server.host_request import HostRequest


class HostDesk:
    """Makes the writes the team server holds for the environments this journal hosts, each as the person who asked, so its events are dispatched and handled here, and tells the server it is made; a feature registers the kinds it makes; a worker offered from the pool is kept as a pool job, whose arrival the workers feature hears and takes up off the sync thread; one at a time, so a request that a push and a pull both bring is made once, the message's idempotency key finding it made."""

    MESSAGE = "message"
    POOL_WORKER = "pool_worker"

    def __init__(self, link: TeamServerLink, environments: Environments, messages: Messages, scope: Scope, jobs: PoolJobs) -> None:
        self.link, self.environments, self.messages, self.scope, self.jobs = link, environments, messages, scope, jobs
        self.makers = {self.MESSAGE: self.message, self.POOL_WORKER: self.jobs.arrived}
        self.lock = threading.Lock()

    def register(self, kind: str, writer: Callable[[HostRequest], None]) -> None:
        self.makers[kind] = partial(self.finished_write, writer)

    def finished_write(self, writer: Callable[[HostRequest], None], request: HostRequest) -> None:
        writer(request)
        self.link.finish_host_request(request.id)

    def handle(self, requests: tuple[HostRequest, ...]) -> None:
        with self.lock:
            for request in requests:
                self.makers[request.kind](request)

    def message(self, request: HostRequest) -> None:
        for environment in self.environments.keyed(request.environment_key):
            with self.scope.environment(environment.row_id):
                self.messages.posted(Message(environment_id=environment.row_id, author=Author.USER, **request.body), Actor.user(request.account_id))
        self.link.finish_host_request(request.id)
