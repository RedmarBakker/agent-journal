import tomllib
from pathlib import Path

from journal.features.organization.support.contract_problem import ContractProblem
from journal.features.organization.support.domain import Domain
from journal.features.organization.support.edge_reader import EdgeReader
from journal.features.organization.support.model_reader import ModelReader
from journal.features.organization.support.routing_rule import RoutingRule
from journal.features.organization.support.toml_fields import TomlFields

KEYS = ("id", "title", "description", "outcome", "responsible", "not_responsible", "roles", "skills", "model", "guidance", "edges", "routing")
GUIDANCE = "AGENTS.md"


class DomainReader:
    """Reads a domain from its folder: domain.toml for the structure and the guidance file it names, AGENTS.md by default, as the guidance its Roles share."""

    def __init__(self, models: ModelReader, edges: EdgeReader) -> None:
        self.models, self.edges = models, edges

    def read(self, folder: Path, relative: str, known_skills: frozenset[str]) -> tuple[Domain | None, tuple[ContractProblem, ...]]:
        path = f"{relative}/domain.toml"
        try:
            data = tomllib.loads((folder / "domain.toml").read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeDecodeError) as broken:
            return None, (ContractProblem(path, "parse", f"domain.toml does not parse: {broken}"),)
        fields = TomlFields(path, data)
        domain = self.domain(fields, folder, known_skills)
        return (None, tuple(fields.problems)) if fields.problems else (domain, ())

    def domain(self, fields: TomlFields, folder: Path, known_skills: frozenset[str]) -> Domain:
        fields.unknown(KEYS)
        domain_id = fields.text("id")
        if domain_id and domain_id != folder.name:
            fields.problem("id", f"id is {domain_id} but the folder is {folder.name}; make them the same")
        skills = fields.listed("skills")
        for skill in skills:
            if skill not in known_skills:
                fields.problem("skills", f'"{skill}" is not the id of a skill; list the name of a skill folder')
        models = self.models.read(fields, False)
        return Domain(domain_id, fields.text("title"), fields.text("description"), fields.text("outcome"), fields.texts("responsible"), fields.texts("not_responsible"), fields.listed("roles"), skills, models,
                      self.guidance(fields, folder), self.edges.read(fields), self.routing(fields))

    @staticmethod
    def guidance(fields: TomlFields, folder: Path) -> str:
        named = fields.data.get("guidance", GUIDANCE)
        path = folder / named if isinstance(named, str) else folder / GUIDANCE
        if not path.is_file():
            fields.problem("guidance", f"the guidance file {named} does not exist beside domain.toml")
            return ""
        return path.read_text(encoding="utf-8")

    @staticmethod
    def routing(fields: TomlFields) -> tuple[RoutingRule, ...]:
        rules = []
        for table in fields.tables("routing"):
            when, role, then = table.text("when"), table.text("role"), table.listed("then") if "then" in table.data else ()
            table.unknown(("when", "role", "then"))
            fields.absorbed(table)
            rules.append(RoutingRule(when, role, then))
        return tuple(rules)
