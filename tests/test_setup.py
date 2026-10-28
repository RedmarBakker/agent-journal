"""journal setup wires a project: hooks for Claude, the skills, the law in AGENTS.md, the import in CLAUDE.md. Real files in a temp root; the command lands inside the project."""

import json
from pathlib import Path

import pytest

from journal.app import App
from journal.config import Config
from journal.console.commands.setup_command import SetupCommand
from journal.providers.provider import HOOK_SCRIPT
from journal.support.caller import Caller
from tests.main_journal import main_journal


@pytest.fixture
def app(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    (tmp_path / "home" / ".local" / "bin").mkdir(parents=True)
    return main_journal(Config(tmp_path, port=0))






def test_a_command_from_inside_an_agent_is_the_live_agents(app: App):
    import json as js
    from urllib.request import Request as HttpRequest, urlopen
    from journal.support.actor import Actor
    from journal.repositories.tasks import Tasks
    app.runtime().start()
    try:
        port = app.server().port
        hook = js.dumps({"hook_event_name": "SessionStart", "session_id": "live-1"}).encode()
        urlopen(HttpRequest(f"http://127.0.0.1:{port}/hooks/claude", data=hook, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main"}), timeout=5).read()
        body = js.dumps({"argv": ["task", "create", "from inside"], "env": "main", "session": "", "agent": True}).encode()
        urlopen(HttpRequest(f"http://127.0.0.1:{port}/cli", data=body, method="POST", headers={"Content-Type": "application/json", "X-Journal-Env": "main"}), timeout=5).read()
        assert app.container.get(Tasks).find(1).creator == Actor.agent("live-1")
    finally:
        app.runtime().stop()


def test_each_hooks_ready_state_is_read_from_the_projects_settings_and_codexs_trust(app: App, monkeypatch):
    from journal.providers.claude import Claude
    from journal.providers.codex import Codex
    from journal.providers.support.hooks_ready import HooksReady
    monkeypatch.delenv("CODEX_HOME", raising=False)
    root = app.config.root
    (root / ".codex").mkdir()
    assert Codex().hooks_ready(root) == HooksReady.UNWIRED and Claude().hooks_ready(root) == HooksReady.UNWIRED, "no journal hook in the settings: not wired"
    for provider in (Claude(), Codex()):
        provider.wire_hooks(root, HOOK_SCRIPT, provider.hook_command(root))
    assert Claude().hooks_ready(root) == HooksReady.READY, "Claude Code runs a project's hooks with no trust step of its own"
    assert Codex().hooks_ready(root) == HooksReady.UNTRUSTED, "wired, but Codex was never asked to trust them"
    hooks = root.resolve() / ".codex" / "hooks.json"
    tables = lambda kinds: "".join(f'[hooks.state."{hooks}:{type_name}:0:0"]\ntrusted_hash = "x"\n\n' for type_name in kinds)
    (root / "home" / ".codex").mkdir(parents=True)
    (root / "home" / ".codex" / "config.toml").write_text(tables(["session_start", "stop"]))
    assert Codex().hooks_ready(root) == HooksReady.TRUST_OUTDATED, "trusted before the journal wired the hooks it has now"
    captured = Path(__file__).with_name("hook_bodies") / "codex_0.163.0_trust.toml"
    (root / "home" / ".codex" / "config.toml").write_text(captured.read_text().replace("/project/.codex/hooks.json", str(hooks)))
    assert Codex().hooks_ready(root) == HooksReady.READY, "the tables a real Codex 0.163.0 wrote when it trusted every hook"


def test_the_private_folder_keeps_keys_and_secrets_to_their_user_and_out_of_git(tmp_path, monkeypatch):
    import stat
    from journal.support.private_folder import SECRETS_VARIABLE, PrivateFolder
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.delenv(SECRETS_VARIABLE, raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    folder = PrivateFolder(tmp_path / "proj")
    keys, secrets = folder.keys_file(), folder.secrets()
    assert keys.parent == tmp_path / ".journal" / "keys" and secrets == tmp_path / ".config" / "agent-journal" / "secrets", "version 3's secrets folder, so its values open unchanged"
    assert not keys.parent.exists() and not secrets.exists(), "naming the folders makes nothing, so a read never writes into the home folder"
    for produced in (PrivateFolder.created(keys.parent), PrivateFolder.created(secrets)):
        assert stat.S_IMODE(produced.stat().st_mode) == 0o700 and (produced / ".gitignore").read_text() == "*\n"
    monkeypatch.setenv(SECRETS_VARIABLE, str(tmp_path / "moved"))
    assert folder.secrets() == tmp_path / "moved"




def test_a_provider_missing_an_answer_cannot_be_built_and_each_lists_what_the_viewer_may_offer():
    from journal.providers.claude import Claude
    from journal.providers.provider import Provider
    from journal.providers.providers import Providers
    from journal.providers.support.capability import Capability

    class Halfway(Provider):
        name = "halfway"

        def resume(self, session: str) -> tuple[str, ...]:
            return ("--resume", session)

    with pytest.raises(TypeError, match="abstract"):
        Halfway()
    assert {provider.name: provider.capabilities for provider in Providers().all()} == {"claude": frozenset(Capability), "codex": frozenset()}, "a change to what a provider can offer is seen here"


def test_mcp_servers_written_into_codexs_config_keep_its_other_tables(app: App):
    import tomllib
    from journal.features.mcp.support.provider_config import ProviderConfig
    from journal.models.mcp_server import McpServer
    from journal.repositories.mcp_servers import McpServers
    from journal.support.actor import Actor
    root = app.config.root
    (root / ".codex").mkdir()
    (root / ".codex" / "config.toml").write_text('model = "gpt-6"\n\n[mcp_servers.mine]\ncommand = "my-server"\n\n[profiles.fast]\nmodel = "gpt-6-mini"\n')
    servers = app.container.get(McpServers)
    servers.save(McpServer(name="browser", transport="stdio", command="npx", args=("browser-mcp",)), Actor.system())
    gone = servers.save(McpServer(name="search", transport="http", url="https://search.test/mcp"), Actor.system())
    app.container.get(ProviderConfig).write()
    written = tomllib.loads((root / ".codex" / "config.toml").read_text())
    assert written["model"] == "gpt-6" and written["profiles"] == {"fast": {"model": "gpt-6-mini"}}, "the user's own settings stay"
    assert set(written["mcp_servers"]) == {"mine", "browser", "search"} and written["mcp_servers"]["browser"]["command"] == "npx"
    servers.delete(gone, Actor.system())
    app.container.get(ProviderConfig).write()
    assert set(tomllib.loads((root / ".codex" / "config.toml").read_text())["mcp_servers"]) == {"mine", "browser"}, "a server the journal took out goes, the user's own stays"
    assert set(json.loads((root / ".mcp.json").read_text())["mcpServers"]) == {"browser"}


def test_an_agents_row_offers_only_what_its_program_reports(app: App, monkeypatch):
    from journal.config import Config
    from journal.http.agents.agent_activity import AgentActivity
    from journal.models.agent import Agent
    from journal.repositories.agents import Agents
    from journal.support.actor import Actor
    from journal.repositories.scope import Scope
    monkeypatch.setattr(Config, "status_home", property(lambda self: self.root / "status"))
    (app.config.root / "status").mkdir()
    (app.config.root / "status" / "claude-1.json").write_text(json.dumps({"context_window": {"used_percentage": 42}, "model": {"display_name": "Opus 5.5"}, "rate_limits": {"five_hour": {"used_percentage": 10, "resets_at": 99}}}))
    agents = app.container.get(Agents)
    with app.container.get(Scope).environment(1):
        for session, provider in (("claude-1", "claude"), ("codex-1", "codex")):
            agents.save(Agent(environment_id=1, session=session, provider=provider), Actor.system())
        rows = {row["session"]: row for row in app.container.get(AgentActivity).page(agents.scoped())}
    assert rows["claude-1"]["context"] == 42 and rows["claude-1"]["model"] == "Opus 5.5" and rows["claude-1"]["usage"] == [{"key": "five_hour", "label": "5h", "used": 10, "resets_at": 99}]
    assert "context status" in rows["claude-1"]["capabilities"] and rows["codex-1"]["capabilities"] == []
    assert rows["codex-1"]["context"] is None and rows["codex-1"]["model"] == "", "a context Codex never reported is unknown, never zero"
