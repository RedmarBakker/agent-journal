from datetime import datetime, timezone

from journal.engine.job import Job
from journal.features.plans.support.approved_plan_start import ApprovedPlanStart
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.template import Template
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.templates import Templates
from journal.support.actor import Actor

MADE_FROM_LINK = "made_from"


class TemplatePlanStart(Job):
    """Every minute, each plan template on a schedule whose day, week, month or quarter has turned since its last plan, or since it was scheduled, makes a plan from it in the project's own environment: its title and the date, its brief, its parts as tasks or its brief as the one task, approved and started once no other plan runs."""

    interval_seconds = 60.0

    def __init__(self, templates: Templates, plans: Plans, tasks: Tasks, links: Links, environments: Environments, scope: Scope, start: ApprovedPlanStart) -> None:
        self.templates, self.plans, self.tasks, self.links = templates, plans, tasks, links
        self.environments, self.scope, self.start = environments, scope, start

    def tick(self, time: float) -> None:
        now = datetime.fromtimestamp(time, timezone.utc)
        for template in self.templates.scheduled():
            if template.schedule.is_due(self.last_start(template), now):
                self.started(template, now)

    def last_start(self, template: Template) -> datetime:
        made = self.links.typed_source_links(template, MADE_FROM_LINK, Plan.table())
        return made[-1].creation_time if made else template.update_time

    def started(self, template: Template, now: datetime) -> None:
        environment_id = self.environments.working()[0].row_id
        with self.scope.environment(environment_id):
            plan = self.plans.save(Plan(environment_id=environment_id, title=f"{template.title} {now.astimezone():%Y-%m-%d}", brief=template.brief), Actor.system())
            self.links.save(Link(source=Ref.build(plan), target=Ref.build(template), link_type=MADE_FROM_LINK), Actor.system())
            for part in template.parts or (f"{template.title}: {template.brief}",):
                self.task(plan, part)
            self.plans.agent_approved(plan, Actor.system())
            self.start.run()

    def task(self, plan: Plan, part: str) -> None:
        title, _, brief = part.partition(":")
        task = self.tasks.save(Task(environment_id=plan.environment_id, title=title.strip(), brief=brief.strip()), Actor.system())
        self.links.save(Link(source=Ref.build(task), target=Ref.build(plan), link_type=PLAN_LINK), Actor.system())
