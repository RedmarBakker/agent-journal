from journal.config import Config
from journal.events.agent.session_started import SessionStarted
from journal.events.agent_listener import AgentListener
from journal.repositories.environments import Environments
from journal.chat.moment_cards import MomentCards
from journal.support.actor import Actor
from journal.support.worktree import Worktree
from journal.support.card_type import CardType


class WorktreeSessionLink(AgentListener[SessionStarted]):
    """A session that starts in an environment with a worktree is marked in the chat with the worktree and its branch, once a session."""

    def __init__(self, config: Config, environments: Environments, cards: MomentCards) -> None:
        self.config, self.environments, self.cards = config, environments, cards

    def handle(self, event: SessionStarted) -> None:
        tree = Worktree(self.config.root, self.environments.find(event.environment_id).name)
        if not tree.path.is_dir() or self.cards.is_shown(f"worktree:{event.session}", Actor.system()):
            return
        self.cards.show(event.environment_id, event.session, f"Working on a separate copy of the project, branch {tree.current_branch()}", key=f"worktree:{event.session}", shows=CardType.WORKTREES)
