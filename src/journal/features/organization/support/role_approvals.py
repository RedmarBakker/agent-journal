from datetime import timedelta

from journal.features.organization.support.approval_action import ApprovalAction
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

APPROVAL_TTL = timedelta(hours=1)
APPROVE_ANSWER = "the user approves this action"
REFUSE_ANSWER = "the user refuses this action"


class RoleApprovals:
    """Creates the user's question for a Role action and spends an approval on its first authorized call."""

    def __init__(self, approvals: Approvals, questions: Questions, answering: AnswerDelivery, agents: Agents, tasks: Tasks, scope: Scope, time_source: TimeSource) -> None:
        self.approvals, self.questions, self.answering, self.agents, self.tasks, self.scope, self.time_source = approvals, questions, answering, agents, tasks, scope, time_source

    def request(self, worker: Worker, action: ApprovalAction) -> Approval | None:
        task_id = self.current_task(worker)
        if task_id is None:
            return None
        actor = Actor.agent(worker.session)
        current = self.approvals.for_action(actor.stamp, worker.role, task_id, action.value)
        now = self.time_source.moment()
        if current:
            current = self.refreshed(current)
        if current and self.keeps(current, now):
            return current
        environment_id = self.request_environment(worker)
        text = f"Approve {action.replace('_', ' ')} for Role {worker.role}, task {task_id}?"
        with self.scope.environment(environment_id):
            question = self.questions.save(Question(text=text, options=(APPROVE_ANSWER, REFUSE_ANSWER)), actor)
            question = self.questions.save(question.posed(now.timestamp()), actor)
        return self.approvals.save(Approval(environment_id=environment_id, actor=actor.stamp, role=worker.role, plan_id=worker.plan_id, task_id=task_id,
                                            action=action, question_id=question.row_id, question_environment_id=environment_id, expires_at=now + APPROVAL_TTL), actor)

    def authorizes(self, session: str, worker: Worker, action: ApprovalAction) -> bool:
        task_id = self.current_task(worker)
        if task_id is None:
            return False
        actor = Actor.agent(session)
        with self.approvals.writing():
            approval = self.approvals.for_action(actor.stamp, worker.role, task_id, action.value)
            if approval is None:
                return False
            approval = self.refreshed(approval)
            now = self.time_source.moment()
            if not approval.permits(now):
                return False
            self.approvals.save(approval.used(now), actor)
            return True

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
