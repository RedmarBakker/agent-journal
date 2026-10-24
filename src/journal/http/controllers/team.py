import time
from dataclasses import asdict

from journal.features.team.support.repository_identity import RepositoryIdentity
from journal.features.team.support.team_join import TeamJoin
from journal.features.workers.support.pool_overview import PoolOverview
from journal.sync.team_url import TeamUrl
from journal.http.support.request import Request
from journal.repositories.environment_owners import EnvironmentOwners
from journal.repositories.environments import Environments
from journal.support.response import Response
from journal.sync.sync_status import SyncStatus
from journal.sync.team_account import TeamAccount
from journal.sync.team_requests import TeamRequests
from journal.sync.team_server_link import TeamServerLink
from journal.version import VERSION

ONLINE_SECONDS = 120


class TeamController:
    """The viewer's Team tab: how this journal stands with its team, the join a journal in no team makes from it by a team URL, the email git knows filled in, as journal team join does, the team's people with their environments and when they were last seen, the worker pool, the slots this machine gives and the pool workers it runs, a stop of one of them, this journal's pool workers elsewhere and the team's, and for an admin the invitation, answered with the line the person joins with, and the devices, one of which can be revoked."""

    def __init__(self, account: TeamAccount, joining: TeamJoin, link: TeamServerLink, status: SyncStatus, environments: Environments, owners: EnvironmentOwners, identity: RepositoryIdentity, pool_overview: PoolOverview) -> None:
        self.account, self.joining, self.link, self.status, self.identity = account, joining, link, status, identity
        self.environments, self.owners, self.pool_overview = environments, owners, pool_overview

    def show(self, request: Request) -> Response:
        if not self.account.is_joined():
            return Response.json({"joined": False, "email": self.identity.person_email()})
        return Response.json({"joined": True, "address": self.account.address(), "line": self.status.line(), "state": self.status.state(), "version": self.account.team_version(), "running": VERSION, "waiting": self.status.waiting(), "admin": self.account.is_admin(), "device": self.account.device()})

    def join(self, request: Request) -> Response:
        body = request.body
        outcome = TeamRequests.reached(lambda: self.joining.join(TeamUrl.parse(str(body.get("url", ""))), str(body.get("email", "")).strip(), str(body.get("password", "")), str(body.get("name", "")).strip()))
        return Response.json({"outcome": outcome, "environment": request.environment}, 201)

    def pool(self, request: Request) -> Response:
        lent = self.pool_overview.lent()
        slots = self.pool_overview.slots()
        return Response.json({"slots": slots, "free": max(slots - len(lent), 0), "minutes_today": self.pool_overview.minutes_today(), "minute_cap": self.pool_overview.minute_cap(), "lent": [asdict(line) for line in lent], "elsewhere": [asdict(line) for line in self.pool_overview.remote_runs()], "team": [asdict(line) for line in self.pool_overview.team()]})

    def pool_stop(self, request: Request) -> Response:
        self.pool_overview.stop(request.number("id"), request.actor)
        return self.pool(request)

    def people(self, request: Request) -> Response:
        answer = TeamRequests.reached(self.link.people)
        rows = self.environments.rows()
        checked_at = time.time()
        return Response.json({"people": [{"id": person.id, "name": person.name, "role": person.role, "me": person.id == request.actor.number(), "online": checked_at - person.pulled_at < ONLINE_SECONDS, "seen_at": person.pulled_at, "environments": [{"id": row.row_id, "name": row.name} for row in rows if self.owners.owner_number(row.row_id) == person.id]} for person in answer.people]})

    def password(self, request: Request) -> Response:
        TeamRequests.reached(lambda: self.link.change_password(str(request.body.get("old", "")), str(request.body.get("new", ""))))
        return Response.json({"changed": True})

    def password_reset(self, request: Request) -> Response:
        return Response.json({"password": TeamRequests.reached(lambda: self.link.reset_password(request.number("id")))})

    def opening(self, request: Request) -> Response:
        code = TeamRequests.reached(self.link.signin_code)
        return Response.json({"url": f"{self.account.address()}/open?code={code}"})

    def invite(self, request: Request) -> Response:
        answer = TeamRequests.reached(lambda: self.link.invite(str(request.body.get("email", "")).strip()))
        return Response.json({"email": answer.email, "url": self.account.invitation_url(answer.code)})

    def devices(self, request: Request) -> Response:
        names = {person.id: person.name for person in TeamRequests.reached(self.link.people).people}
        listed = TeamRequests.reached(self.link.devices).devices
        return Response.json({"devices": [{"id": device.id, "name": device.name, "person": names.get(device.account_id, f"user {device.account_id}"), "pulled_at": device.pulled_at, "this": str(device.id) == str(self.account.device())} for device in listed if not device.is_revoked()]})

    def revoke(self, request: Request) -> Response:
        TeamRequests.reached(lambda: self.link.revoke(request.number("id")))
        return self.devices(request)
