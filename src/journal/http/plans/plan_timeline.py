from journal.features.plans.support.plan_agents import PlanAgents
from journal.http.plans.timeline_moment import TimelineMoment
from journal.models.message import Message
from journal.models.plan import Plan
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.messages import Messages
from journal.repositories.plans import Plans
from journal.repositories.task_logs import TaskLogs


class PlanTimeline:
    """A plan's task events and Plan agent messages, oldest first."""

    def __init__(self, plans: Plans, task_logs: TaskLogs, messages: Messages, plan_agents: PlanAgents) -> None:
        self.plans, self.task_logs, self.messages, self.plan_agents = plans, task_logs, messages, plan_agents

    def build(self, plan: Plan) -> list[TimelineMoment]:
        moments = [moment for task in self.plans.plan_tasks(plan) for moment in self.moments(task)]
        moments.extend(self.communications(plan))
        return sorted(moments, key=lambda m: m.time)

    def communications(self, plan: Plan) -> list[TimelineMoment]:
        environment = self.plan_agents.environment(plan)
        if environment is None:
            return []
        query = (
            self.messages.query()
            .filter(environment_id=environment.row_id)
            .filter_json("data->kind", Message.PEER)
            .filter_present("data->sent_to")
            .order("id")
        )
        rows = self.messages.selected_globally(query)
        return [
            TimelineMoment(
                message.creation_time.timestamp(),
                "refused_send" if message.data.get("failure") else "handoff",
                0,
                message.data[Message.RECIPIENT_KEY],
                message.text,
                message.data.get("address", ""),
                message.data.get("failure", ""),
            )
            for message in rows
        ]

    def moments(self, task: Task) -> list[TimelineMoment]:
        rows = [TimelineMoment(log.creation_time.timestamp(), "log", task.row_id, task.title, log.line) for log in self.task_logs.logs(task)]
        if task.started_at:
            rows.append(TimelineMoment(task.started_at.timestamp(), "started", task.row_id, task.title))
        if task.completed_at:
            rows.append(TimelineMoment(task.completed_at.timestamp(), "done" if task.state == TaskState.COMPLETED else "ended", task.row_id, task.title, task.outcome))
        return rows
