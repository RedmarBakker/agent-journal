from pathlib import Path

from journal.features.organization.support.contract_folder import ContractFolder
from journal.features.skills.support.skill_files import SkillFiles

SKILL_FILE = "SKILL.md"
ROOT_SKILLS = "skills"


class SkillIds:
    """The skill ids a contract may list: the name of every folder under the organization folder, or the workspace's skills folder beside it, that holds a SKILL.md, and the journal's own skills."""

    def __init__(self, folder: ContractFolder, files: SkillFiles) -> None:
        self.folder, self.files = folder, files

    def known(self, path: Path) -> frozenset[str]:
        return frozenset((*self.folders(path), *(skill.name for skill in self.files.catalogue())))

    def folders(self, path: Path) -> dict[str, Path]:
        named = self.folder.named()
        return {file.parent.name: file.parent for root in (path, named.parent / ROOT_SKILLS) if root.is_dir() for file in root.rglob(SKILL_FILE)}
