from journal.features.migration.support.project_type import ProjectType
from journal.features.migration.support.version_3_row import Version3Row


class BuiltinType(ProjectType):
    """A project kind version 3 also shipped rows of: the ones it shipped stay behind, since version 4 ships its own."""

    def skipped(self, row: Version3Row) -> str:
        return super().skipped(row) or ("shipped with version 3" if row.data.get("system") else "")
