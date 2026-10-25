import hashlib
import socket
import ssl
import time
from typing import Callable
from datetime import datetime, timezone

from journal.support.release import Release
from journal.config import Config
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.id_blocks import IdBlocks
from journal.repositories.journal_backup import JournalBackup

from journal.db.schema import Schema
from journal.repositories.environment_owners import OWNER, EnvironmentOwners
from journal.features.team.support.repository_identity import RepositoryIdentity
from journal.models.environment import Environment
from journal.models.link import Link
from journal.models.task import Task
from journal.models.support.ref import Ref
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.models.outgoing_change import CREATED, OutgoingChange
from journal.models.user import User
from journal.models.worker import Worker
from journal.repositories.outgoing_changes import OutgoingChanges
from journal.repositories.shared_tables import SharedTables
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.sync.block_supply import BlockSupply
from journal.services.service_event import TEAM_DEPARTURE, TEAM_JOINED, ServiceEvent
from journal.services.service_hooks import ServiceHooks
from journal.sync.team_account import TeamAccount
from journal.sync.team_server_link import TeamServerLink
from journal.sync.team_url import TeamUrl
from sync_server.login_answer import LoginAnswer
from sync_server.file_place import FilePlace
from journal.sync.attachments import FOLDERS
from journal.sync.hosting import Hosting
from journal.sync.journal_copy import JournalCopy
from journal.sync.team_chat_branch import TEAM_CHAT
from journal.version import VERSION
from journal.features.updates.support.release_installer import ReleaseInstaller
from journal.features.updates.support.release_source import REPOSITORY
from sync_server.login_request import LoginRequest
from journal.sync.team_refusal import TeamRefusal
from sync_server.team_details import ANY
from sync_server.team_summary import TeamSummary

BACKUP_NAME = "journal-before-team-%Y%m%d-%H%M%S.db"
TABLES = {folder: table for table, folder in FOLDERS.items()}


class TeamJoin:
    """A journal joining its team's server: the server's own certificate authority checked against the fingerprint when it has one, the repository checked against the team's (but for the team server's own hosted journal, which has no checkout), the journal's version against the team's pinned one (or, where the team allows any version, its migration against the team's), with the line to install the team's version when they differ, a team that holds a journal refused to a journal with tasks or messages of its own unless it asks to replace them, the code and password traded for this machine's token, and any row numbers stored from an earlier team let go, since only this team's server hands out numbers here; then a team with no journal yet takes this one whole, every file under .journal/files with it, each environment given its team name, the person's name before its own, and the Team chat, an environment named team owned by no one, stored when the journal holds one and made when it holds none, and the team's hub environment, named after the checkout's folder, which names the team on the server too; a team with one replaces this journal's shared rows with its copy, this journal stored as it was in a backup file beside it and the hook log emptied, and each of this machine's environments is found again in the copy by its key, keeping its own name, or made anew under its team name, every agent staying in its environment; and adds this person's user row. No environment's name on this machine is ever changed by a join. The sync service is told once it is done."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, tables: SharedTables, outgoing: OutgoingChanges, identity: RepositoryIdentity, backups: JournalBackup, config: Config, environments: Environments, agents: Agents, entries: Entries, owners: EnvironmentOwners, links: Links, copy: JournalCopy, schema: Schema, hosting: Hosting, blocks: IdBlocks, supply: BlockSupply, hooks: ServiceHooks, messages: Messages) -> None:
        self.account, self.link, self.tables, self.outgoing, self.identity = account, link, tables, outgoing, identity
        self.backups, self.config, self.environments, self.agents, self.entries = backups, config, environments, agents, entries
        self.owners, self.links, self.copy, self.schema, self.hosting, self.blocks, self.supply = owners, links, copy, schema, hosting, blocks, supply
        self.hooks, self.messages = hooks, messages

    def join(self, url: TeamUrl, email: str, password: str, name: str) -> str:
        return self.joined(url, email, password, name, self.history_refusal)

    def join_replacing(self, url: TeamUrl, email: str, password: str, name: str) -> str:
        return self.joined(url, email, password, name, lambda summary, url: "")

    def joined(self, url: TeamUrl, email: str, password: str, name: str, guard: Callable[[TeamSummary, TeamUrl], str]) -> str:
        if self.account.is_joined():
            raise Rejection(f"this journal has joined the team at {self.account.address()} already: journal team status says how it stands")
        self.trusted(url)
        summary = self.link.summary(url.address)
        repository = self.identity.first_commit()
        if self.repository_refusal(summary, repository):
            raise Rejection(self.repository_refusal(summary, repository))
        if self.version_refusal(summary):
            raise Rejection(self.version_refusal(summary))
        if guard(summary, url):
            raise Rejection(guard(summary, url))
        login = self.login(url, summary, email or self.identity.person_email(), name or self.identity.person_name(), password)
        self.blocks.clear()
        address = url.address
        prefix = self.account.write_prefix(login.name)
        if not summary.has_rows:
            self.claim_environments(prefix, login.account_id)
            self.name_user(login.account_id, login.name)
            self.team_chat_ready()
            self.environments.save(Environment.hub(summary.key, self.team_name()), Actor.system())
        self.account.write({"address": address, "token": login.token, "device": login.device_id, "account_id": login.account_id, "role": login.role, "sequence": 0, "team_version": summary.version or VERSION, "team_key": summary.key, "team_name": summary.name or self.team_name()})
        outcome = self.downloaded(login.account_id, login.name) if summary.has_rows else self.uploaded(repository)
        self.hooks.post(ServiceEvent(TEAM_JOINED))
        return outcome

    def leave(self) -> str:
        if not self.account.is_joined():
            raise Rejection("this journal is in no team")
        address = self.account.address()
        self.blocks.clear()
        self.outgoing.clear()
        backup = self.account.leave(time.time())
        self.hooks.post(ServiceEvent(TEAM_DEPARTURE))
        return f"left the team at {address}: sync stopped, every local row kept, and the team's settings kept in {backup.name}; claim a server or connect with an account to join one again"

    def repository_refusal(self, summary: TeamSummary, repository: str) -> str:
        if not summary.repository or summary.repository == repository or self.hosting.is_hosted():
            return ""
        return f"the team's journal belongs to the repository whose first commit is {summary.repository}, and this checkout's is {repository or 'none'}: join from a clone of the team's repository"

    def version_refusal(self, summary: TeamSummary) -> str:
        if not summary.has_rows or summary.version in ("", VERSION):
            return ""
        if summary.versions == ANY and summary.migration == self.schema.version():
            return ""
        tag = Release.tagged(summary.version)
        return f"the team runs journal version {summary.version} and this journal {VERSION}: install {summary.version} first with curl -fsSL {ReleaseInstaller.script_path(REPOSITORY, tag)} | AGENT_JOURNAL_REF={tag} sh, then join again"

    def history_refusal(self, summary: TeamSummary, url: TeamUrl) -> str:
        tasks, messages = self.tables.rows(Task.table()).stored_count(), self.messages.message_count()
        if not summary.has_rows or not tasks + messages:
            return ""
        return (f"this journal holds {tasks} tasks and {messages} messages of its own, and the team at {url.address} holds a journal already, which a join would put in place of this one: "
                f"join from a fresh clone of the repository, or take the team's journal in place of this one, this journal kept in a backup file beside it, with: journal team join --replace-mine '{url.invitation(url.code, url.fingerprint) if url.is_invitation() else url.address}'")

    def claim_refusal(self, url: TeamUrl) -> str:
        self.trusted(url)
        if self.link.summary(url.address).has_admin:
            return f"the team server at {url.address} has its admin already: connect with your account, or with the invitation URL an admin shares"
        return ""

    def trusted(self, url: TeamUrl) -> None:
        if url.fingerprint:
            self.trust(url.address, url.fingerprint)
        elif url.has_self_signed_certificate():
            self.account.root_path().write_text(self.link.root_certificate(url.address))

    def login(self, url: TeamUrl, summary: TeamSummary, email: str, name: str, password: str) -> LoginAnswer:
        if not summary.has_admin:
            return self.link.install(url.address, email, name, password, socket.gethostname())
        if not url.is_invitation():
            return self.account_login(url, email, password)
        return self.link.accept(url.address, url.code, email, name, password, socket.gethostname())

    def account_login(self, url: TeamUrl, email: str, password: str) -> LoginAnswer:
        try:
            return self.link.login(url.address, LoginRequest(email, password, socket.gethostname()))
        except TeamRefusal as refused:
            raise Rejection(f"the team server at {url.address} has its admin already: join with your own account's email and password there, or with the invitation URL an admin shares from the Team tab ({refused})") from refused

    def trust(self, address: str, fingerprint: str) -> None:
        certificate = self.link.root_certificate(address)
        if hashlib.sha256(ssl.PEM_cert_to_DER_cert(certificate)).hexdigest() != fingerprint.lower():
            raise Rejection(f"the server at {address} does not hold the certificate the fingerprint names: check the join line, or the address")
        self.account.root_path().write_text(certificate)

    def uploaded(self, repository: str) -> str:
        rows = self.copy.rows()
        answer = self.link.upload(rows, self.copy.highest(rows), repository, VERSION, self.team_name())
        self.account.record_sequence(answer.head)
        files = self.upload_files()
        self.supply.refill()
        self.stamp_workers()
        return f"this journal is now the team's: {answer.rows} rows and {files} files uploaded"

    def team_name(self) -> str:
        return self.config.root.name

    def upload_files(self) -> int:
        files = [path for table, folder in FOLDERS.items() for path in (self.config.files / folder).glob("*/*") if path.is_file() and path.parent.name.isdigit()]
        for path in files:
            self.link.upload_file(FilePlace(TABLES[path.parent.parent.name], int(path.parent.name), path.name), path.read_bytes())
        return len(files)

    def downloaded(self, account_id: int, name: str) -> str:
        self.supply.refill()
        copy = self.link.full_copy()
        backup = self.config.home / time.strftime(BACKUP_NAME)
        self.backups.write(backup)
        local_environments = self.environments.working()
        local_agents = {environment.key: self.agents.global_matching(environment_id=environment.row_id) for environment in local_environments}
        self.outgoing.clear()
        self.entries.clear()
        self.copy.replace_whole(copy.rows)
        self.account.record_sequence(copy.head)
        self.add_user(account_id, name)
        for environment in local_environments:
            team_row = self.reowned(environment)
            for agent in local_agents[environment.key]:
                self.agents.save(agent.with_(environment_id=team_row.row_id), Actor.system())
        return f"joined the team: {len(copy.rows)} rows downloaded, and this journal as it was kept in {backup.name}"

    def reowned(self, environment: Environment) -> Environment:
        for namesake in self.environments.namesakes(environment.name, environment.key):
            self.environments.save(namesake.with_(name=f"{namesake.name}-{namesake.row_id}"), Actor.system())
        keyed_rows = self.environments.keyed(environment.key)
        if keyed_rows:
            return self.environments.save(keyed_rows[0].with_(name=environment.name), Actor.system())
        return self.environments.save(Environment(name=environment.name, branch=environment.branch, key=environment.key).team_ready(self.account.prefix()), Actor.system())

    def add_user(self, account_id: int, name: str) -> None:
        users = self.tables.rows(User.table())
        if users.numbered([account_id]):
            return
        user = users.pulled_creation(account_id, {"name": name}, Actor.system())
        fields = Schema.stored_values(user, None)
        self.outgoing.queued(OutgoingChange(row_table=User.table(), row=account_id, action=CREATED, fields=fields, changed_at={field: 0.0 for field in fields}, writer=Actor.user(account_id).stamp), Actor.user(account_id))

    def team_chat_ready(self) -> None:
        chats = self.environments.team_chats()
        if not chats:
            self.environments.save(Environment(name=TEAM_CHAT, team_name=TEAM_CHAT, is_team_chat=True), Actor.system())
            return
        for chat in chats:
            self.environments.save(chat.with_(team_name=TEAM_CHAT), Actor.system())

    def claim_environments(self, prefix: str, account_id: int) -> None:
        for environment in self.environments.working():
            if not self.owners.owner_number(environment.row_id):
                self.links.save(Link(source=Ref(User.table(), account_id), target=Ref.build(environment), kind=OWNER), Actor.system())
            if environment.team_name is None:
                self.environments.save(environment.team_ready(prefix), Actor.system())

    def name_user(self, account_id: int, name: str) -> None:
        users = self.tables.rows(User.table())
        moment = datetime.now(timezone.utc).isoformat()
        if not users.pulled_update(account_id, {"name": name, "updated_at": moment}, Actor.system()):
            users.pulled_creation(account_id, {"name": name, "created_at": moment, "updated_at": moment}, Actor.system())

    def stamp_workers(self) -> None:
        workers = self.tables.rows(Worker.table())
        for worker in workers.rows():
            if not worker.device:
                workers.save(worker.with_(device=self.account.device()), Actor.system())
