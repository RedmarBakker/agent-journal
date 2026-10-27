from enum import StrEnum

from journal.support.rejection import Rejection


class SecretType(StrEnum):
    API_KEY = "api key"
    LOGIN = "login"
    BROWSER_LOGIN = "browser login"
    CUSTOM = "custom"

    @classmethod
    def lookup(cls, supplied: str) -> "SecretType":
        try:
            return cls(supplied.strip().lower())
        except ValueError as unknown:
            raise Rejection(f"a secret is one of {', '.join(type_name.value for type_name in cls)}, not {supplied!r}") from unknown

    def first_fields(self, title: str) -> tuple[dict, ...]:
        stem = "_".join("".join(c if c.isalnum() else " " for c in title).upper().split())
        names = {SecretType.API_KEY: (("key", True),), SecretType.LOGIN: (("username", False), ("password", True))}.get(self, ())
        return tuple({"name": name, "hidden": hidden, "variable": f"{stem}_{name.upper()}"} for name, hidden in names)
