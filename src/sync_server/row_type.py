FORMER_TYPE_KEY = "kind"


class RowType:
    """A row's type as a journal sends it, under its table's name for it, as link_type, or under kind, the name a row sent before the rename has."""

    @staticmethod
    def of(fields: dict, name: str, default: str = "") -> str:
        return fields.get(name, fields.get(FORMER_TYPE_KEY, default))
