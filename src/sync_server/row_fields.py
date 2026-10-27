FORMER_TYPE_KEY = "kind"


class RowFields:
    """A row's fields as the server reads them by name: a field, none when the row has not got it, and the row's type under its table's name for it, as link_type, or under kind, the name a row sent before the rename has."""

    fields: dict

    def field(self, name: str) -> object:
        return self.fields.get(name)

    def row_type(self, name: str, default: str = "") -> str:
        return self.fields.get(name, self.fields.get(FORMER_TYPE_KEY, default))
