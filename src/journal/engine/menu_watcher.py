import time

from journal.engine.job import Job
from journal.events.announcer import Announcer
from journal.events.moments.menu_answered import MenuAnswered
from journal.models.agent import Agent
from journal.providers.support.menu import ESCAPE, Menu
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.supervisor_link import SupervisorLink
from journal.engine.support.launch_files import LaunchFiles
from journal.engine.support.menu_answers import MenuAnswers
from journal.support.timeout import Timeout

STILLNESS_SECONDS = 1.5
CAUSE_WINDOW_SECONDS = 15.0
USER_KEY_WINDOW_SECONDS = 3.0


class MenuWatcher(Job):
    """A job that reads, twice a second, each live agent's screen through the supervisor's mirror and keeps the agent from sitting at a menu: one the journal caused is confirmed, the trust question for the launched folder accepted, a program's review of the hooks the journal wrote answered by trusting them, anything else declined or closed with Escape, and a card in the chat says what was done; a menu the user opened at the keyboard is left alone. A menu is answered at the first look when the screen has stood still, otherwise at the next look that finds the same menu, whatever a spinner above it does."""

    interval_seconds = 0.5

    def __init__(self, agents: Agents, supervisor: SupervisorLink, announcer: Announcer, scope: Scope, answers: MenuAnswers, launches: LaunchFiles) -> None:
        self.agents, self.supervisor, self.announcer, self.scope = agents, supervisor, announcer, scope
        self.answers, self.launches = answers, launches
        self._menu_signatures: dict[int, tuple] = {}
        self._menu_changed_at: dict[int, float] = {}
        self._answered: dict[int, tuple] = {}

    def tick(self, time: float) -> None:
        for agent in self.agents.active_main_agents():
            with self.scope.environment(agent.environment_id):
                self.check(agent)

    def check(self, agent: Agent) -> str:
        environment, moment = agent.environment_id, time.time()
        menu = Menu.parsed(self.supervisor.screen(environment)[-8192:])
        if menu is None or not (menu.foreign() or self.answers_permission(menu, environment)):
            self._menu_signatures.pop(environment, None)
            self._answered.pop(environment, None)
            return ""
        if self._menu_signatures.get(environment) != menu.signature():
            self._menu_signatures[environment], self._menu_changed_at[environment] = menu.signature(), moment
        if self._answered.get(environment) == menu.signature() or self.is_drawing(environment, moment):
            return ""
        user_owned = not Timeout.seconds(USER_KEY_WINDOW_SECONDS).started(self.supervisor.last_keystroke(environment)).is_elapsed(self._menu_changed_at[environment])
        if user_owned and not menu.confirming():
            return ""
        triggered = user_owned or not Timeout.seconds(CAUSE_WINDOW_SECONDS).started(self.supervisor.last_selection(environment)).is_elapsed(self._menu_changed_at[environment])
        decided = self.decided(menu, triggered, agent)
        if decided is None:
            return ""
        keys, line_text = decided
        self.supervisor.keys(environment, keys)
        if triggered:
            self.supervisor.confirmed(environment)
        self._answered[environment] = menu.signature()
        self.announcer.announce(MenuAnswered(environment_id=environment, session=agent.session, question=menu.question, done=line_text))
        return keys

    def answers_permission(self, menu: Menu, environment: int) -> bool:
        return menu.asking_permission() and self.launches.skips_prompts(environment)

    def is_drawing(self, environment: int, moment: float) -> bool:
        return self._menu_changed_at[environment] == moment and moment - self.supervisor.last_screen_change(environment) < STILLNESS_SECONDS

    def decided(self, menu: Menu, triggered: bool, agent: Agent) -> tuple[str, str] | None:
        trust_all = menu.trusting_all() if menu.reviewing_hooks() else None
        if trust_all is not None:
            return menu.keys(trust_all), f'chose "{trust_all.label}", since the hooks it reviews are the ones the journal wrote for this launch'
        if triggered or menu.trusting() or menu.switching_model():
            claimed = menu.accepting()
            return menu.keys(claimed), f'chose "{claimed.label}", since it confirms what was asked for' if triggered else f'chose "{claimed.label}"'
        if self.answers_permission(menu, agent.environment_id):
            claimed = menu.accepting()
            return menu.keys(claimed), f'chose "{claimed.label}", since the launch skips the permission prompts'
        answer = self.answers.stored_answer(menu) or menu.declining() or self.answers.query(menu, agent)
        if answer is None and self.answers.is_asking(menu):
            return None
        answer = answer or self.answers.query(menu, agent)
        if answer:
            return menu.keys(answer), f'chose "{answer.label}"'
        return ESCAPE, "closed it with Escape, since even an asked agent could not say what it was for"
