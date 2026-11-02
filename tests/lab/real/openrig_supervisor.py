import subprocess
import sys
import time
from pathlib import Path


def run(rig: str, home: Path, port: str, database: str) -> int:
    start = subprocess.run(
        [rig, "daemon", "start", "--host", "127.0.0.1", "--port", port, "--db", database, "--no-kernel"],
        capture_output=True, text=True, check=False,
    )
    sys.stdout.write(start.stdout)
    sys.stderr.write(start.stderr)
    if start.returncode:
        return start.returncode
    (home / "start-confirmed").write_text("started\n", encoding="utf-8")
    while not (home / "stop-requested").exists():
        time.sleep(0.1)
    stop = subprocess.run([rig, "daemon", "stop"], capture_output=True, text=True, check=False)
    sys.stdout.write(stop.stdout)
    sys.stderr.write(stop.stderr)
    if stop.returncode:
        return stop.returncode
    (home / "stop-confirmed").write_text("stopped\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1], Path(sys.argv[2]), sys.argv[3], sys.argv[4]))
