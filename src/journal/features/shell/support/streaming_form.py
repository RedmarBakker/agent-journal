from journal.features.shell.support.activity_title import TITLE_RULE
from journal.support.command_shape import CommandShape

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
    "vite build": "vite build prints its transformed module count (N modules transformed) at the end only: run it with --logLevel info for a line per step, and count those lines against the total",
    "webpack": "run webpack with --progress, which prints a percentage as it builds, and read it with --progress '(\\d+)%'",
    "cargo build": "cargo build prints a Compiling line per crate: count those lines against the number of crates in cargo metadata --format-version 1 (its packages list) and print N/M as each one starts",
    "go build": "run go build with -v, which prints a line per package as it compiles; count those lines against go list -deps . and print N/M",
    "dotnet build": "run dotnet build with -v n, which prints a line per project as it builds, and count them against the projects in the solution",
    "gradle": "run gradle with --console=plain, which prints a line per task as it runs, and count those lines against the tasks of gradle <task> --dry-run",
    "npm run build": "npm run build runs whatever tool its package.json build script names: read that script, and give that tool the form it takes (vite --logLevel info, webpack --progress, tsc --listFiles) so it prints a line per step; " + DEFAULT_ADVICE,
    "dotnet test": "run dotnet test with --logger 'console;verbosity=normal', which prints each test as it ends",
}


class StreamingForm:
    """How to make a quiet command print as it runs: the streaming form of a tool the journal knows, by its bare command, or the general advice."""

    @staticmethod
    def advice(command: str) -> str:
        name = CommandShape.command_name(command)
        program = name.split()[0] if name else ""
        return FORMS.get(name) or FORMS.get(program) or ("run it unbuffered with python -u" if program.endswith(".py") else DEFAULT_ADVICE)
