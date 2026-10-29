from journal.models.agent_role import AgentRole
from journal.support.actor_type import ActorType
from journal.support.hook_type import HookType


class AnswerReturn:
    def __init__(self, sessions, machine) -> None:
        self.sessions, self.machine = sessions, machine

    def decision(self, event, agent, reply):
        # @sin SessionPurityRoleCheckedDetector
        if agent.role.is_helper():
            return self.machine.worker_decision(agent.row_id, reply.decision, event)
        return reply.decision

    def thread(self, agent):
        # @sin SessionPurityRoleCheckedDetector
        return "main" if agent.role == AgentRole.MAIN else "helper"

    def actor_number(self, actor):
        # @sin SessionPurityActorTypeCheckedDetector
        return actor.actor_type == ActorType.WORKER

    def worker_answer(self, caller):
        # @sin SessionPurityActorTypeCheckedDetector
        return caller.is_worker()

    def subagent_start(self, hook, environment):
        # @sin SessionPurityHookKindComparedDetector
        if hook.hook_type == HookType.SUBAGENT_START:
            self.machine.started(hook, environment)

    def tool_start(self, hook):
        # @sin SessionPurityHookKindComparedDetector
        return hook.is_pre_tool_use()

    def agent_row(self, event):
        # @sin SessionPurityAgentLookedUpAgainDetector
        return self.sessions.agent(event.session, event.environment_id, event.provider)

    def session_agent_row(self, agents, event):
        # @sin SessionPurityAgentLookedUpAgainDetector
        return agents.session_agent(event.session)


class AnswerReturnFixed:
    def __init__(self, machine) -> None:
        self.machine = machine

    def decision(self, event, reply):
        # @righteous SessionPurityRoleCheckedDetector
        return event.agent.floor().returned(reply.decision)

    def thread(self, agent):
        # @righteous SessionPurityRoleCheckedDetector
        return agent.thread

    def actor_number(self, actor):
        # @righteous SessionPurityActorTypeCheckedDetector
        return actor.number()

    def agent_row(self, event):
        # @righteous SessionPurityAgentLookedUpAgainDetector
        return event.agent

    def event_entries(self, entries, event):
        # @righteous SessionPurityHookKindComparedDetector
        return entries.session_kind_entries(type(event).__name__, event.session)
