from journal.features.shell.support.activity_title import TITLE_RULE

COUNTING = "count what has finished against the total and print it as N/M on each line that finishes one, such as each test against the number the run will run, as a suite run in shards counts every shard's finished tests; give the reader --progress '(\\d+)/(\\d+)' and a --label that is " + TITLE_RULE + ". A bar that counts suites or packages says little when each runs many tests: count the tests"
DEFAULT_ADVICE = f"make the command print its steps as it goes, run it unbuffered (python -u), or {COUNTING}"
# the form of a tool that prints each step as it happens, by the bare command a run is known by
FORMS = {
    "go test": "count the tests, not the packages: go test -list . <packages> prints every test's name before the run, so the lines starting Test, Example or Fuzz are the total, and go test -v prints an unindented --- PASS, --- SKIP or --- FAIL line as each test ends (subtests are indented and not counted); number those lines N/M tests and give the reader --progress '(\\d+)/(\\d+) tests', its pattern on the FAIL and panic lines so the PASS lines stay out of the card",
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
