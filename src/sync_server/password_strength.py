import re

from sync_server.refusal import Refusal

MINIMUM_CHARACTERS = 12
PASSPHRASE_CHARACTERS = 20
KINDS_NEEDED = 3
CHARACTER_KINDS = {"lower case": re.compile(r"[a-z]"), "upper case": re.compile(r"[A-Z]"), "digits": re.compile(r"[0-9]"), "symbols": re.compile(r"[^A-Za-z0-9]")}
SHORTEST_NAME = 3


class PasswordStrength:
    """Whether a new password is strong enough: a passphrase of 20 characters or more, or 12 or more mixing three of lower case, upper case, digits and symbols; in neither case holding the name of its email."""

    @staticmethod
    def check(password: str, email: str) -> None:
        name = email.split("@")[0].lower()
        if len(name) >= SHORTEST_NAME and name in password.lower():
            raise Refusal("a password never holds the name of its email")
        if len(password) >= PASSPHRASE_CHARACTERS:
            return
        if len(password) < MINIMUM_CHARACTERS:
            raise Refusal(f"a password has at least {MINIMUM_CHARACTERS} characters mixing three of lower case, upper case, digits and symbols, or is a passphrase of {PASSPHRASE_CHARACTERS} characters or more")
        missing = [kind for kind, pattern in CHARACTER_KINDS.items() if not pattern.search(password)]
        if len(CHARACTER_KINDS) - len(missing) < KINDS_NEEDED:
            raise Refusal(f"a password of fewer than {PASSPHRASE_CHARACTERS} characters mixes three of lower case, upper case, digits and symbols; this one has no {' and no '.join(missing)}")
