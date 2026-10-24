import argparse
from pathlib import Path

from journal.launcher.remote_install import INSTALLER
from journal.version import VERSION

WORKFLOW = Path(".github") / "workflows" / "agent-journal-server.yml"
RUNNER_LABEL = "agent-journal"
WORKFLOW_TEXT = """# Installs this project's team server, with its hosted journal, on your own server through a self-hosted GitHub runner
# installed there with the label {label}, so no SSH is needed. Run it from the Actions tab, Agent journal server, Run
# workflow; its log prints the server's URL and the one-time setup code that claims it. Written by journal remote github init.
name: Agent journal server

on:
  workflow_dispatch:
    inputs:
      address:
        description: "The address the team reaches the server at: a domain name or the server's IP address"
        required: true
      project:
        description: "The project name, which names the server's volume and container"
        required: true
        default: "{project}"
      version:
        description: "The agent-journal release to install"
        required: true
        default: "{version}"

jobs:
  install:
    runs-on: [self-hosted, {label}]
    steps:
      - name: Install the team server
        env:
          TEAM_PROJECT: ${{{{ inputs.project }}}}
          TEAM_ADDRESS: ${{{{ inputs.address }}}}
          TEAM_VERSION: ${{{{ inputs.version }}}}
        run: curl -fsSL "{installer}" | sh
"""
STEPS = """wrote {workflow}. Next:
  1. On your server, register a self-hosted runner for this repository with the label {label}: on GitHub, the
     repository's Settings, Actions, Runners, New self-hosted runner (Linux); run the commands it shows, adding
     --labels {label} to ./config.sh, then sudo ./svc.sh install and sudo ./svc.sh start so it keeps running.
  2. Commit and push {workflow}.
  3. In the repository's Actions tab, run Agent journal server with the server's address. Its log prints the URL and
     the setup code: claim the server at the URL with the code, or journal team join <url> --setup-code <code>."""


class RemoteGithub:
    """journal remote github init: writes into the project a GitHub Actions workflow that installs the team server, with its hosted journal, on the user's own server through a self-hosted runner there, so no SSH is needed, and says how to register the runner and run it."""

    def __init__(self, root: Path, replacing: bool) -> None:
        self.root, self.replacing = root, replacing

    @classmethod
    def parsed(cls, argv: list[str], root: Path) -> "RemoteGithub":
        parser = argparse.ArgumentParser(prog="journal remote github", description="install the team server on your own server through GitHub Actions, with no SSH")
        parser.add_argument("verb", choices=["init"])
        parser.add_argument("--replace", action="store_true", help="write the workflow again over one already there")
        args = parser.parse_args(argv)
        return cls(root, args.replace)

    def text(self) -> str:
        installer = INSTALLER.replace("{version}", "${TEAM_VERSION}")
        return WORKFLOW_TEXT.format(label=RUNNER_LABEL, project=self.root.name, version=VERSION, installer=installer)

    def run(self) -> int:
        target = self.root / WORKFLOW
        if target.exists() and not self.replacing:
            print(f"{WORKFLOW} is there already: journal remote github init --replace writes it again")
            return 1
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.text())
        print(STEPS.format(workflow=WORKFLOW, label=RUNNER_LABEL))
        return 0
