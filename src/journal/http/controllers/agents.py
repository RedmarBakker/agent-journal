import mimetypes
import time as timing

from journal.db.query import Query
from journal.config import Config
from journal.features.pausing.agent_pause import AgentPause
from journal.features.schedules.job_stop import JobStop
from journal.features.sequences.support.run_tracker import RunTracker
from journal.http.agents.agent_activity import AgentActivity
from journal.http.agents.agent_bar_writes import AgentBarWrites
from journal.http.agents.terminal_lines import TerminalLines
from journal.http.controllers.controller import Controller
from journal.features.edits.support.image_files import ImageFiles
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.http.support.sandboxed_file_response import SandboxedFileResponse
from journal.support.response import Response
from journal.models.agent import Agent
from journal.models.edit import Edit
from journal.providers.providers import Providers
from journal.support.rejection import Rejection
from journal.repositories.agents import Agents
from journal.repositories.edits import Edits
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.supervisor_link import SupervisorLink
from journal.support.time_source import TimeSource
from journal.models.agent import ENDED_STATE

EDITS_SHOWN = 50


class AgentController(Controller[Agent]):
    """The environment's agents, one read by id with what it is doing; what the user types or picks for the running one goes to its terminal, and the files it changed and the commands it ran are read from here."""

    repository: Agents

    def __init__(self, agents: Agents, activity: AgentActivity, supervisor: SupervisorLink, terminal_lines: TerminalLines, edits: Edits, scope: Scope, environments: Environments,
                 providers: Providers, active: RunTracker, config: Config, pausing: AgentPause, job_stop: JobStop, writes: AgentBarWrites, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.repository, self.activity, self.supervisor, self.terminal_lines, self.file_edits, self.scope = agents, activity, supervisor, terminal_lines, edits, scope
        self.environments, self.providers, self.running, self.config, self.pausing, self.job_stop = environments, providers, active, config, pausing, job_stop
        self.writes = writes

    def open_rows(self, query: Query) -> Query:
        return query.filter_unequal("state", ENDED_STATE)

    def closed_rows(self, query: Query) -> Query:
        return query.filter(state=ENDED_STATE)

    def shown_page(self, rows: list[Agent]) -> list[dict]:
        return self.activity.page(rows)

    def current(self, request: Request) -> Response:
        rows = []
        for environment in self.environments.all():
            with self.scope.environment(environment.row_id):
                agent = self.repository.current()
            if agent:
                rows.append({"environment": environment.name, "agent": agent})
        return Response.json(rows)

    def type(self, request: Request) -> Response:
        self.supervisor.type(self.scope.id, request.body.get("line", ""))
        return Response.json({})

    def shell(self, request: Request) -> Response:
        command = request.body.get("command", "").strip()
        if command:
            self.writes.shell(self.repository.find(request.number("id")), command)
        return Response.json({"queued": bool(command)})

    def controls(self, request: Request) -> Response:
        provider = self.providers.lookup(request.params["provider"])
        current = {"model": request.query.get("model", ""), "effort": request.query.get("effort", "")}
        return Response.json({"groups": [{**group, "current": current.get(group["key"], "")} for group in provider.controls["groups"]], "note": provider.controls["note"]})

    def control(self, request: Request) -> Response:
        action, value = request.body.get("action", ""), request.body.get("value", "")
        self.writes.control(self.repository.find(request.number("id")), action, value)
        return Response.json({"queued": True})

    def edits(self, request: Request) -> Response:
        session = self.session(request.number("id"))
        shown = self.file_edits.agent_edits(session, request.queried("since"), EDITS_SHOWN, int(request.queried("before")))
        older = bool(shown) and self.file_edits.has_older(session, shown[0].row_id)
        return Response.json({"cursor": self.time_source.seconds(), "edits": [self.listed_edit(edit) for edit in shown], "older": older})

    def listed_edit(self, edit: Edit) -> dict:
        return {**ModelFields.build(edit), "old_text": "", "new_text": "", "has_text": bool(edit.old_text or edit.new_text), "image": ImageFiles.is_image(edit.path)}

    def requested_edit(self, request: Request) -> Edit:
        edit = self.file_edits.find(int(request.queried("edit")))
        if edit.session != self.session(request.number("id")):
            raise Rejection("no such edit")
        return edit

    def edited_text(self, request: Request) -> Response:
        edit = self.requested_edit(request)
        return Response.json({"path": edit.path, "old_text": edit.old_text, "new_text": edit.new_text, "stored": bool(edit.old_text or edit.new_text)})

    def edited_image(self, request: Request) -> SandboxedFileResponse | Response:
        edit = self.requested_edit(request)
        file = (self.config.root / edit.path).resolve()
        if not ImageFiles.is_image(edit.path) or not file.is_relative_to(self.config.root.resolve()) or not file.is_file():
            return Response.absent(edit.path)
        return SandboxedFileResponse(mimetypes.guess_type(file.name)[0] or "application/octet-stream", file.read_bytes())

    def session(self, id: int) -> str:
        return self.repository.find(id).session

    def terminal(self, request: Request) -> Response:
        return Response.json(self.terminal_lines.lines(self.repository.find(request.number("id")), request.queried("after")))

    def pause(self, request: Request) -> Response:
        return Response.json(self.shown(self.pausing.pause(self.repository.find(request.number("id")), request.actor)))

    def resume(self, request: Request) -> Response:
        return Response.json(self.shown(self.pausing.resume(self.repository.find(request.number("id")), request.actor)))

    def stop_job(self, request: Request) -> Response:
        self.job_stop.stop(self.repository.find(request.number("id")), request.params["job"], request.actor)
        return Response.json({"asked": True})

    def skip_step(self, request: Request) -> Response:
        agent = self.running_agent(request.number("id"))
        self.running.skip(agent.session, agent.environment_id)
        return Response.json(self.shown(self.repository.find(agent.row_id)))

    def end_sequence(self, request: Request) -> Response:
        agent = self.running_agent(request.number("id"))
        self.running.end(agent.session, agent.environment_id)
        return Response.json(self.shown(self.repository.find(agent.row_id)))

    def running_agent(self, id: int) -> Agent:
        agent = self.repository.find(id)
        if self.running.current(agent.session, agent.environment_id) is None:
            raise Rejection(f"agent {id} runs no sequence")
        return agent

