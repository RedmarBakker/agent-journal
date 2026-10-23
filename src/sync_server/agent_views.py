import threading

from sync_server.agent_view import AgentView
from sync_server.agent_view_list import AgentViewList
from sync_server.agent_view_post import AgentViewPost
from sync_server.devices import Devices

VIEW_LIFETIME_SECONDS = 60


class AgentViews:
    """The latest agent bar rows each host sent for its environments, held in memory and never stored: any device of the team reads them by environment key, and a view its host stopped sending for VIEW_LIFETIME_SECONDS is no longer handed out, so a host that went offline shows no agent."""

    def __init__(self, devices: Devices) -> None:
        self.devices = devices
        self.lock = threading.Lock()
        self.views_by_key: dict[str, AgentView] = {}

    def posted(self, token: str, request: AgentViewPost, request_at: float) -> AgentViewList:
        self.devices.device(token)
        with self.lock:
            self.views_by_key.update({key: AgentView(rows, request_at) for key, rows in request.views.items()})
        return AgentViewList(views={})

    def listed(self, token: str, keys: list[str], request_at: float) -> AgentViewList:
        self.devices.device(token)
        with self.lock:
            return AgentViewList(views={key: stored.rows for key in keys if (stored := self.views_by_key.get(key)) and request_at - stored.updated_at < VIEW_LIFETIME_SECONDS})
