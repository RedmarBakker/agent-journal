from collections.abc import Sequence

from journal.db.query import Query
from journal.models.link import Link
from journal.support.actor import Actor
from journal.models.model import Model
from journal.models.support.ref import Ref
from journal.repositories.repository import Repository

# refs read in one query, each named twice, under SQLite's limit of values in one statement
REF_CHUNK = 10_000


class Links(Repository[Link]):
    model = Link

    def link_rows(self, model: Model) -> list[Link]:
        return self.selected(self.touching(model).order("id"))

    def of_kind(self, kind: str) -> list[Link]:
        return self.selected(self.query().filter(kind=kind).order("id"))

    def unlisted_kind_links(self, kind: str) -> list[Link]:
        with self.connection.unlisted():
            return self.of_kind(kind)

    def targets(self, model: Model, kind: str) -> list[Ref]:
        return [link.target for link in self.selected(self.query().filter(source=Ref.build(model), kind=kind).order("id"))]

    def all_targets(self, model: Model) -> list[Ref]:
        return [link.target for link in self.selected(self.query().filter(source=Ref.build(model)).order("id"))]

    def all_sources(self, model: Model) -> list[Ref]:
        return [link.source for link in self.selected(self.query().filter(target=Ref.build(model)).order("id"))]

    def model_links(self, column: str, models: Sequence[Model], kind: str) -> list[Link]:
        return self.ref_links(column, [Ref.build(model) for model in models], kind)

    def ref_links(self, column: str, refs: Sequence[Ref], kind: str) -> list[Link]:
        if not refs:
            return []
        return self.selected(self.query().filter_listed(column, list(refs)).filter(kind=kind).order("id"))

    def ref_count(self, column: str, refs: Sequence[Ref], kind: str, source_table: str) -> int:
        if not refs:
            return 0
        return sum(self.grouped_counts(self.query().filter_listed(column, list(refs)).filter(kind=kind).filter_prefix("source", f"{source_table}:"), "kind").values())

    def target_counts(self, models: Sequence[Model], kind: str) -> dict[int, int]:
        if not models:
            return {}
        counted = self.grouped_counts(self.query().filter_listed("target", [Ref.build(model) for model in models]).filter(kind=kind), "target")
        return {Ref.parse(ref).id: total for ref, total in counted.items()}

    def targets_except(self, model: Model, kind: str, refs: set[Ref]) -> list[Ref]:
        return [ref for ref in self.targets(model, kind) if ref not in refs]

    def typed_targets(self, model: Model, kind: str, table: str) -> list[Ref]:
        return [link.target for link in self.selected(self.query().filter(source=Ref.build(model), kind=kind).filter_prefix("target", f"{table}:").order("id"))]

    def typed_sources(self, model: Model, kind: str, table: str) -> list[Ref]:
        return [ref for ref in self.sources(model, kind) if ref.type == table]

    def source_links(self, model: Model, kind: str) -> list[Link]:
        return self.selected(self.query().filter(source=Ref.build(model), kind=kind).order("id"))

    def sources(self, model: Model, kind: str) -> list[Ref]:
        return self.ref_sources(Ref.build(model), kind)

    def ref_sources(self, target: Ref, kind: str) -> list[Ref]:
        return [link.source for link in self.selected(self.query().filter(target=target, kind=kind).order("id"))]

    def sources_except(self, model: Model, kind: str, refs: Sequence[Ref]) -> list[Ref]:
        if not refs:
            return self.sources(model, kind)
        return [link.source for link in self.selected(self.query().filter(target=Ref.build(model), kind=kind).filter_unlisted("source", list(refs)).order("id"))]

    def linked(self, source: Ref, target: Ref, kind: str, actor: Actor) -> Link:
        with self.writing():
            existing = self.matching(source=source, target=target, kind=kind)
            return existing[0] if existing else self.save(Link(source=source, target=target, kind=kind), actor)

    def connecting(self, source: Model, target: Model) -> list[Link]:
        return self.matching(source=Ref.build(source), target=Ref.build(target))

    def remove_links(self, model: Model, actor: Actor) -> None:
        ref = Ref.build(model)
        self.purged_rows(Link, self.query().filter(source=ref).filter_unlisted("kind", list(Link.SURVIVING_SOURCE)), actor)
        self.purged_rows(Link, self.query().filter(target=ref).filter_unlisted("kind", list(Link.SURVIVING_TARGET)), actor)

    def touching_any(self, models: Sequence[Model]) -> list[Link]:
        refs = [Ref.build(model) for model in models]
        chunks = [refs[start:start + REF_CHUNK] for start in range(0, len(refs), REF_CHUNK)]
        return list({link.id: link for chunk in chunks for link in self.selected(self.query().filter_alternatives(self.query().filter_listed("source", chunk), self.query().filter_listed("target", chunk)))}.values())

    def touching(self, model: Model) -> Query:
        ref = Ref.build(model)
        return self.query().filter_alternatives(self.query().filter(source=ref), self.query().filter(target=ref))
