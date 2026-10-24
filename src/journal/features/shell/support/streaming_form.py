DEFAULT_ADVICE = "make the command print its steps as it goes, run it unbuffered (python -u), or give its reader a --progress pattern and a --label"
# the form of a tool that prints each step as it happens, by the bare command a run is known by
FORMS = {
    "go test": "run go test -json or -v, which print each test as it ends, not each package",
    "pytest": "run pytest without -q or -qq, so it prints its progress percentage, and read it with --progress '\\[\\s*(\\d+)%\\]'",
    "vitest run": "run vitest with --reporter=verbose, which prints each test as it ends",
    "jest": "run jest with --verbose, which prints each test as it ends",
    "cargo test": "run cargo test with -- --nocapture --test-threads=1, which prints each test as it runs",
    "phpunit": "run phpunit with --testdox, which prints each test as it ends",
    "dotnet test": "run dotnet test with --logger 'console;verbosity=normal', which prints each test as it ends",
}


class StreamingForm:
    """How to make a quiet command print as it runs: the streaming form of a tool the journal knows, by its bare command, or the general advice."""

    @staticmethod
    def advice(command: str) -> str:
        program = command.split()[0] if command else ""
        return FORMS.get(command) or FORMS.get(program) or ("run it unbuffered with python -u" if program.endswith(".py") else DEFAULT_ADVICE)
