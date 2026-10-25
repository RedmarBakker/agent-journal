import os
import subprocess

FALLBACK = ("/usr/local/bin", "/opt/homebrew/bin", "/usr/bin", "/bin")
START_MARK = "journal-path-start:"
END_MARK = ":journal-path-end"
ASK_SECONDS = 10


class LoginPath:
    """The PATH the user's login shell has, read once from it, so a tool installed by nvm, Homebrew or asdf is found by the processes the journal starts; the usual folders when the shell gives none."""

    def __init__(self) -> None:
        self.kept: str | None = None

    def value(self) -> str:
        if self.kept is None:
            self.kept = self.asked() or os.pathsep.join(FALLBACK)
        return self.kept

    @staticmethod
    def asked() -> str:
        shell = os.environ.get("SHELL", "/bin/sh")
        try:
            done = subprocess.run([shell, "-l", "-i", "-c", f'printf "%s" "{START_MARK}$PATH{END_MARK}"'], capture_output=True, text=True, timeout=ASK_SECONDS, stdin=subprocess.DEVNULL)
        except (subprocess.TimeoutExpired, OSError):
            return ""
        start, end = done.stdout.rfind(START_MARK), done.stdout.rfind(END_MARK)
        return done.stdout[start + len(START_MARK):end] if 0 <= start < end else ""
