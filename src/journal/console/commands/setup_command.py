import os
import shutil
from argparse import Namespace
from pathlib import Path

from journal.config import Config
from journal.console.command import Command
from journal.console.support.project_update_commit import ProjectUpdateCommit
from journal.features.plugins.support.plugin_skills import PluginSkills
from journal.features.profiles.support.profile_files import ProfileFiles
from journal.features.shell.support.restart_queue import RestartQueue
from journal.features.shell.support.shell_request import OUTPUT_FOLDER_VARIABLE
from journal.features.skills.support.skill_files import SkillFiles
from journal.launcher.dispatcher import Dispatcher
from journal.models.command_output import CommandOutput
from journal.models.environment import Environment
from journal.providers.provider import HOOK_SCRIPT
from journal.providers.providers import Providers
from journal.repositories.environments import Environments
from journal.support.caller import Caller
from journal.support.law_text import LawText
from journal.supervisor_link import SupervisorLink
from journal.support.project_command import ProjectCommand

# what the project's .gitignore keeps out of git, each with the spellings that already do: the journal's folder, and the
# agent's settings of this machine, which hold the journal's hooks with this machine's paths
IGNORED_PATHS = (("/.journal", ".journal", ".journal/"), ("/.claude/settings.local.json", ".claude/settings.local.json"))


class SetupCommand(Command):
    """journal setup: everything a project needs to run under the journal, idempotently."""

    noun = "setup"
    default_verb = "project"

    def __init__(self, config: Config, providers: Providers, files: SkillFiles, plugin_skills: PluginSkills, profiles: ProfileFiles, environments: Environments, supervisor: SupervisorLink, queue: RestartQueue, update_commit: ProjectUpdateCommit) -> None:
        self.config, self.providers, self.files, self.plugin_skills, self.profiles, self.environments, self.supervisor, self.queue, self.update_commit = config, providers, files, plugin_skills, profiles, environments, supervisor, queue, update_commit

    def arguments(self, verbs) -> None:
        self.verb(verbs, "project", "wire the hooks, write the skills and the law, put journal on the path; what journal setup does alone")
        self.verb(verbs, "hooks", "wire the hooks only")
        self.verb(verbs, "restart", "restart the running journals on the installed code; the agents keep running")

    def project(self, args: Namespace, caller: Caller) -> int:
        self.config.home.mkdir(parents=True, exist_ok=True)
        update_files = [*self.files.managed_paths(), *self.profiles.managed_paths(), *self.project_hooks(args, caller)]
        skills = self.files.write_all()
        update_files.extend(skills)
        for path in skills:
            print(f"skill   {path.relative_to(self.config.root)}")
        self.plugin_skills.refresh_all()
        profiles = self.profiles.write_all()
        update_files.extend(profiles)
        for path in profiles:
            print(f"profile {path.relative_to(self.config.root)}")
        law_path = self.config.root / "AGENTS.md"
        law_before = self.file_state(law_path)
        law = self.law()
        imports_path = self.config.root / "CLAUDE.md"
        imports_before = self.file_state(imports_path)
        imports = self.claude_md()
        ignored_path = self.config.root / ".gitignore"
        ignored_before = self.file_state(ignored_path)
        ignored = self.ignored()
        update_files.extend(path for path, before in ((law, law_before), (imports, imports_before), (ignored, ignored_before)) if self.file_state(path) != before)
        print(f"law     {law.relative_to(self.config.root)}")
        print(f"imports {imports.relative_to(self.config.root)}")
        print(f"command {self.shim()}")
        dispatcher = Dispatcher(Path.home())
        if dispatcher.is_writable():
            print(f"journal {dispatcher.write()}")
        print(f"ignored {ignored.relative_to(self.config.root)}")
        release = os.environ.get("JOURNAL_UPDATE_REF", "")
        managed_text = {law: LawText.installed, imports: self.claude_md_text, ignored: self.ignored_text}
        for provider in self.providers.all():
            for counterpart in provider.foreign_settings:
                managed_text[self.config.root / provider.home / counterpart] = provider.unwired_text
        committed = self.update_commit.commit(update_files, release, managed_text)
        if committed:
            print(f"update commit: {self.update_commit.message(release)} ({', '.join(committed)})")
        for line in self.restarted():
            print(line)
        return 0

    def restart(self, args: Namespace, caller: Caller) -> int:
        lines = self.restarted()
        for line in lines:
            print(line)
        if not lines:
            print("no journal is running")
        return 0

    def restarted(self) -> list[str]:
        asking_folder = os.environ.get(OUTPUT_FOLDER_VARIABLE, "")
        return [self.restart_line(environment, self.queue.restart(environment.row_id, asking_folder)) for environment in self.supervisor.running(self.environments.all())]

    @staticmethod
    def restart_line(environment: Environment, outputs: list[CommandOutput]) -> str:
        if not outputs:
            return f"restart {environment.name}: the journal of that environment runs the new code"
        numbers = ", ".join(str(output.id) for output in outputs)
        return f"restart {environment.name} waits: outputs {numbers} still run, and the restart starts by itself once the last of them ends. check each with journal output status, whether it is still working and why, and end any that is stuck"

    def hooks(self, args: Namespace, caller: Caller) -> int:
        self.project_hooks(args, caller)
        return 0

    def project_hooks(self, args: Namespace, caller: Caller) -> list[Path]:
        paths = []
        for provider in self.providers.all():
            if not provider.default and not (self.config.root / provider.home).is_dir() and not shutil.which(provider.name):
                continue
            for counterpart in provider.foreign_settings:
                path = self.config.root / provider.home / counterpart
                if path.is_file() and provider.has_journal_hooks(path):
                    paths.append(path)
            command = provider.hook_command(self.config.root)
            previous = self.file_state(self.config.root / provider.home / provider.settings_file)
            path = provider.wire_hooks(self.config.root, HOOK_SCRIPT, command)
            if self.file_state(path) != previous:
                paths.append(path)
            print(f"hooks   {path.relative_to(self.config.root)}")
        return paths

    @staticmethod
    def file_state(path: Path) -> bytes | None:
        return path.read_bytes() if path.is_file() else None

    def law(self) -> Path:
        path = self.config.root / "AGENTS.md"
        prior = path.read_text() if path.is_file() else "# " + self.config.root.name + "\n"
        saved = LawText.installed(prior)
        if saved != prior:
            path.write_text(saved)
        return path

    def claude_md(self) -> Path:
        path = self.config.root / "CLAUDE.md"
        prior = path.read_text() if path.is_file() else ""
        saved = self.claude_md_text(prior)
        if saved != prior:
            path.write_text(saved)
        return path

    @staticmethod
    def claude_md_text(prior: str) -> str:
        if "@AGENTS.md" in prior:
            return prior
        return (prior.rstrip("\n") + "\n\n" if prior.strip() else "") + "@AGENTS.md\n"

    def ignored(self) -> Path:
        path = self.config.root / ".gitignore"
        prior = path.read_text() if path.is_file() else ""
        saved = self.ignored_text(prior)
        if saved != prior:
            path.write_text(saved)
        return path

    @staticmethod
    def ignored_text(prior: str) -> str:
        missing = [spellings[0] for spellings in IGNORED_PATHS if not set(spellings) & set(prior.splitlines())]
        return (prior.rstrip("\n") + "\n" if prior.strip() else "") + "".join(f"{entry}\n" for entry in missing) if missing else prior

    def shim(self) -> Path:
        return ProjectCommand(self.config.root, self.package.parent / "journal.sh").write()

    @property
    def package(self) -> Path:
        return Path(__file__).resolve().parents[2]
