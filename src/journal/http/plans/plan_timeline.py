from journal.engine.support.stack_history import StackHistory
from journal.features.plans.support.plan_agents import PlanAgents
from journal.http.plans.timeline_moment import TimelineMoment
from journal.models.message import Message
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.entries import Entries
from journal.repositories.messages import Messages
from journal.repositories.plans import Plans
from journal.repositories.task_logs import TaskLogs


class PlanTimeline:
    """A plan's task events and Plan agent history, oldest first."""

    def __init__(self, plans: Plans, task_logs: TaskLogs, messages: Messages, plan_agents: PlanAgents, entries: Entries) -> None:
        self.plans, self.task_logs, self.messages, self.plan_agents, self.entries = plans, task_logs, messages, plan_agents, entries

    def build(self, plan: Plan) -> list[TimelineMoment]:
        moments = [moment for task in self.plans.plan_tasks(plan) for moment in self.moments(task)]
        moments.extend(self.communications(plan))
        return sorted(moments, key=lambda m: m.time)

    def roles_taken(self, plan: Plan) -> dict:
        if plan.mode != PlanMode.SOLO:
            return {"current_role": "", "steps": []}
        agent, environment = self.plan_agents.agent(plan), self.plan_agents.environment(plan)
        if environment is None:
            return {"current_role": "", "steps": []}

        tasks = self.plans.plan_tasks(plan)
        steps = []
        for entry in self.entries.global_matching(environment_id=environment.row_id, entry_type=StackHistory.KIND):
            before = {
                (layer.get("data", {}).get("role"), layer.get("data", {}).get("version"))
                for layer in entry.data.get("before", [])
                if layer.get("state") == "role_work"
            }
            after = [layer for layer in entry.data.get("after", []) if layer.get("state") == "role_work"]
            for layer in after:
                data = layer.get("data", {})
                role = data.get("role", "")
                if not role or (role, data.get("version")) in before:
                    continue
                task = next(
                    (
                        task
                        for task in tasks
                        if task.started_at
                        and task.started_at <= entry.created_at
                        and (task.completed_at is None or entry.created_at <= task.completed_at)
                    ),
                    None,
                )
                steps.append({"role": role, "task": task.row_id if task else 0, "title": task.title if task else "", "time": entry.created_at.timestamp()})

        current_role = ""
        if agent:
            stack = agent.stack or ({"state": agent.state, "data": agent.data},)
            top = stack[-1]
            if top.get("state") == "role_work":
                current_role = top.get("data", {}).get("role", "")
        return {"current_role": current_role, "steps": steps}

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
            rows.append(TimelineMoment(task.completed_at.timestamp(), "done" if task.is_completed() else "ended", task.row_id, task.title, task.outcome))
        return rows
