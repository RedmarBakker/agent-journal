import json
import threading
import time

from journal.features.voices.support.voice_choice import VoiceChoice
from journal.http.agents.agent_activity import AgentActivity
from journal.http.agents.terminal_lines import TerminalLines
from journal.http.support.json_out import JsonOut
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.sync.hosts import Hosts
from journal.sync.team_account import TeamAccount
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink

CHECK_SECONDS = 2
RESEND_SECONDS = 30
FAULT_SECONDS = 60
TERMINAL_LINE_COUNT = 50


class AgentViewSender:
    """Sends the team server the agent bar rows of each environment this journal hosts, each with its agent's newest terminal lines and the voice its owner chose here, whose figure the hosted journal shows, other than the Team chat, while it is in a team, every time they change and again before the server's copy goes stale, so the owner on the hosted journal and a colleague see the agent as it is here; a fault waits a minute and is never the sync's."""

    def __init__(self, account: TeamAccount, hosts: Hosts, agents: Agents, activity: AgentActivity, terminal: TerminalLines, scope: Scope, link: TeamServerLink, voices: VoiceChoice) -> None:
        self.account, self.hosts, self.agents, self.activity, self.terminal, self.scope, self.link = account, hosts, agents, activity, terminal, scope, link
        self.voices = voices
        self.last_views: dict[str, list[dict]] = {}
        self.last_send_at = 0.0
        self.stopping = threading.Event()

    def start(self) -> None:
        self.stopping.clear()
        threading.Thread(target=self.run, name="agent-views", daemon=True).start()

    def stop(self) -> None:
        self.stopping.set()

    def run(self) -> None:
        while not self.stopping.is_set():
            try:
                self.check(time.time())
                self.stopping.wait(CHECK_SECONDS)
            except (OSError, TeamRefusal) as fault:
                print(f"the agent views could not be sent to the team server: {fault}", flush=True)
                self.stopping.wait(FAULT_SECONDS)

    def check(self, request_at: float) -> None:
        if self.account.is_joined():
            self.send(request_at)

    def send(self, request_at: float) -> None:
        views = self.views()
        if views == self.last_views and request_at - self.last_send_at < RESEND_SECONDS:
            return
        self.link.send_agent_views(views)
        self.last_views, self.last_send_at = views, request_at

    def views(self) -> dict[str, list[dict]]:
        return {environment.key: self.rows(environment.row_id) for environment in self.hosts.hosted_environments() if not environment.is_team_chat}

    def rows(self, environment_id: int) -> list[dict]:
        with self.scope.environment(environment_id):
            agent = self.agents.current()
            voice = self.voices.voice().name
            return json.loads(JsonOut.encoded([{**row, "terminal": self.terminal.lines(agent, 0.0)[-TERMINAL_LINE_COUNT:], "voice": voice} for row in self.activity.page([agent])])) if agent else []
