from urllib.request import Request as HttpRequest, urlopen

from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope


class ShellSteps:
    """A shell command the agent runs through the journal's runner, as its shell prefix sends it, and the number of the output it left."""

    def agent_runs_a_command(self, line: str) -> int:
        raw = f"JOURNAL_ENV=main\0\0{line}\n"
        request = HttpRequest(f"http://127.0.0.1:{self.app.server().port}/shell/run", data=raw.encode(), method="POST", headers={"Content-Type": "application/octet-stream", "X-Journal-Env": "main", "X-Journal-Cwd": str(self.app.config.root), "X-Journal-Shell": "sh"})
        urlopen(request, timeout=30).read()
        self.observed(f"agent runs a command {line.split()[0]}", None, None)
        with self.app.container.get(Scope).environment(1):
            outputs = self.app.container.get(CommandOutputs)
            return outputs.selected(outputs.query().order_descending("id").limit(1))[0].row_id
