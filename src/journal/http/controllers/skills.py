from journal.features.registry import Registry
from journal.features.skills.support.skill_files import SkillFiles
from journal.http.support.request import Request
from journal.support.response import Response
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.supervisor_link import SupervisorLink
from journal.repositories.setting_rows import SettingRows
from journal.features.skills.skills_options import SkillsOptions
from journal.features.skills.skills_nudges import SkillsNudges
from journal.engine.nudger import Nudger

MOMENTS = {"session_start": SkillsOptions.START_SKILLS, "after_compaction": SkillsOptions.COMPACTION_SKILLS}


class SkillController:
    """The journal's skills, with whether the agent concerned has read each and whether each is required at a session start and after a compaction; one opened whole, one the running agent is instructed to read now, and either moment switched for one."""

    def __init__(self, registry: Registry, agents: Agents, skill_files: SkillFiles, supervisor: SupervisorLink, scope: Scope, settings: SettingRows, nudger: Nudger) -> None:
        self.registry, self.agents, self.skill_files, self.supervisor, self.scope, self.settings = registry, agents, skill_files, supervisor, scope, settings
        self.nudger = nudger

    def index(self, request: Request) -> Response:
        agent = next(iter(self.agents.numbered(request.query.get("agent", ""))), None)
        loaded = set(agent.skills_loaded.keys()) if agent else set()
        starts, compactions = self.settings.texts(SkillsOptions.START_SKILLS), self.settings.texts(SkillsOptions.COMPACTION_SKILLS)
        return Response.json([{"name": skill.name, "description": skill.description, "loaded": skill.name in loaded, "session_start": skill.name in starts, "after_compaction": skill.name in compactions} for skill in self.registry.skills()])

    def moment(self, request: Request) -> Response:
        skill = self.registry.skill(request.params["name"])
        option = MOMENTS.get(request.body.get("moment", ""))
        if skill is None or option is None:
            return Response.absent("no such skill or moment")
        if request.body.get("on"):
            self.settings.with_line(option, skill.name, request.actor)
        else:
            self.settings.without_line(option, skill.name, request.actor)
        return Response.json({"name": skill.name, request.body["moment"]: bool(request.body.get("on"))})

    def show(self, request: Request) -> Response:
        skill = self.registry.skill(request.params["name"])
        return Response.json({"name": skill.name, "description": skill.description, "text": skill.body}) if skill else Response.absent("no such skill")

    def load(self, request: Request) -> Response:
        skill = self.registry.skill(request.params["name"])
        if skill is None:
            return Response.absent("no such skill")
        agent = self.agents.current()
        line = self.nudger.deliver(agent, SkillsNudges.SKILL_VIEWER_REQUEST.create(name=skill.name, path=str(self.skill_files.path(skill)))) if agent else None
        if line:
            self.supervisor.type(self.scope.id, line)
        return Response.json({"queued": bool(line)})
