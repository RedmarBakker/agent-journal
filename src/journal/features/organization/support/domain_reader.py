import tomllib
from pathlib import Path

from journal.features.organization.support.board_phases import BoardPhases
from journal.features.organization.support.contract_problem import ContractProblem
from journal.features.organization.support.definition_of_done import DefinitionOfDone
from journal.features.organization.support.domain import Domain
from journal.features.organization.support.edge_reader import EdgeReader
from journal.features.organization.support.evidence_requirement import EvidenceRequirement
from journal.features.organization.support.model_reader import ModelReader
from journal.features.organization.support.routing_rule import RoutingRule
from journal.features.organization.support.toml_fields import TomlFields
from journal.models.board_phase import BoardPhase

KEYS = ("id", "title", "icon", "description", "outcome", "responsible", "not_responsible", "roles", "skills", "model", "guidance", "edges", "routing", "board", "definition_of_done")
GUIDANCE = "AGENTS.md"
PHASES = tuple(phase.value for phase in BoardPhase)


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
        return Domain(domain_id, fields.text("title"), fields.text("icon"), fields.text("description"), fields.text("outcome"), fields.texts("responsible"), fields.texts("not_responsible"), fields.listed("roles"), skills, models,
                      self.guidance(fields, folder), self.edges.read(fields), self.routing(fields), self.board(fields), self.definition_of_done(fields))

    @staticmethod
    def definition_of_done(fields: TomlFields) -> DefinitionOfDone | None:
        if "definition_of_done" not in fields.data:
            return None
        table = fields.table("definition_of_done")
        table.unknown(("criterion", "evidence", "target"))
        criterion, evidence_name, target = table.text("criterion"), table.text("evidence"), table.text("target")
        try:
            evidence = EvidenceRequirement(evidence_name)
        except ValueError:
            table.problem("evidence", "must be production_deployment, published_output, verified_output or accepted_output")
            evidence = None
        if evidence == EvidenceRequirement.PRODUCTION_DEPLOYMENT and target != "production":
            table.problem("target", "production_deployment evidence must name the production environment")
        fields.absorbed(table)
        return DefinitionOfDone(criterion, evidence, target) if evidence is not None and not table.problems else None

    @staticmethod
    def guidance(fields: TomlFields, folder: Path) -> str:
        named = fields.data.get("guidance", GUIDANCE)
        path = folder / named if isinstance(named, str) else folder / GUIDANCE
        if not path.is_file():
            fields.problem("guidance", f"the guidance file {named} does not exist beside domain.toml")
            return ""
        return path.read_text(encoding="utf-8")

    @staticmethod
    def board(fields: TomlFields) -> BoardPhases:
        if "board" not in fields.data:
            return BoardPhases()
        table = fields.table("board")
        table.unknown(PHASES)
        named = {phase: table.text(phase) for phase in PHASES if phase in table.data}
        fields.absorbed(table)
        return BoardPhases(**named)

    @staticmethod
    def routing(fields: TomlFields) -> tuple[RoutingRule, ...]:
        rules = []
        for table in fields.tables("routing"):
            when, role, then = table.text("when"), table.text("role"), table.listed("then") if "then" in table.data else ()
            table.unknown(("when", "role", "then"))
            fields.absorbed(table)
            rules.append(RoutingRule(when, role, then))
        return tuple(rules)
