import resource
import sys
from pathlib import Path

from supervisor.bad_launch_file import BadLaunchFile
from supervisor.launch_file import LaunchFile
from supervisor.supervisor import ENDED

# a process macOS starts at login may hold 256 open files at most, too few for the journal and the test runs it starts; the
# supervisor raises it for itself and every process it runs, up to this or the system's own ceiling
OPEN_FILES = 10240


def raise_open_file_limit() -> None:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    wanted = OPEN_FILES if hard == resource.RLIM_INFINITY else min(OPEN_FILES, hard)
    if soft < wanted:
        resource.setrlimit(resource.RLIMIT_NOFILE, (wanted, hard))


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python3 -m supervisor <launch file>", file=sys.stderr)
        return ENDED
    try:
        launch = LaunchFile.read(Path(argv[0]))
    except BadLaunchFile as bad:
        print(bad, file=sys.stderr)
        return ENDED
    raise_open_file_limit()
    return launch.supervisor().run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
