import hashlib
from pathlib import Path

from journal.features.organization.support.contract_folder import ContractFolder
from journal.features.organization.support.contract_problem import ContractProblem
from journal.features.organization.support.contract_rules import ContractRules
from journal.features.organization.support.contracts import Contracts
from journal.features.organization.support.domain import Domain
from journal.features.organization.support.domain_reader import DomainReader
from journal.features.organization.support.role import Role
from journal.features.organization.support.role_reader import RoleReader
from journal.features.organization.support.revision_unreadable import RevisionUnreadable
from journal.features.organization.support.skill_ids import SkillIds

DOMAINS = "domains"
ROLES = "roles"
SOURCES = ("*.toml", "*.md")


class ContractReader:
    """Walks the organization folder and reads what it finds: domains/<domain>/domain.toml is a domain, domains/<domain>/roles/<role>/role.toml is a Role, and anything else, an empty Role folder included, is not read; a file that breaks a rule is left out whole and reported."""

    def __init__(self, folder: ContractFolder, domains: DomainReader, roles: RoleReader, rules: ContractRules, skills: SkillIds) -> None:
        self.folder, self.domains, self.roles, self.rules, self.skills = folder, domains, roles, rules, skills

    def read(self) -> Contracts:
        try:
            root = self.folder.path()
        except RevisionUnreadable as unreadable:
            return Contracts((), (), (ContractProblem(self.folder.version(), "version", str(unreadable)),), "")
        if root is None:
            return Contracts((), (), (), "")
        if not root.is_dir():
            return Contracts((), (), (ContractProblem(str(root), "folder", f"The organization folder {root} does not exist; set it on the Settings page"),), "")
        known, problems, domains, roles, present = self.skills.known(root), [], [], [], {}
        for folder in self.folders(root / DOMAINS):
            domain = self.domain(root, folder, known, problems)
            present[folder.name] = frozenset(role_folder.name for role_folder in self.role_folders(folder))
            if domain:
                domains.append(domain)
                roles += self.roles_of(root, folder, known, problems)
            elif present[folder.name]:
                problems.append(ContractProblem(self.relative(root, folder), "domain", f"domain {folder.name} has Roles but no readable domain.toml; its Roles are left out"))
        problems += self.rules.check(tuple(domains), tuple(roles), present)
        bad = {problem.path for problem in problems if problem.is_error()}
        return Contracts(tuple(domain for domain in domains if self.path_of(domain) not in bad), tuple(role for role in roles if self.rules.role_path(role) not in bad), tuple(problems), self.digest(root))

    def has_changed(self, read: Contracts) -> bool:
        root = self.folder.named()
        return bool(root and root.is_dir() and not self.folder.version() and self.digest(root) != read.version)

    def domain(self, root: Path, folder: Path, known: frozenset[str], problems: list[ContractProblem]) -> Domain | None:
        if not (folder / "domain.toml").is_file():
            return None
        domain, found = self.domains.read(folder, self.relative(root, folder), known)
        problems += found
        return domain

    def roles_of(self, root: Path, folder: Path, known: frozenset[str], problems: list[ContractProblem]) -> list[Role]:
        roles = []
        for role_folder in self.role_folders(folder):
            relative = self.relative(root, role_folder)
            if not (role_folder / "role.toml").is_file():
                problems.append(ContractProblem(relative, "role", f"{role_folder.name} has files but no role.toml; add it or remove the folder"))
                continue
            role, found = self.roles.read(role_folder, relative, folder.name, known)
            problems += found
            roles += [role] if role else []
        return roles

    @staticmethod
    def folders(path: Path) -> list[Path]:
        return sorted(folder for folder in path.iterdir() if folder.is_dir()) if path.is_dir() else []

    def role_folders(self, domain: Path) -> list[Path]:
        return [folder for folder in self.folders(domain / ROLES) if any(folder.iterdir())]

    @staticmethod
    def relative(root: Path, path: Path) -> str:
        return path.relative_to(root).as_posix()

    @staticmethod
    def path_of(domain: Domain) -> str:
        return f"domains/{domain.id}/domain.toml"

    @staticmethod
    def digest(root: Path) -> str:
        files = sorted(path for pattern in SOURCES for path in (root / DOMAINS).rglob(pattern))
        digest = hashlib.sha1()
        for path in files:
            digest.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
        return digest.hexdigest()[:12]
