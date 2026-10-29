from journal.models.template import TESTING, Template
from journal.models.template_schedule import TemplateSchedule
from journal.repositories.repository import Repository


class Templates(Repository[Template]):
    model = Template

    def testing(self, target: str) -> list[Template]:
        return [template for template in self.matching(purpose=TESTING) if target in template.targets]

    def testing_titled(self, title: str, target: str) -> list[Template]:
        return [template for template in self.testing(target) if template.title == title]

    def scheduled(self) -> list[Template]:
        return self.selected(self.query().filter_listed("schedule", [schedule for schedule in TemplateSchedule if schedule != TemplateSchedule.NONE]).order("id"))
