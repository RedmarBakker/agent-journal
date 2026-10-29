from journal.features.organization.support.contract_problem import ContractProblem


class TomlFields:
    """The keys of one parsed contract file, read by type; every missing key, wrong type or unknown key is a problem on the file, all of them, so the author fixes the file once."""

    def __init__(self, path: str, data: dict) -> None:
        self.path, self.data, self.problems = path, data, []

    def problem(self, rule: str, message: str) -> None:
        self.problems.append(ContractProblem(self.path, rule, message))

    def unknown(self, allowed: tuple[str, ...]) -> None:
        for key in self.data:
            if key not in allowed:
                self.problem("schema", f"{key} is not a key of this file; remove it")

    def text(self, key: str) -> str:
        value = self.data.get(key)
        if not isinstance(value, str) or not value.strip():
            self.problem("schema", f"{key} must be a text that is not empty")
            return ""
        return value

    def flag(self, key: str) -> bool:
        value = self.data.get(key)
        if not isinstance(value, bool):
            self.problem("schema", f"{key} must be true or false")
            return False
        return value

    def texts(self, key: str) -> tuple[str, ...]:
        values = self.listed(key)
        if not values:
            self.problem("schema", f"{key} must list at least one entry")
        return values

    def listed(self, key: str) -> tuple[str, ...]:
        value = self.data.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
            self.problem("schema", f"{key} must be a list of texts")
            return ()
        return tuple(value)

    def table(self, key: str) -> "TomlFields":
        value = self.data.get(key)
        if not isinstance(value, dict):
            self.problem("schema", f"{key} must be a table")
            value = {}
        return TomlFields(self.path, value)

    def tables(self, key: str) -> list["TomlFields"]:
        value = self.data.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            self.problem("schema", f"{key} must be a list of tables")
            return []
        return [TomlFields(self.path, item) for item in value]

    def absorbed(self, other: "TomlFields") -> None:
        self.problems += other.problems
