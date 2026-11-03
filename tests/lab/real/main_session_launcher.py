import sys
from pathlib import Path


def main() -> int:
    root, provider, supervisor_socket = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    sys.path.insert(0, str(root / "src"))
    from journal.launcher.launch import Launch

    initial = Launch.parse([provider], root)
    launch = Launch.parse([provider, *initial.provider.prompt_flags, *sys.argv[4:],
                           "--env", "main", "--no-open", "--no-journal"], root)
    object.__setattr__(launch, "socket", lambda _environment: supervisor_socket)
    return launch.run()


if __name__ == "__main__":
    raise SystemExit(main())
