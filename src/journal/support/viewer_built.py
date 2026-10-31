import hashlib
from pathlib import Path

SOURCES = ("src", "public", "index.html", "phone.html", "share.html", "package.json", "package-lock.json", "vite.config.js")


def digest(web: Path) -> str:
    hashed = hashlib.sha256()
    for name in SOURCES:
        top = web / name
        for path in sorted([top] if top.is_file() else (one for one in top.rglob("*") if one.is_file())):
            hashed.update(str(path.relative_to(web)).encode() + b"\0" + path.read_bytes() + b"\0")
    return hashed.hexdigest()


def problems(web: Path) -> list[str]:
    built_from = web / "dist" / "built-from"
    built = built_from.read_text().strip() if built_from.is_file() else ""
    if built == digest(web):
        return []
    return ["src/web/dist was not built from the viewer's sources as they are now: the build was forgotten or failed. "
            "Run npm --prefix src/web run build (after npm --prefix src/web install) and commit src/web/dist."]


def is_source_path(path: str) -> bool:
    return any(path == f"src/web/{name}" or path.startswith(f"src/web/{name}/") for name in SOURCES)
