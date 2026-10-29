import tomllib
from pathlib import Path

from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.cardinality import Cardinality
from journal.features.organization.support.contract_problem import ContractProblem
from journal.features.organization.support.edge_reader import EdgeReader
from journal.features.organization.support.model_reader import ModelReader
from journal.features.organization.support.role import EDIT_TOOL, Role
from journal.features.organization.support.tool_ids import ToolIds
from journal.features.organization.support.toml_fields import TomlFields

KEYS = ("id", "title", "domain", "description", "cardinality", "writes", "responsible", "not_responsible", "inputs", "outputs", "edges", "skills", "tools", "approval_required", "model")
GUIDANCE = "AGENTS.md"


class RoleReader:
    """Reads a Role from its folder: role.toml for the structure and the AGENTS.md beside it as its guidance; a file that breaks any rule gives no Role and every problem it has."""

    def __init__(self, models: ModelReader, edges: EdgeReader, tools: ToolIds) -> None:
        self.models, self.edges, self.tools = models, edges, tools

    def read(self, folder: Path, relative: str, domain_id: str, known_skills: frozenset[str]) -> tuple[Role | None, tuple[ContractProblem, ...]]:
        path = f"{relative}/role.toml"
        try:
            data = tomllib.loads((folder / "role.toml").read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeDecodeError) as broken:
            return None, (ContractProblem(path, "parse", f"role.toml does not parse: {broken}"),)
        fields = TomlFields(path, data)
        role = self.role(fields, folder, domain_id, known_skills)
        return (None, tuple(fields.problems)) if fields.problems else (role, ())

    def role(self, fields: TomlFields, folder: Path, domain_id: str, known_skills: frozenset[str]) -> Role:
        fields.unknown(KEYS)
        role_id, domain = fields.text("id"), fields.text("domain")
        if role_id and role_id != folder.name:
            fields.problem("id", f"id is {role_id} but the folder is {folder.name}; make them the same")
        if domain and domain != domain_id:
            fields.problem("domain", f"domain is {domain} but the Role is in the folder of {domain_id}")
        cardinality, writes = self.cardinality(fields), fields.flag("writes")
        tools, skills = fields.listed("tools"), fields.listed("skills")
        self.check_tools(fields, tools, writes)
        self.check_skills(fields, skills, known_skills)
        models = self.models.read(fields, writes)
        guidance = self.guidance(fields, folder)
        return Role(role_id, fields.text("title"), domain, fields.text("description"), cardinality, writes, fields.texts("responsible"), fields.texts("not_responsible"), fields.texts("inputs"), fields.texts("outputs"),
                    self.edges.read(fields), skills, tools, self.approvals(fields), models, guidance)

    @staticmethod
    def cardinality(fields: TomlFields) -> Cardinality:
        value = fields.text("cardinality")
        if value not in Cardinality:
            fields.problem("cardinality", f"cardinality is {value}; use one of {', '.join(Cardinality)}")
            return Cardinality.MANY
        return Cardinality(value)

    def check_tools(self, fields: TomlFields, tools: tuple[str, ...], writes: bool) -> None:
        for tool in tools:
            if not self.tools.is_well_formed(tool):
                fields.problem("tools", f"tool {tool} is not an id; write it in lower case with underscores")
        if len(set(tools)) != len(tools):
            fields.problem("tools", "a tool is listed twice")
        if writes != (EDIT_TOOL in tools):
            fields.problem("tools", f"a Role that writes lists {EDIT_TOOL}, and one that does not write does not")

    @staticmethod
    def check_skills(fields: TomlFields, skills: tuple[str, ...], known: frozenset[str]) -> None:
        for skill in skills:
            if skill not in known:
                fields.problem("skills", f'"{skill}" is not the id of a skill; list the name of a skill folder')
        if len(set(skills)) != len(skills):
            fields.problem("skills", "a skill is listed twice")

    @staticmethod
    def approvals(fields: TomlFields) -> tuple[ApprovalAction, ...]:
        listed = fields.listed("approval_required")
        for action in listed:
            if action not in ApprovalAction:
                fields.problem("approval", f"{action} is not an action that waits for approval; use one of {', '.join(ApprovalAction)}")
        return tuple(ApprovalAction(action) for action in dict.fromkeys(listed) if action in ApprovalAction)

    @staticmethod
    def guidance(fields: TomlFields, folder: Path) -> str:
        if not (folder / GUIDANCE).is_file():
            fields.problem("guidance", f"{GUIDANCE} is missing beside role.toml")
            return ""
        return (folder / GUIDANCE).read_text(encoding="utf-8")
