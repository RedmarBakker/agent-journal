from pathlib import Path, PurePosixPath

from journal.features.library.support.portable_body import PortableBody
from journal.support.rejection import Rejection

SKILL_FILE = "SKILL.md"


class SkillBody:
    """A skill as the library carries it: its folder's name and every text file under it by its path inside the folder, carried in the body as texts, since files names what the server stores apart; and back into the folder, refusing a path that would leave it."""

    @staticmethod
    def text(folder: Path) -> str:
        files = {str(path.relative_to(folder).as_posix()): path.read_text() for path in sorted(folder.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}
        if SKILL_FILE not in files:
            raise Rejection(f"{folder.name} has no {SKILL_FILE}, so it is no skill")
        return PortableBody.text({"name": folder.name, "texts": files})

    @staticmethod
    def files(body: str) -> dict[str, str]:
        files = {str(path): str(text) for path, text in PortableBody.fields(body)["texts"].items()}
        for path in files:
            parts = PurePosixPath(path).parts
            if PurePosixPath(path).is_absolute() or ".." in parts or not parts:
                raise Rejection(f"the skill holds a file outside its folder: {path}")
        return files

    @staticmethod
    def save(folder: Path, body: str) -> Path:
        for path, text in SkillBody.files(body).items():
            (folder / path).parent.mkdir(parents=True, exist_ok=True)
            (folder / path).write_text(text)
        return folder / SKILL_FILE
