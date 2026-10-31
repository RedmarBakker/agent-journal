import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def arguments() -> tuple[Path, list[str]]:
    received = list(sys.argv[1:])
    if "--root" not in received:
        return ROOT, received
    index = received.index("--root")
    root = Path(received.pop(index + 1))
    received.pop(index)
    return root, received


def checker():
    sys.path.insert(0, str(ROOT / "src"))
    from journal.support.viewer_built import digest, problems

    return digest, problems


if __name__ == "__main__":
    root, received = arguments()
    web = root / "src" / "web"
    digest, problems = checker()
    if received == ["--digest"]:
        print(digest(web))
        sys.exit(0)
    text = problems(web)
    print("\n".join(text) if text else "the viewer's bundle was built from its sources as they are")
    sys.exit(1 if text else 0)
