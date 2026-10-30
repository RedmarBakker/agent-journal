from journal.models.template import TESTING, Template
from journal.repositories.repository import Repository


class Templates(Repository[Template]):
    model = Template

    def testing(self, target: str) -> list[Template]:
        return [template for template in self.matching(purpose=TESTING) if target in template.targets]

    def testing_titled(self, title: str, target: str) -> list[Template]:
        return [template for template in self.testing(target) if template.title == title]

    def has_titled(self, ids: list[int], title: str) -> bool:
        return self.counted(self.query().filter_listed("id", ids).filter(title=title)) > 0
