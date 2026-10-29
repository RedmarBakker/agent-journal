from dataclasses import dataclass
from datetime import timedelta

from journal.features.organization.support.approval_action import ApprovalAction
from journal.features.organization.support.approval_actions import ApprovalActions
from journal.features.organization.support.role import Role
from journal.features.questions.support.answer_delivery import AnswerDelivery
from journal.models.approval import Approval
from journal.models.question import Question
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.approvals import Approvals
from journal.repositories.agents import Agents
from journal.repositories.questions import Questions
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource
from journal.support.tool_call import ToolCall

APPROVAL_TTL = timedelta(hours=1)
APPROVE_ANSWER = "the user approves this action"
REFUSE_ANSWER = "the user refuses this action"


@dataclass(frozen=True)
class RoleApprovalContext:
    """The agent, Role, plan task and environment where the user's question belongs."""

    session: str
    role: str
    plan_id: int
    task_id: int
    question_environment_id: int


class RoleApprovals:
    """Creates an exact-call question and atomically spends its user approval once."""

    def __init__(self, approvals: Approvals, questions: Questions, answering: AnswerDelivery, agents: Agents, tasks: Tasks, scope: Scope, time_source: TimeSource) -> None:
        self.approvals, self.questions, self.answering, self.agents, self.tasks, self.scope, self.time_source = approvals, questions, answering, agents, tasks, scope, time_source

    def context_for_worker(self, session: str, worker: Worker) -> RoleApprovalContext | None:
        if worker.is_new or not worker.role:
            return None
        task_id = self.current_task(worker)
        if task_id is None:
            return None
        return RoleApprovalContext(session, worker.role, worker.plan_id, task_id, self.request_environment(worker))

    def authorizes_worker(self, session: str, worker: Worker, role: Role, call: ToolCall) -> bool:
        context = self.context_for_worker(session, worker)
        return self.authorizes(context, role, call) if context else False

    def authorizes(self, context: RoleApprovalContext, role: Role, call: ToolCall) -> bool:
        actions = tuple(action for action in ApprovalActions.of(call) if role.needs_approval(action))
        if context.role != role.id or len(actions) != 1:
            return False
        action = actions[0]
        request_hash, details = ApprovalActions.identity(call)
        actor = Actor.agent(context.session)
        with self.approvals.writing():
            approval = self.current_or_new(context, action, request_hash, details, actor)
            now = self.time_source.moment()
            if not approval.permits(now):
                return False
            self.approvals.save(approval.used(now), actor)
            return True

    def request(self, context: RoleApprovalContext, action: ApprovalAction, call: ToolCall) -> Approval | None:
        if ApprovalActions.of(call) != (action,):
            return None
        request_hash, details = ApprovalActions.identity(call)
        actor = Actor.agent(context.session)
        with self.approvals.writing():
            return self.current_or_new(context, action, request_hash, details, actor)

    def current_or_new(self, context: RoleApprovalContext, action: ApprovalAction, request_hash: str, details: str, actor: Actor) -> Approval:
        current = self.approvals.for_action(actor.stamp, context.role, context.plan_id, context.task_id, action.value, request_hash)
        now = self.time_source.moment()
        if current:
            current = self.refreshed(current)
            if self.keeps(current, now):
                return current
        text = (f"Approve {action.value.replace('_', ' ')} for Role {context.role}, task {context.task_id}, requested by {actor.stamp}?\n\n"
                f"Exact normalized request:\n{details}")
        with self.scope.environment(context.question_environment_id):
            question = self.questions.save(Question(text=text, options=(APPROVE_ANSWER, REFUSE_ANSWER)), actor)
            question = self.questions.save(question.posed(now.timestamp()), actor)
        return self.approvals.save(Approval(environment_id=context.question_environment_id, actor=actor.stamp, role=context.role, plan_id=context.plan_id, task_id=context.task_id,
                                            action=action, request_hash=request_hash, request_details=details, question_id=question.row_id,
                                            question_environment_id=context.question_environment_id, expires_at=now + APPROVAL_TTL), actor)

    def approve(self, approval: Approval, actor: Actor) -> Approval:
        return self.decide(approval, Approval.APPROVED, actor)

    def refuse(self, approval: Approval, actor: Actor) -> Approval:
        return self.decide(approval, Approval.REFUSED, actor)

    def decide(self, approval: Approval, decision: str, actor: Actor) -> Approval:
        if not actor.is_user():
            raise Rejection("only the user can decide a Role approval")
        with self.approvals.writing():
            approval = self.refreshed(self.approvals.find(approval.row_id))
            if approval.decision == decision:
                return approval
            if approval.decision != Approval.PENDING:
                raise Rejection(f"approval {approval.id} is already {approval.decision}")
            now = self.time_source.moment()
            if decision == Approval.APPROVED and (approval.expires_at is None or approval.expires_at <= now):
                raise Rejection(f"approval {approval.id} has expired")
            with self.scope.environment(approval.question_environment_id):
                question = self.questions.find(approval.question_id)
                if not question.is_answered():
                    self.answering.answer(question, APPROVE_ANSWER if decision == Approval.APPROVED else REFUSE_ANSWER, actor)
            return self.approvals.save(approval.decided(decision, now), actor)

    def refreshed(self, approval: Approval) -> Approval:
        if approval.decision != Approval.PENDING or not approval.question_id:
            return approval
        with self.scope.environment(approval.question_environment_id):
            question = self.questions.find(approval.question_id)
            now = self.time_source.moment()
            if not question.is_answered():
                if approval.expires_at is None or approval.expires_at > now:
                    return approval
                actor = Actor.system()
                self.answering.close(question, actor)
                return self.approvals.save(approval.decided(Approval.EXPIRED, now), actor)
        answer = question.answer.strip().lower() if question.answer else ""
        now = self.time_source.moment()
        user_answer = question.updater is not None and question.updater.is_user()
        decision = Approval.APPROVED if user_answer and (answer == APPROVE_ANSWER or answer in ("yes", "approve", "approved", "allow")) else Approval.REFUSED
        if decision == Approval.APPROVED and (approval.expires_at is None or approval.expires_at <= now):
            decision = Approval.EXPIRED
        return self.approvals.save(approval.decided(decision, question.updated_at or now), question.updater or Actor.system())

    def keeps(self, approval: Approval, now) -> bool:
        if approval.decision == Approval.REFUSED or approval.used_at is not None:
            return True
        return approval.expires_at is not None and approval.expires_at > now

    def request_environment(self, worker: Worker) -> int:
        dispatchers = self.agents.session_rows(worker.dispatcher) if worker.dispatcher else []
        return dispatchers[0].environment_id if dispatchers else worker.environment_id

    def current_task(self, worker: Worker) -> int | None:
        with self.scope.environment(worker.environment_id):
            task = self.tasks.holder_task(Ref.build(worker))
        return task.row_id if task else None
