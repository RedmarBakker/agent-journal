import re
import shlex

# programs that only start the command after them, with their own flags first: sudo apt-get install is apt-get install
PREFIX_PROGRAMS = frozenset({"sudo", "xvfb-run", "npx", "pnpx", "bunx"})
# a program and its subcommand that start the command after them: bundle exec rspec is rspec
PREFIX_SUBCOMMANDS = frozenset({("bundle", "exec"), ("uv", "run"), ("poetry", "run"), ("pipenv", "run"), ("pnpm", "exec"), ("pnpm", "dlx"), ("yarn", "dlx")})
# the flags of a wrapper that take the word after them as their value
VALUED_FLAGS = frozenset({"-u", "-g", "-n", "-s", "-w", "-v", "-e", "-p", "--name", "--user", "--workdir", "--volume", "--env", "--env-file", "--network", "--entrypoint", "--publish", "--package", "-c", "--container", "--namespace", "--project-name", "-f", "--file", "--mount", "--label", "--platform", "--prefix"})
# a value with a unit, as timeout 300 or timeout 5m takes
DURATION = re.compile(r"^\d+(\.\d+)?[smhd]?$")
# a variable set for the one command after it, as CI=true npm test
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=(?![^\s]*(\$\(|`))")
# the first word of a command: a program, never a group, a brace or a continuation
PROGRAM = re.compile(r"^[\w./~-]")
# the shell's own punctuation, written back as it is
OPERATORS = frozenset({"|", "||", "&&", ";", "&", ">", ">>", "<", ">&", "<&", "(", ")", "2>&1"})


class CommandWrappers:
    """The command a wrapper runs, which a line is named for: sudo, time and timeout, npx and bundle exec, nix develop -c, and a container's command through docker run, docker compose run or exec, and kubectl exec."""

    @classmethod
    def inner(cls, part: str) -> str:
        lexer = shlex.shlex(part, posix=True, punctuation_chars="|&;<>")
        lexer.whitespace_split = True
        try:
            tokens = list(lexer)
        except ValueError:
            return part
        command = cls.wrapped(tokens)
        if not command or not PROGRAM.match(command[0]):
            return part
        return " ".join(map(cls.shell_word, command))

    @staticmethod
    def shell_word(token: str) -> str:
        return token if token in OPERATORS else shlex.quote(token)

    @classmethod
    def wrapped(cls, tokens: list[str]) -> list[str] | None:
        if not tokens:
            return None
        if ASSIGNMENT.match(tokens[0]):
            return cls.past_flags(tokens)
        program = tokens[0].rsplit("/", 1)[-1]
        if program in PREFIX_PROGRAMS:
            return cls.past_flags(tokens[1:])
        if program == "timeout":
            command = cls.past_flags(tokens[1:])
            return command[1:] if command and DURATION.match(command[0]) else command
        if len(tokens) > 1 and (program, tokens[1]) in PREFIX_SUBCOMMANDS:
            return cls.past_flags(tokens[2:])
        if program == "nix" and tokens[1:2] == ["develop"]:
            return next((tokens[index + 1:] for index, token in enumerate(tokens) if token in ("-c", "--command")), None)
        if program == "docker":
            return cls.container_command(tokens[1:])
        if program == "kubectl" and tokens[1:2] == ["exec"] and "--" in tokens:
            return cls.unshelled(tokens[tokens.index("--") + 1:])
        return None

    @classmethod
    def container_command(cls, tokens: list[str]) -> list[str] | None:
        arguments = tokens[1:] if tokens[:1] == ["compose"] else tokens
        if arguments[:1] not in (["run"], ["exec"]):
            return None
        command = cls.past_flags(arguments[1:])
        return cls.unshelled(command[1:]) if len(command) > 1 else None

    @staticmethod
    def unshelled(tokens: list[str]) -> list[str] | None:
        if len(tokens) < 3 or tokens[0].rsplit("/", 1)[-1] not in ("sh", "bash", "zsh") or tokens[1] != "-c":
            return tokens
        if ";" in tokens[2]:
            return None
        return shlex.split(tokens[2].split("&&")[-1].strip()) or None

    @staticmethod
    def past_flags(tokens: list[str]) -> list[str]:
        index = 0
        while index < len(tokens) and (tokens[index].startswith("-") or "=" in tokens[index] and not tokens[index].startswith("'")):
            index += 2 if tokens[index] in VALUED_FLAGS else 1
        return tokens[index:]
