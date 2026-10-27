from datetime import datetime, timezone

from journal.models.plan_state import PlanState
from journal.db.query import Query
from journal.features.plans.support.plan_testing import PlanTesting
from journal.features.plans.support.review_rounds import ReviewRounds
from journal.features.tasks.active_task import ActiveTask
from journal.http.controllers.controller import Controller
from journal.http.plans.plan_outline import PlanOutline
from journal.http.plans.plan_timeline import PlanTimeline
from journal.http.support.model_fields import ModelFields
from journal.http.support.request import Request
from journal.support.caller import Caller
from journal.support.response import Response
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.links import Links
from journal.repositories.messages import Messages
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.tasks import Tasks
from journal.support.time_source import TimeSource

CLOSED_PLAN_STATES = tuple(state for state in PlanState if state.is_closed())


class PlanController(Controller[Plan]):
    """Plans in outline, and the user's moves on one: review, approve, start, pause, finish and abandon, each answered with the plan's own fields, its outline read by id."""

    repository: Plans

    def __init__(self, plans: Plans, tasks: Tasks, links: Links, outline: PlanOutline, timeline: PlanTimeline, taking: ActiveTask, rounds: ReviewRounds, testing: PlanTesting, time_source: TimeSource, messages: Messages) -> None:
        self.time_source, self.messages = time_source, messages
        self.repository, self.tasks, self.links, self.outline, self.moments, self.taking, self.rounds = plans, tasks, links, outline, timeline, taking, rounds
        self.plan_testing = testing

    def open_rows(self, query: Query) -> Query:
        return query.filter_unlisted("state", CLOSED_PLAN_STATES)

    def closed_rows(self, query: Query) -> Query:
        return query.filter_listed("state", CLOSED_PLAN_STATES)

    def shown_page(self, rows: list[Plan]) -> list[dict]:
        return [self.outline.build(plan) for plan in rows]

    def index_page(self, rows: list[Plan]) -> list[dict]:
        phases, tasks = self.repository.phase_counts(rows), self.repository.task_counts(rows)
        return [{**ModelFields.build(plan), "phase_count": phases.get(plan.id, 0), "task_count": tasks.get(plan.id, 0)} for plan in rows]

    def timeline(self, request: Request) -> Response:
        return Response.json(self.moments.build(self.repository.find(request.number("id"))))

    def plan_tasks(self, request: Request) -> Response:
        return Response.json(self.repository.plan_tasks(self.repository.find(request.number("id"))))

    def add_task(self, request: Request) -> Response:
        plan = self.repository.find(request.number("id"))
        task = self.tasks.save(Task(environment_id=plan.environment_id, title=request.body.get("title", ""), brief=request.body.get("brief", "")), request.actor)
        self.links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), request.actor)
        return Response.json(task, 201)

    def review(self, request: Request) -> Response:
        return self.answered(self.rounds.begin(self.repository.find(request.number("id")), request.actor))

    def approve(self, request: Request) -> Response:
        return self.answered(self.repository.approve(self.repository.find(request.number("id")), request.actor, self.comment_id(request)))

    def comment_id(self, request: Request) -> int | None:
        key = request.body.get("comment_key")
        comments = self.messages.sent_with(str(key)) if key else []
        return comments[0].id if comments else None

    def start(self, request: Request) -> Response:
        return self.answered(self.repository.start(self.repository.find(request.number("id")), self.taking.holder(Caller.user(request.environment)), request.actor))

    def dismiss(self, request: Request) -> Response:
        return self.answered(self.repository.save(self.repository.find(request.number("id")).card_dismissed(), request.actor))

    def pause(self, request: Request) -> Response:
        return self.answered(self.repository.postpone(self.repository.find(request.number("id")), request.actor))

    def finish(self, request: Request) -> Response:
        return self.moved(request, lambda plan: plan.finished(self.time_source.moment().timestamp()))

    def testing(self, request: Request) -> Response:
        plan = self.repository.find(request.number("id"))
        self.plan_testing.follow(plan, str(request.body.get("title", "")), request.actor)
        return Response.json(self.outline.build(plan))

    def testing_templates(self, request: Request) -> Response:
        return Response.json([{"title": template.title, "brief": template.brief} for template in self.plan_testing.templates_offered()])

    def abandon(self, request: Request) -> Response:
        plan = self.repository.find(request.number("id"))
        self.repository.cancel(plan, request.actor)
        return self.answered(self.repository.find(plan.row_id))

    def moved(self, request: Request, move) -> Response:
        return self.answered(self.repository.save(move(self.repository.find(request.number("id"))), request.actor))

    def answered(self, plan: Plan) -> Response:
        return Response.json(ModelFields.build(plan))
