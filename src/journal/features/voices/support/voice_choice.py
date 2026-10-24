import subprocess
import time

from journal.config import Config
from journal.features.voices.support.builtin_catalogue import BuiltinCatalogue
from journal.features.voices.support.voice import Voice
from journal.repositories.setting_rows import SettingRows
from journal.features.voices.voices_options import VoicesOptions


RECENCY_SECONDS = 60.0


class VoiceChoice:
    """The voice, title and first name the user chose, as settings on the project; the first name falls back to what git knows the user by."""

    def __init__(self, settings: SettingRows, config: Config) -> None:
        self.settings, self.config = settings, config
        self.git_name_read_at = 0.0
        self.last_git_name = ""

    def voice(self) -> Voice:
        return BuiltinCatalogue.lookup(str(self.settings.option(VoicesOptions.PROFILE)))

    def title(self) -> str:
        return str(self.settings.option(VoicesOptions.TITLE))

    def first_name(self) -> str:
        return str(self.settings.option(VoicesOptions.NAME) or self.git_name())

    def instruction(self) -> str:
        return self.voice().instruction(self.title(), self.first_name())

    def git_name(self) -> str:
        if time.monotonic() - self.git_name_read_at < RECENCY_SECONDS:
            return self.last_git_name
        self.last_git_name, self.git_name_read_at = self.git_user_first_name(), time.monotonic()
        return self.last_git_name

    def git_user_first_name(self) -> str:
        try:
            full = subprocess.run(["git", "config", "user.name"], cwd=self.config.root, capture_output=True, text=True, timeout=5).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return full.split(" ")[0] if full else ""
